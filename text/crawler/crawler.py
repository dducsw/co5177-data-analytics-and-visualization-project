import argparse
import hashlib
import os
import re
import sys
import threading
import time
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

# Handle Windows terminal encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_URL = "https://vneconomy.vn"
SITEMAP_INDEX_URL = f"{BASE_URL}/sitemap.xml"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ---------------------------------------------------------------------------
# 5 chuyên mục chính xác theo cấu trúc VnEconomy
# Chỉ nhận bài khi article:section khớp đúng 1 trong 5 tên này
# ---------------------------------------------------------------------------
TARGET_CATEGORIES: Set[str] = {
    "Chứng khoán",
    "Tài chính",
    "Bất động sản",
    "Thế giới",
    "Thị trường",
}

thread_local = threading.local()


def get_session() -> requests.Session:
    """Get or create thread-local requests session with connection pool and retry."""
    if not hasattr(thread_local, "session"):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=retry_strategy,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(HEADERS)
        thread_local.session = session
    return thread_local.session


def get_md5_hash(text: str) -> str:
    """Generate MD5 hash for deduplication."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def normalize_title_hash(title: str) -> str:
    """Normalize title and compute hash to catch near-duplicate syndicated articles."""
    cleaned = re.sub(r"\W+", "", title.lower())
    return hashlib.md5(cleaned.encode("utf-8")).hexdigest()


def parse_datetime_iso(date_str: str) -> Tuple[str, str]:
    """Parse Vietnamese date string to standard ISO datetime and year-month string."""
    if not date_str:
        return "", ""
    date_str = date_str.strip()
    m = re.search(r"(\d{1,2}):(\d{2}),?\s+(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m:
        hh, mm, d, mth, y = m.groups()
        dt = datetime(int(y), int(mth), int(d), int(hh), int(mm))
        return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.strftime("%Y-%m")

    m2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m2:
        d, mth, y = m2.groups()
        dt = datetime(int(y), int(mth), int(d))
        return dt.strftime("%Y-%m-%d 00:00:00"), dt.strftime("%Y-%m")

    return date_str, ""


def get_monthly_sitemap_urls(session: Optional[requests.Session] = None) -> List[str]:
    """Fetch all monthly news sitemaps from sitemap index."""
    s = session or get_session()
    response = s.get(SITEMAP_INDEX_URL, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    sitemap_urls = []
    for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and "/sitemap/news-" in loc.text:
            sitemap_urls.append(loc.text.strip())
    return sitemap_urls


def get_article_urls_from_sitemap(
    sitemap_url: str, session: Optional[requests.Session] = None
) -> List[str]:
    """Extract valid article URLs from monthly sitemap."""
    s = session or get_session()
    response = s.get(sitemap_url, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    article_urls = []
    for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and loc.text and loc.text.endswith(".htm"):
            article_urls.append(loc.text.strip())
    return article_urls


def parse_article(url: str, session: Optional[requests.Session] = None) -> Optional[Dict[str, str]]:
    """Parse article metadata, clean content, and return structured sample."""
    try:
        s = session or get_session()
        response = s.get(url, timeout=8)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Category extraction & validation
        meta_section = soup.find("meta", property="article:section")
        raw_category = (
            meta_section["content"].strip()
            if meta_section and meta_section.get("content")
            else ""
        )

        # Chỉ nhận bài thuộc đúng 1 trong 5 chuyên mục chính của VnEconomy
        if raw_category not in TARGET_CATEGORIES:
            return None
        category = raw_category

        # 2. Title extraction (OG title -> H1 article title)
        meta_title = soup.find("meta", property="og:title")
        title = (
            meta_title["content"].strip()
            if meta_title and meta_title.get("content")
            else ""
        )
        if not title:
            h1 = soup.select_one(
                "h1.article-header__title, h1.article-title, .article-title"
            )
            title = h1.get_text(strip=True) if h1 else ""
        if not title:
            return None

        # 3. Summary (Sapo)
        meta_desc = soup.find("meta", property="og:description")
        summary = (
            meta_desc["content"].strip()
            if meta_desc and meta_desc.get("content")
            else ""
        )
        if not summary:
            sapo_elem = soup.select_one("h4.article-content__lead, .detail-sapo")
            summary = sapo_elem.get_text(strip=True) if sapo_elem else ""

        # 4. Article Body Content
        editor = soup.select_one(".article-editor") or soup.select_one(".ct-edtior-web")
        if not editor:
            return None

        # Remove boilerplates, scripts, ads, and related article links
        unwanted_selectors = [
            "script",
            "style",
            "figure",
            "iframe",
            ".article-related",
            ".box-related",
            ".box_relate",
            ".relate-news",
            ".tags",
            ".article-tag",
            ".author-info",
            ".box-author",
            ".source",
            ".copyright",
            ".share-header",
        ]
        for tag in editor.find_all(unwanted_selectors):
            tag.decompose()

        paragraphs = [
            p.get_text(strip=True)
            for p in editor.find_all("p")
            if p.get_text(strip=True)
        ]
        content = "\n".join(paragraphs)

        # Minimum content filter: at least 100 words
        word_count = len(content.split())
        if word_count < 100:
            return None

        # 5. Publish Date & Datetime Standardization
        time_elem = soup.find("time", class_="article-meta__time") or soup.find("time")
        raw_published_date = time_elem.get_text(strip=True) if time_elem else ""
        published_date, published_year_month = parse_datetime_iso(raw_published_date)

        # 6. Author
        meta_author = soup.find("meta", property="article:author")
        author = (
            meta_author["content"].strip()
            if meta_author and meta_author.get("content")
            else ""
        )
        if not author:
            author_elem = soup.find("span", class_="article-meta__author")
            author = author_elem.get_text(strip=True) if author_elem else ""

        return {
            "id": get_md5_hash(url),
            "url": url,
            "title": title,
            "summary": summary,
            "content": content,
            "word_count": str(word_count),
            "raw_category": raw_category,
            "category": category,
            "published_date": published_date,
            "published_year_month": published_year_month,
            "author": author,
        }
    except Exception:
        return None


def crawl_vneconomy(
    target_per_category: int = 500,
    max_total: int = 2500,
    max_per_month_category: int = 60,
    max_workers: int = 10,
    output_dir: str = "data",
) -> pd.DataFrame:
    """Crawl VnEconomy articles with concurrent workers, class balancing, and deduplication."""
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)
    csv_path = os.path.join(abs_output_dir, "vneconomy_articles.csv")
    jsonl_path = os.path.join(abs_output_dir, "vneconomy_articles.jsonl")

    existing_articles: List[Dict[str, str]] = []
    crawled_urls: Set[str] = set()
    seen_title_hashes: Set[str] = set()
    category_counts: Counter = Counter()
    month_cat_counts: Counter = Counter()

    # Load checkpoint if exists
    if os.path.exists(csv_path):
        try:
            df_existing = pd.read_csv(csv_path)
            existing_articles = df_existing.to_dict("records")
            crawled_urls = set(df_existing["url"].dropna())
            for art in existing_articles:
                t = str(art.get("title", ""))
                if t:
                    seen_title_hashes.add(normalize_title_hash(t))
                c = art.get("category")
                ym = art.get("published_year_month")
                if c:
                    category_counts[c] += 1
                if c and ym:
                    month_cat_counts[(ym, c)] += 1

            print(f"Loaded {len(existing_articles)} existing records from {csv_path}")
            print(f"Current distribution: {dict(category_counts)}")
        except Exception as e:
            print(f"Warning: Could not read existing checkpoint: {e}")

    # Check if target already reached for all 5 categories
    if all(category_counts[c] >= target_per_category for c in TARGET_CATEGORIES):
        print(f"Target already reached for all 5 categories ({len(existing_articles)} articles).")
        return pd.DataFrame(existing_articles)

    session = get_session()
    sitemaps = get_monthly_sitemap_urls(session)
    print(f"Found {len(sitemaps)} monthly news sitemaps.")

    collected_articles = list(existing_articles)
    lock = threading.Lock()
    last_save_time = time.time()

    def save_checkpoint(force: bool = False):
        nonlocal last_save_time
        now = time.time()
        if force or (now - last_save_time > 15):
            with lock:
                df_curr = pd.DataFrame(collected_articles)
                df_curr.to_csv(csv_path, index=False, encoding="utf-8-sig")
                df_curr.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)
                last_save_time = now

    pbar = tqdm(
        total=max_total,
        initial=len(collected_articles),
        desc="Total Crawled",
        unit="articles",
    )

    for sitemap_idx, sitemap_url in enumerate(sitemaps):
        all_met = all(category_counts[cat] >= target_per_category for cat in TARGET_CATEGORIES)
        if all_met or len(collected_articles) >= max_total:
            print("\nTarget quota reached for all 5 categories!")
            break

        ym_match = re.search(r"news-(\d{4}-\d{2})", sitemap_url)
        current_ym = ym_match.group(1) if ym_match else ""

        try:
            article_urls = get_article_urls_from_sitemap(sitemap_url, session)
        except Exception as e:
            print(f"\nError loading sitemap {sitemap_url}: {e}")
            continue

        # Filter out already seen URLs before dispatching
        urls_to_crawl = [u for u in article_urls if u not in crawled_urls]
        if not urls_to_crawl:
            continue

        print(f"\n[Sitemap {current_ym}] Dispatching {len(urls_to_crawl)} URLs with {max_workers} threads...")

        def worker_fetch(u: str) -> Optional[Dict[str, str]]:
            return parse_article(u)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(worker_fetch, u): u for u in urls_to_crawl}

            for future in as_completed(future_to_url):
                u = future_to_url[future]
                with lock:
                    crawled_urls.add(u)

                # Early check: if all categories reached
                if all(category_counts[cat] >= target_per_category for cat in TARGET_CATEGORIES):
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                try:
                    article = future.result()
                except Exception:
                    article = None

                if not article:
                    continue

                cat = article["category"]

                with lock:
                    if category_counts[cat] >= target_per_category:
                        continue

                    ym = article.get("published_year_month") or current_ym
                    # Only enforce month cap if we are still early in sitemaps; relax if later to ensure 500
                    if max_per_month_category > 0 and sitemap_idx < 10:
                        if month_cat_counts[(ym, cat)] >= max_per_month_category:
                            continue

                    t_hash = normalize_title_hash(article["title"])
                    if t_hash in seen_title_hashes:
                        continue

                    seen_title_hashes.add(t_hash)
                    collected_articles.append(article)
                    category_counts[cat] += 1
                    month_cat_counts[(ym, cat)] += 1
                    pbar.update(1)

                save_checkpoint(force=False)

        save_checkpoint(force=True)
        print(f"Status after {current_ym}: {dict(category_counts)}")

    pbar.close()
    save_checkpoint(force=True)

    df_final = pd.DataFrame(collected_articles)
    df_final.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df_final.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)

    print("\n================ Crawling Completed ================")
    print(f"Total articles collected: {len(df_final)}")
    print(f"Category distribution:\n{pd.Series(category_counts)}")
    print(f"Saved to:\n  - {csv_path}\n  - {jsonl_path}")

    return df_final


def main():
    parser = argparse.ArgumentParser(
        description="VnEconomy Text Crawler for 5 Major Categories"
    )
    parser.add_argument(
        "--target-per-category",
        type=int,
        default=500,
        help="Target number of articles per category (default: 500)",
    )
    parser.add_argument(
        "--max-total",
        type=int,
        default=2500,
        help="Maximum total articles to collect (default: 2500)",
    )
    parser.add_argument(
        "--max-per-month-category",
        type=int,
        default=60,
        help="Max articles per category per month (default: 60, 0 to disable)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent worker threads (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory to store crawled data (default: data)",
    )

    args = parser.parse_args()

    crawl_vneconomy(
        target_per_category=args.target_per_category,
        max_total=args.max_total,
        max_per_month_category=args.max_per_month_category,
        max_workers=args.workers,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

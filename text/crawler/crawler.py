import argparse
import hashlib
import math
import os
import random
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
from tqdm import tqdm
from urllib3.util.retry import Retry

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
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def normalize_title_hash(title: str) -> str:
    cleaned = re.sub(r"\W+", "", title.lower())
    return hashlib.md5(cleaned.encode("utf-8")).hexdigest()


def extract_series_prefix(title: str) -> str:
    """Extract recurring series prefix before ':' (e.g., 'Blog chứng khoán') if present."""
    m = re.match(r"^([^:]{3,30}):", title.strip())
    return m.group(1).strip().lower() if m else ""


def parse_datetime_iso(date_str: str) -> Tuple[str, str]:
    """Parse ISO or Vietnamese date string to (YYYY-MM-DD HH:MM:SS, YYYY-MM)."""
    if not date_str:
        return "", ""
    date_str = date_str.strip()

    # 1. ISO format from meta tag (e.g., 2026-08-15T14:30:00+07:00)
    iso_m = re.match(r"^(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}(?::\d{2})?)", date_str)
    if iso_m:
        d_part, t_part = iso_m.groups()
        if len(t_part) == 5:
            t_part += ":00"
        try:
            dt = datetime.strptime(f"{d_part} {t_part}", "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.strftime("%Y-%m")
        except ValueError:
            pass

    # 2. Vietnamese format: HH:MM, DD/MM/YYYY
    m = re.search(r"(\d{1,2}):(\d{2}),?\s+(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m:
        hh, mm, d, mth, y = m.groups()
        dt = datetime(int(y), int(mth), int(d), int(hh), int(mm))
        return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.strftime("%Y-%m")

    # 3. Date only: DD/MM/YYYY
    m2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m2:
        d, mth, y = m2.groups()
        dt = datetime(int(y), int(mth), int(d))
        return dt.strftime("%Y-%m-%d 00:00:00"), dt.strftime("%Y-%m")

    return "", ""


def get_monthly_sitemap_urls(session: Optional[requests.Session] = None) -> List[Tuple[str, str]]:
    """Fetch all monthly news sitemaps sorted newest-first as (year_month, url) tuples."""
    s = session or get_session()
    response = s.get(SITEMAP_INDEX_URL, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    sitemaps: List[Tuple[str, str]] = []
    for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and loc.text and "/sitemap/news-" in loc.text:
            url = loc.text.strip()
            ym_match = re.search(r"news-(\d{4}-\d{2})", url)
            ym = ym_match.group(1) if ym_match else ""
            sitemaps.append((ym, url))

    # Sort newest month first so slicing [:months] is deterministic
    sitemaps.sort(key=lambda x: x[0], reverse=True)
    return sitemaps


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
        if raw_category not in TARGET_CATEGORIES:
            return None

        # 2. Title extraction
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

        word_count = len(content.split())
        if word_count < 100:
            return None

        # 5. Publish Date & Datetime Standardization (Meta tag -> <time> fallback)
        meta_pub = soup.find("meta", property="article:published_time")
        raw_published_date = (
            meta_pub["content"].strip()
            if meta_pub and meta_pub.get("content")
            else ""
        )
        published_date, published_year_month = parse_datetime_iso(raw_published_date)
        if not published_date:
            time_elem = soup.find("time", class_="article-meta__time") or soup.find("time")
            raw_time = time_elem.get_text(strip=True) if time_elem else ""
            published_date, published_year_month = parse_datetime_iso(raw_time)

        if not published_date or not published_year_month:
            return None

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
            "category": raw_category,
            "published_date": published_date,
            "published_year_month": published_year_month,
            "author": author,
        }
    except Exception:
        return None


def crawl_vneconomy(
    target_per_category: int = 1000,
    months_window: int = 12,
    max_series_per_month: int = 5,
    max_workers: int = 10,
    seed: int = 42,
    output_dir: str = "data_5000",
) -> pd.DataFrame:
    """
    Crawl VnEconomy articles with uniform temporal stratification across `months_window`,
    intra-month random shuffling, month-level early stopping, and series cap.
    """
    max_total = target_per_category * len(TARGET_CATEGORIES)
    monthly_cap = math.ceil(target_per_category / max(months_window, 1))

    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)
    csv_path = os.path.join(abs_output_dir, "vneconomy_articles.csv")
    jsonl_path = os.path.join(abs_output_dir, "vneconomy_articles.jsonl")

    existing_articles: List[Dict[str, str]] = []
    crawled_urls: Set[str] = set()
    seen_title_hashes: Set[str] = set()
    category_counts: Counter = Counter()
    month_cat_counts: Counter = Counter()
    month_series_counts: Counter = Counter()

    if os.path.exists(csv_path):
        try:
            df_existing = pd.read_csv(csv_path)
            existing_articles = df_existing.to_dict("records")
            crawled_urls = set(df_existing["url"].dropna())
            for art in existing_articles:
                t = str(art.get("title", ""))
                c = art.get("category")
                ym = art.get("published_year_month")
                if t:
                    seen_title_hashes.add(normalize_title_hash(t))
                    pref = extract_series_prefix(t)
                    if pref and ym:
                        month_series_counts[(ym, pref)] += 1
                if c:
                    category_counts[c] += 1
                if c and ym:
                    month_cat_counts[(ym, c)] += 1

            print(f"Loaded {len(existing_articles)} existing records from {csv_path}")
            print(f"Current distribution: {dict(category_counts)}")
        except Exception as e:
            print(f"Warning: Could not read existing checkpoint: {e}")

    if all(category_counts[c] >= target_per_category for c in TARGET_CATEGORIES):
        print(f"Target already reached for all 5 categories ({len(existing_articles)} articles).")
        return pd.DataFrame(existing_articles)

    session = get_session()
    all_sitemaps = get_monthly_sitemap_urls(session)
    # Exclude the current incomplete month if needed or take the exact window
    target_sitemaps = all_sitemaps[:months_window]
    target_months = {ym for ym, _ in target_sitemaps if ym}

    print(
        f"Temporal plan: {len(target_sitemaps)} months ({min(target_months)} -> {max(target_months)}) | "
        f"Monthly cap/category: {monthly_cap} | Series cap/month: {max_series_per_month}"
    )

    collected_articles = list(existing_articles)
    lock = threading.Lock()
    last_save_time = time.time()
    rng = random.Random(seed)

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

    def process_sitemap(current_ym: str, sitemap_url: str, enforce_month_cap: bool):
        if all(category_counts[cat] >= target_per_category for cat in TARGET_CATEGORIES):
            return

        if enforce_month_cap and current_ym:
            if all(month_cat_counts[(current_ym, cat)] >= monthly_cap for cat in TARGET_CATEGORIES):
                print(f"\n[Sitemap {current_ym}] Monthly cap already satisfied for all 5 categories. Skipping.")
                return

        try:
            article_urls = get_article_urls_from_sitemap(sitemap_url, session)
        except Exception as e:
            print(f"\nError loading sitemap {sitemap_url}: {e}")
            return

        urls_to_crawl = [u for u in article_urls if u not in crawled_urls]
        if not urls_to_crawl:
            return

        # Shuffle URLs within the month so sampled articles span days 1..31 evenly
        rng.shuffle(urls_to_crawl)
        print(f"\n[Sitemap {current_ym}] Dispatching {len(urls_to_crawl)} shuffled URLs...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(parse_article, u): u for u in urls_to_crawl}

            for future in as_completed(future_to_url):
                u = future_to_url[future]
                with lock:
                    crawled_urls.add(u)

                # Global early stop
                if all(category_counts[cat] >= target_per_category for cat in TARGET_CATEGORIES):
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                # Month-level early stop: stop fetching once all 5 categories hit monthly_cap
                if enforce_month_cap and current_ym:
                    if all(month_cat_counts[(current_ym, cat)] >= monthly_cap for cat in TARGET_CATEGORIES):
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                try:
                    article = future.result()
                except Exception:
                    article = None

                if not article:
                    continue

                cat = article["category"]
                ym = article["published_year_month"]

                # Keep strictly inside the target month window during Pass 1
                if enforce_month_cap and current_ym and ym != current_ym:
                    continue

                with lock:
                    if category_counts[cat] >= target_per_category:
                        continue

                    if enforce_month_cap and month_cat_counts[(ym, cat)] >= monthly_cap:
                        continue

                    t_hash = normalize_title_hash(article["title"])
                    if t_hash in seen_title_hashes:
                        continue

                    pref = extract_series_prefix(article["title"])
                    if pref and max_series_per_month > 0:
                        if month_series_counts[(ym, pref)] >= max_series_per_month:
                            continue
                        month_series_counts[(ym, pref)] += 1

                    seen_title_hashes.add(t_hash)
                    collected_articles.append(article)
                    category_counts[cat] += 1
                    month_cat_counts[(ym, cat)] += 1
                    pbar.update(1)

                save_checkpoint(force=False)

        save_checkpoint(force=True)
        print(f"Status after {current_ym}: {dict(category_counts)}")

    # Pass 1: Strict uniform stratification across the target months window
    for ym, s_url in target_sitemaps:
        process_sitemap(ym, s_url, enforce_month_cap=True)

    # Pass 2 (Fallback): Top up any category still below target_per_category from remaining sitemaps
    if any(category_counts[c] < target_per_category for c in TARGET_CATEGORIES):
        print("\nRunning fallback pass to top up remaining category quotas...")
        for ym, s_url in all_sitemaps[months_window:]:
            if all(category_counts[c] >= target_per_category for c in TARGET_CATEGORIES):
                break
            process_sitemap(ym, s_url, enforce_month_cap=False)

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
        description="VnEconomy Text Crawler with Uniform Temporal Stratification"
    )
    parser.add_argument(
        "--target-per-category",
        type=int,
        default=1000,
        help="Target number of articles per category (default: 1000)",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=12,
        help="Number of recent monthly sitemaps to stratify uniformly across (default: 12)",
    )
    parser.add_argument(
        "--max-series-per-month",
        type=int,
        default=5,
        help="Max articles per recurring title prefix per month (default: 5, 0 to disable)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent worker threads (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for shuffling URLs within each month (default: 42)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data_5000",
        help="Directory to store crawled data (default: data_5000)",
    )

    args = parser.parse_args()

    crawl_vneconomy(
        target_per_category=args.target_per_category,
        months_window=args.months,
        max_series_per_month=args.max_series_per_month,
        max_workers=args.workers,
        seed=args.seed,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
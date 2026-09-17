import argparse
import hashlib
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
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
# 5 chuyên mục cha chính xác theo cấu trúc VnEconomy
# Chỉ nhận bài khi article:section khớp đúng 1 trong 5 tên này
# ---------------------------------------------------------------------------
TARGET_CATEGORIES: Set[str] = {
    "Chứng khoán",
    "Tài chính",
    "Bất động sản",
    "Thế giới",
    "Thị trường",
}


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




def get_monthly_sitemap_urls(session: requests.Session) -> List[str]:
    """Fetch all monthly news sitemaps from sitemap index."""
    response = session.get(SITEMAP_INDEX_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    sitemap_urls = []
    for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and "/sitemap/news-" in loc.text:
            sitemap_urls.append(loc.text.strip())
    return sitemap_urls


def get_article_urls_from_sitemap(sitemap_url: str, session: requests.Session) -> List[str]:
    """Extract valid article URLs from monthly sitemap."""
    response = session.get(sitemap_url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    article_urls = []
    for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and loc.text and loc.text.endswith(".htm"):
            article_urls.append(loc.text.strip())
    return article_urls


def parse_article(url: str, session: requests.Session) -> Optional[Dict[str, str]]:
    """Parse article metadata, clean content, and return structured sample."""
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Category extraction & validation
        meta_section = soup.find("meta", property="article:section")
        raw_category = meta_section["content"].strip() if meta_section and meta_section.get("content") else ""

        # Chỉ nhận bài thuộc đúng 1 trong 5 chuyên mục cha chính của VnEconomy
        if raw_category not in TARGET_CATEGORIES:
            return None
        category = raw_category


        # 2. Title extraction (OG title -> H1 article title)
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title and meta_title.get("content") else ""
        if not title:
            h1 = soup.select_one("h1.article-header__title, h1.article-title, .article-title")
            title = h1.get_text(strip=True) if h1 else ""
        if not title:
            return None

        # 3. Summary (Sapo)
        meta_desc = soup.find("meta", property="og:description")
        summary = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
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

        paragraphs = [p.get_text(strip=True) for p in editor.find_all("p") if p.get_text(strip=True)]
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
        author = meta_author["content"].strip() if meta_author and meta_author.get("content") else ""
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
    delay: float = 0.25,
    output_dir: str = "data",
) -> pd.DataFrame:
    """Crawl VnEconomy articles with class balancing, temporal stratification, and deduplication."""
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "vneconomy_articles.csv")
    jsonl_path = os.path.join(output_dir, "vneconomy_articles.jsonl")

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

    if len(existing_articles) >= max_total:
        print(f"Target already reached ({len(existing_articles)} >= {max_total}).")
        return pd.DataFrame(existing_articles)

    session = requests.Session()
    sitemaps = get_monthly_sitemap_urls(session)
    print(f"Found {len(sitemaps)} monthly news sitemaps.")

    collected_articles = existing_articles

    for sitemap_url in sitemaps:
        if len(collected_articles) >= max_total:
            break

        all_met = all(category_counts[cat] >= target_per_category for cat in TARGET_CATEGORIES)
        if all_met:
            print("Target per category reached for all 5 categories.")
            break

        # Extract year-month from sitemap URL
        ym_match = re.search(r"news-(\d{4}-\d{2})", sitemap_url)
        current_ym = ym_match.group(1) if ym_match else ""

        try:
            article_urls = get_article_urls_from_sitemap(sitemap_url, session)
        except Exception as e:
            print(f"Error loading sitemap {sitemap_url}: {e}")
            continue

        print(f"\nProcessing sitemap: {sitemap_url} ({len(article_urls)} URLs)")

        for url in tqdm(article_urls, desc=f"Sitemap {current_ym}", unit="article"):
            if len(collected_articles) >= max_total:
                break

            if url in crawled_urls:
                continue

            crawled_urls.add(url)
            article = parse_article(url, session)

            if not article:
                continue

            cat = article["category"]

            # Check overall quota for this category
            if category_counts[cat] >= target_per_category:
                continue

            # Check temporal stratification quota per month
            ym = article.get("published_year_month") or current_ym
            if max_per_month_category > 0 and month_cat_counts[(ym, cat)] >= max_per_month_category:
                continue

            # Content deduplication by normalized title
            t_hash = normalize_title_hash(article["title"])
            if t_hash in seen_title_hashes:
                continue

            seen_title_hashes.add(t_hash)
            collected_articles.append(article)
            category_counts[cat] += 1
            month_cat_counts[(ym, cat)] += 1

            if delay > 0:
                time.sleep(delay)

            # Checkpoint save every 50 articles
            if len(collected_articles) % 50 == 0:
                df_temp = pd.DataFrame(collected_articles)
                df_temp.to_csv(csv_path, index=False, encoding="utf-8-sig")
                df_temp.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)

    df_final = pd.DataFrame(collected_articles)
    df_final.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df_final.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)

    print("\n================ Crawling Finished ================")
    print(f"Total articles collected: {len(df_final)}")
    print(f"Category distribution:\n{pd.Series(category_counts)}")
    print(f"Output saved to: {csv_path} and {jsonl_path}")

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
        help="Max articles per category per month for temporal balance (default: 60, 0 to disable)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Delay between requests in seconds (default: 0.25)",
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
        delay=args.delay,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

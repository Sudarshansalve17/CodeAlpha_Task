"""Collect quote data from the Quotes to Scrape practice website."""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


START_URL = "https://quotes.toscrape.com/"
USER_AGENT = "LearningDatasetScraper/1.0 (educational use)"
COLUMNS = ["quote", "author", "author_url", "tags", "source_url", "scraped_at_utc"]


def scrape_quotes(max_pages: int, delay: float) -> list[dict[str, str]]:
    """Fetch up to max_pages and return the quote records found."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    next_url: str | None = START_URL
    visited_urls: set[str] = set()
    records: list[dict[str, str]] = []
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    while next_url and next_url not in visited_urls and len(visited_urls) < max_pages:
        visited_urls.add(next_url)
        response = session.get(next_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.select("div.quote"):
            quote_text = item.select_one("span.text")
            author = item.select_one("small.author")
            if quote_text is None or author is None:
                continue

            # The only plain link besides the tags is the author's "(about)" page.
            author_link = item.select_one("span a[href^='/author/']")

            records.append(
                {
                    "quote": quote_text.get_text(strip=True),
                    "author": author.get_text(strip=True),
                    "author_url": urljoin(response.url, author_link["href"])
                    if author_link
                    else "",
                    "tags": ";".join(
                        tag.get_text(strip=True) for tag in item.select("a.tag")
                    ),
                    # The page the quote was actually scraped from.
                    "source_url": response.url,
                    "scraped_at_utc": collected_at,
                }
            )

        print(
            f"Page {len(visited_urls)}: found {len(soup.select('div.quote'))} quotes "
            f"at {response.url} (total: {len(records)})"
        )

        next_link = soup.select_one("li.next a[href]")
        next_url = urljoin(response.url, next_link["href"]) if next_link else None
        if next_url:
            time.sleep(delay)

    return records


def write_csv(records: list[dict[str, str]], output_path: Path) -> None:
    """Write records with a stable column order, including for empty results."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape quote, author, and tag data into a CSV dataset."
    )
    parser.add_argument("--pages", type=int, default=10, help="maximum pages to fetch")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between pages")
    parser.add_argument("--output", type=Path, default=Path("data/quotes.csv"))
    args = parser.parse_args()

    if args.pages < 1:
        parser.error("--pages must be at least 1")
    if args.delay < 0:
        parser.error("--delay cannot be negative")

    records = scrape_quotes(args.pages, args.delay)
    write_csv(records, args.output)
    print(f"Saved {len(records)} quotes to {args.output}")


if __name__ == "__main__":
    main()

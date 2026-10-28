# Quote Dataset Scraper

A small Python project that demonstrates how to collect a custom dataset from a public practice website. It uses `requests` to fetch HTML, Beautiful Soup CSS selectors to extract fields, and the site's **Next** link to navigate between pages.

## Setup

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python scraper.py --pages 3 --delay 1 --output data\quotes.csv
```

The CSV contains `quote`, `author`, `tags`, `source_url`, and `scraped_at_utc`. Change the record fields in `scrape_quotes` to shape the dataset for a particular analysis. For example, retaining tags supports topic counts, while author and quote text support author-level summaries or text analysis.

## How extraction works

- Each quote is contained in `div.quote`.
- The text and author are in `span.text` and `small.author`.
- Tags are links with the `tag` class.
- Pagination is discovered from `li.next a`, rather than assuming a fixed URL pattern.

To adapt this to another site, inspect its page source or browser developer tools, identify the corresponding elements and pagination link, then update the selectors. Sites may change their HTML, so verify a few output rows against the source page.

Use only pages you are allowed to access. Check the site's terms and robots.txt, avoid personal or sensitive data, and keep requests modest. This example waits between page requests and sets a 15-second timeout.
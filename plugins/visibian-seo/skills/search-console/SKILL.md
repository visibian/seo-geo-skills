---
name: search-console
description: Pull live Google Search Console data through its API with the user's own access, without exports, for clicks, impressions, click-through and average position by query, page, country, device or date; URL inspection (whether each page is indexed, why not, Google's chosen canonical, last crawl, robots.txt, rich result issues); and submitted sitemaps with their errors. Use when someone asks for Search Console data, Google rankings or positions, indexing status, why a page is not indexed, index coverage, crawl dates, canonical problems, sitemap errors, or wants keyword research or SEO reporting from live data instead of a CSV export.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Search Console, live

Read the site's own Google Search Console data through the API, so the other skills work from today's numbers instead of an export.

## Before starting

The user needs access to the property in Search Console and an OAuth access token for it, set in their environment as `SEARCH_CONSOLE_TOKEN`. Explain the two ways in the script's help (`python3 scripts/gsc_api.py --help`): Google's OAuth 2.0 Playground (no setup; the token lasts one hour) or gcloud. The scope is `webmasters.readonly`: the token can read, not change, anything.

Never ask the user to paste a token, key or password into the chat. If they cannot set a token, use the exports instead: the `keyword-research` skill reads the Performance export, and Search Console's own URL Inspection tool shows one page at a time.

## Steps

From this skill's folder:

1. Find the property's exact name: `python3 scripts/gsc_api.py sites`. A domain property reads `sc-domain:example.com`; a URL-prefix property is the full address with its trailing slash.
2. Performance: `python3 scripts/gsc_api.py performance sc-domain:example.com --days 90`
   writes `search-console-performance.csv` with query, page, clicks, impressions, ctr and position. Then run the `keyword-research` skill on it (`python3 gsc_queries.py search-console-performance.csv --brand "..."`), which adds the pages that compete for one query. Other cuts: `--dimensions query,country`, `--dimensions date` for a trend, `--type image` or `news` or `discover`.
3. Indexing: `python3 scripts/gsc_api.py inspect sc-domain:example.com --urls pages.txt` for the pages that matter most (the money pages, new pages, pages that lost traffic). It reports, per page, whether it is indexed and why not, Google's canonical against the page's own, the last crawl and the device it was crawled as, and rich result issues. The limit is 2,000 inspections a day for each property, so pick pages rather than inspecting a whole site.
4. Sitemaps: `python3 scripts/gsc_api.py sitemaps sc-domain:example.com` lists each submitted sitemap with its address count, errors, warnings and when Google last read it.
5. Act on what is found:
   - "Crawled, currently not indexed" or "Discovered, currently not indexed": Google chose not to index yet. Check the page's value and uniqueness, its internal links (`internal-linking`) and whether it is in the sitemap; do not resubmit in a loop.
   - Indexing blocked by a noindex tag, header or robots.txt: confirm the block is wanted; if not, remove it (`seo-audit` finds the rest of the site's blocks).
   - Google chose another canonical: make the page's canonical, internal links, sitemap entry and redirects all point to one address, or accept Google's choice if the pages are duplicates.
   - Fetch errors (not found, server error, redirect error, soft 404): fix the page or redirect it, then ask Google to recrawl it in Search Console.
   - Sitemap errors: open the sitemap address and fix what Search Console names; `seo-audit` checks the sitemap's addresses too.

## Output

- For performance: the file, its window and totals, then the `keyword-research` plan.
- For inspection: a table of pages with what to look at, the problems grouped by cause, and the fix for each cause.
- What the data cannot tell: queries Search Console leaves out for privacy, anything before its 16 months of history, and what AI assistants say about the brand.

## Ground rules

- Report Search Console's numbers as it returns them, with the window and the property. Dates are in Pacific time and the last two or three days are not final.
- The API returns the top rows, not always every row (Google, "Search Analytics: query", read 17 November 2026); say so when totals differ from the Search Console chart.
- Only read. This skill never submits, removes or changes anything in Search Console.

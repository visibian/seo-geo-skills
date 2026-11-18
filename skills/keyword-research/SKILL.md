---
name: keyword-research
description: Do keyword research and rank tracking from a site's own Google Search Console data, finding quick wins (queries ranking 4 to 20), queries with low click-through for their position, the questions searchers ask, topic clusters, search intent, branded against non-branded traffic, keyword cannibalization, and queries that declined between two periods, then map them to pages and content. Use when someone asks for keyword research, which keywords to target, SEO opportunities, rank tracking, why traffic dropped, content gaps, or what to write next, and has Search Console access or exports.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Keyword research from Search Console

Use what Google already reports about the site: the queries it shows for, how often, at what position and with what click-through. It is the user's own data, free, and closer to their buyers than any keyword list.

## Get the data

Ask the user to export it (they need access to the property in Search Console):

1. Search Console, Performance, Search results. Set the date range (the last 3 months is a good start), and for a comparison, Compare to the previous period.
2. Export, Download CSV. The download holds several tables; use `Queries.csv`. For a comparison, export each period on its own.
3. For pages that compete for the same query, the query and page together are needed: as a CSV with `query` and `page` columns from Looker Studio or the BigQuery bulk export.

With a Search Console API token set in their environment, the `search-console` skill pulls the same data live, query and page together, without an export: `python3 gsc_api.py performance sc-domain:example.com --days 90` writes a CSV this skill reads as it is.

Never ask for the user's Google password, a token or access to their account; work from files they give you or from the token they set themselves.

## Steps

1. Run, from this skill's folder:
   `python3 scripts/gsc_queries.py Queries.csv --brand "brand name,brand.com"`
   Add `--compare Queries-before.csv` for declines. It lists quick wins, low click-through against the site's own median at each position, questions, topics and intent.
2. Turn the list into a plan:
   - Quick wins: for each, find the page that ranks (search the site, or the pairs file) and improve it for that query with the `on-page-seo` skill. If no page fits, it is a new page.
   - Low click-through: rewrite the title and description to match what the query asks; check whether a rich result or an AI Overview takes the clicks.
   - Questions: answer them on the page that ranks, or gather them into the `buyer-questions` skill's list and write answer-first pages (`answer-first-content`).
   - Topics: one page per distinct need, with hub pages linking each group (`internal-linking`).
   - Competing pages: decide which page should answer, then merge, redirect or differentiate the others.
   - Declines: check whether the page changed, broke (`seo-audit`), or lost to another page or an AI answer.
3. Map every chosen query to one page in a table, so two pages never chase the same query.

## Output

- A table: query, impressions, clicks, position, intent, the page that should answer, the action.
- The five actions with the most impressions behind them, first.
- What the data cannot tell: volume for queries the site never shows for, and anything about AI answers.

## Ground rules

- Use the user's own data. Do not invent search volumes, difficulty scores or traffic forecasts.
- Search Console leaves out rare queries for privacy and rounds figures; say so when totals differ from its chart.
- Intent and topics come from the words in each query; check them before acting.
- Write for the question, not for word counts: Google's spam policies count keyword stuffing as spam (Google Search Central, "Spam policies for Google web search", updated 28 August 2026).

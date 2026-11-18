---
name: ai-traffic-readout
description: Read the real traffic AI sends to the user's site from Visibian's Ground Truth data, covering visits referred by AI assistants (from Google Analytics or the site's edge) and page fetches by AI crawlers, per day and per source, and put them next to the brand's visibility in AI answers. Use when someone asks how many visits ChatGPT, Perplexity, Gemini or Copilot send them, whether AI crawlers read their site, or whether AI visibility turns into traffic, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# AI traffic readout

Show what AI assistants send to the site and how often their crawlers read it, from the user's Visibian Ground Truth data. How to read the data: `references/reading-visibian-data.md`.

## Steps

1. Portfolio and window. `list_portfolios`, then `get_ground_truth` for 30 or 90 days.
2. Split the rows by kind: `ai_referral` (visits from AI assistants) and `crawler_hit` (AI crawlers fetching pages). They count different things; never add them together.
3. Totals and trend per source: for each source, the total over the window and the first and last weeks. Rows with zero are omitted, so a missing day for a source means none were counted.
4. Set it beside visibility: `get_visibility_series` for the same window. Describe whether visits and visibility moved together, and say that this is a comparison, not proof of cause.
5. If there are no rows, Ground Truth may not be connected for this portfolio (it needs Google Analytics or the edge connector set up in Visibian, on the Business plan and up). Say so, and point to the free reports in the `ai-traffic-analytics` skill if the free plugin is installed.

## Format

```
## AI traffic: [portfolio], [from] to [to]

| Source | Visits from AI answers | First week | Last week |
|---|---|---|---|

| Crawler | Page fetches | First week | Last week |
|---|---|---|---|

[One or two sentences setting the visits beside visibility, with numbers.]

Not counted here: answers that named the brand without a visit, and clicks Google counts as ordinary search.
```

## Ground rules

- Counts exactly as returned, with the window. Never estimate visits that were not recorded.
- Crawler fetches are not visits by people; never present them as traffic.

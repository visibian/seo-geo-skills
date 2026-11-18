---
name: page-speed
description: Check a page's speed and Core Web Vitals (LCP, INP, CLS) from Google's PageSpeed Insights or a local Lighthouse report, separating real-user field data from lab data, read the Chrome UX Report's history of real-user Core Web Vitals for a whole site or a page over up to 40 weeks, and turn the opportunities into concrete fixes in the site's code, images, fonts and server. Use when someone asks about page speed, site speed, Core Web Vitals, PageSpeed Insights, Lighthouse, CrUX or the Chrome UX Report, LCP, INP or CLS, whether a speed fix worked, slow pages, or whether speed affects SEO or AI crawlers.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Page speed and Core Web Vitals

Measure how fast a page is for real visitors, find what slows it, and fix it where the page is built.

## What to tell the user first

- Core Web Vitals are three measures of real visits at the 75th percentile: Largest Contentful Paint (good within 2.5 seconds), Interaction to Next Paint (200 milliseconds or less) and Cumulative Layout Shift (0.1 or less) (web.dev, "Web Vitals", updated 31 October 2024).
- Field data (from real Chrome users, when Google has enough of it) decides whether a page passes. Lab data, from one Lighthouse run, is for finding causes; it moves between runs.
- Google has no single page experience signal; its ranking systems "look at a variety of signals that align with overall page experience", and it "always seeks to show the most relevant content, even if the page experience is sub-par" (Google Search Central, "Understanding page experience in Google Search results", updated 22 September 2026). Speed alone does not lift a page.

## Steps

1. Measure the key pages, from this skill's folder:
   `python3 scripts/page_speed.py https://example.com/pricing` (mobile; add `--strategy desktop` for desktop).
   If it answers 429, the shared quota is used up: ask the user to set a free PageSpeed Insights API key of their own in `PAGESPEED_API_KEY`, or to run Lighthouse on their machine and give you the report (`--file report.json`; the command is in the script's help). Never ask the user to paste a key into the chat.
2. Read field data first. If a metric is "poor" or "needs improvement", that is the problem to solve. If there is no field data, say so and work from lab data.
3. For the trend, and for the whole site rather than one page, read the Chrome UX Report's history:
   `python3 scripts/crux_history.py https://example.com` (add `--page` for one page, `--form-factor phone`, `--periods 40` for about ten months). It needs a free key with the Chrome UX Report API enabled in `CRUX_API_KEY` (the same Google Cloud key as PageSpeed Insights works once both APIs are enabled). It shows each metric now, its first value in the history, its best and worst, and how many weekly periods were good, so it answers "did our fix work" and "since when are we failing". Without a key, skip this step and say so.
4. Match causes to fixes, using the opportunities and the largest element the script names:
   - LCP: serve the main image in a modern format at the size shown, preload it or give it `fetchpriority="high"`, never lazy-load it; cut server response time (caching, a CDN); remove render-blocking CSS and scripts above it.
   - INP: break up long JavaScript tasks, defer or remove third-party scripts, avoid heavy work in input handlers.
   - CLS: give images, videos, ads and embeds width and height or an aspect ratio; reserve space for banners; load web fonts with `font-display` and matching fallback metrics.
5. In a codebase, make the changes where the page is built (components, image pipeline, font loading, server or CDN settings), then measure again. Field data covers "the previous 28-day collection period" (PageSpeed Insights, "About PageSpeed Insights", updated 21 October 2024), so it reflects a change only gradually.

## Output

- A table per page: metric, field value and rating, lab value.
- With the history: whether each metric improved, held or slipped, and since which period.
- The three to five changes with the most effect, each tied to a metric and to the element or file it touches.
- What could not be measured, and why (no field data, quota, a page behind a login).

## Ground rules

- Report numbers as the tools return them, with the date and device. Do not average runs into a new number.
- Do not promise a ranking change from speed alone.
- The Lighthouse performance score is Lighthouse's own; present it as that, never as Visibian's or your own score.

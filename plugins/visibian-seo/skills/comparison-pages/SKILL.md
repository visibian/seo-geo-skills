---
name: comparison-pages
description: Write fair "X vs Y" comparison pages and "alternatives to Y" pages that buyers and AI assistants can trust, built from each product's own published pages with the date each fact was read, a plain comparison table, and the rows where the competitor is ahead kept in. Use when someone asks for a versus page, a competitor comparison, an alternatives page, a "best X for Y" roundup of their own category, or wants an existing comparison page checked for accuracy.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Comparison pages

Comparison questions ("Acme vs Example", "alternatives to Example") are where buyers decide. A comparison page earns trust, from readers and from anyone who quotes it, only if it is accurate and fair.

## Steps

1. Pick the comparison from real buyer questions (see the `buyer-questions` skill): which competitor, for which buyer, on which criteria.
2. Read each product's own pages the same day: pricing, features, plans and limits, integrations, terms that matter (contracts, free trial, data location). Record the URL and the date read for every fact. Prefer the vendor's own page over a third-party summary. Where a page is unclear, say so instead of guessing.
3. Choose criteria the buyer cares about, not only the ones the user's brand wins. Six to twelve rows is usually enough.
4. Build the table with `assets/comparison-template.md`. Keep every row where the competitor is ahead, and say plainly who each product suits better. A page that hides the competitor's strengths reads as an advert, and buyers check.
5. Write the page answer-first: two or three sentences that answer "which is better for whom", then the table, then a section per criterion with the facts and their sources (see the `answer-first-content` skill).
6. Date it: show "Prices and features as published by each company on [date]" near the table, and plan a review date. Comparison pages go stale quickly.
7. For an "alternatives to Y" page, list the real alternatives a buyer would consider, including ones that compete with the user's brand, each with who it suits.
8. Markup: a WebPage or Article with `mentions` naming each product compared as a Product or Organization is enough. Do not mark up the competitor's ratings or prices as structured data on your page.

## Output

- The page, with its table, sources and dates.
- A list of facts that could not be confirmed from the vendor's own pages.
- A review date.

## Ground rules

- Every fact about a competitor comes from a source with a date. Never invent or estimate a competitor's price, feature, customer count or rating.
- No disparaging language, no claims that cannot be checked ("the best", "the only"), and no fake reviews or testimonials.
- Use competitors' names and trademarks only to identify them, the way a buyer would.
- Say what changed since the last review when updating a page.

---
name: structured-data
description: Write, add and check JSON-LD structured data (schema.org markup) for a website, such as Organization, WebSite, Product, SoftwareApplication, LocalBusiness, Article, BreadcrumbList, Event and Review, following Google's required and recommended properties. Use when someone asks for schema markup, JSON-LD, rich results, structured data for AI search or ChatGPT, or wants existing markup validated or fixed in their code.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Structured data

Write correct JSON-LD that describes what a page is, keep it true to what the page shows, and be exact about what it does and does not do for AI answers.

## What to tell the user first

Structured data helps search engines read a page's facts. Google calls it useful and says there is "no special schema.org structured data" needed for its AI features; tests so far found no clear rise in AI citations from adding it. Details, with sources and dates, are in `references/evidence.md`. Recommend it as good practice for search and for keeping facts consistent, never as a way to get named by an assistant.

## Steps

1. Find what exists. In a codebase, search for `application/ld+json`, `schema.org`, and framework helpers (for example `next-seo`, a `JsonLd` component, Yoast or Rank Math settings in WordPress, a Shopify theme's `structured-data` snippets). On a live page, run from this skill's folder:
   `python3 scripts/check_jsonld.py https://example.com/page`
   or point it at a built HTML file. It reads the raw HTML, the way a crawler that runs no scripts sees the page.
2. Pick the types that match what the page really is. Use `references/types.md` for the right type per page and a template for each. One page usually needs one main node, plus Organization and WebSite once on the home page, and BreadcrumbList on inner pages.
3. Fill in only facts that are on the page. Google asks that everything in the markup be visible on the page. Never add ratings, reviews, prices or awards that the page does not show, and never invent them.
4. Link the nodes with stable `@id` values (for example `https://example.com/#organization`), so the Organization is described once and referenced everywhere.
5. Validate. Run `scripts/check_jsonld.py` on the result. Fix every error. Treat notes as suggestions. For a type the script does not know, check it in Google's Rich Results Test and the Schema Markup Validator.
6. In a codebase, put it where the page is built, so it stays in step with the content (for example generated from the same product data as the visible price), and add it to the server-rendered HTML rather than injecting it after load.

## Output

- The JSON-LD, ready to paste or committed in code, one block per page type.
- The checker's result after the change.
- A short list of what was left out because the page does not show it.

## Ground rules

- Never put a fact in the markup that is not on the page or that the user has not confirmed.
- Every claim about how a search engine or assistant uses structured data carries its source and date, and may have changed since.
- Do not promise rich results or AI citations. Google decides rich results; no test has shown that markup makes an assistant name a brand.

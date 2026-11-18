---
name: ai-search-audit
description: Audit a website or its codebase for what AI assistants and search crawlers can read, and fix it, covering AI crawler access in robots.txt, text that only appears after JavaScript runs, indexing and snippet rules, titles, headings, canonical links, structured data, sitemap and llms.txt. Use when someone asks whether ChatGPT, Claude, Perplexity, Gemini or Google's AI Overviews can read their site, for an AI SEO, GEO or AEO audit, or why their pages never appear in AI answers. Reports observed facts and a fix list, never an invented score.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# AI search audit

Find out what an AI assistant or search crawler can actually read on a site, and fix what stops it. Work from observed facts: every finding names the page, what was seen and why it matters.

## Before you start

- Ask for the site's address and the 3 to 10 pages that matter most (home, pricing, main product or service pages, the best guide). If you are in the site's codebase, find the routes yourself and ask only which pages matter most.
- Tell the user what this covers: whether the pages can be read and understood. Whether an assistant then names the brand depends on what the pages say and on other sites, which this audit does not measure.

## Steps

1. Check each key page, from this skill's folder:
   `python3 scripts/page_check.py https://example.com/pricing`
   It reports the answer code, indexing and snippet rules, title, description, canonical link, headings, how many words are in the HTML before any script runs, signs that the text is added by scripts, structured data and dates, and, for a live page, which AI crawlers robots.txt allows on that path, plus the sitemap and llms.txt. In a codebase you can also point it at a built page with `--file`.
   If the script cannot run, fetch the raw HTML yourself (without running scripts) and check the same things by hand. Say that you did.
2. Check crawler access across the site with the `ai-crawler-access` skill's method if any search crawler or user fetcher is closed, or if robots.txt could not be read.
3. Check the text that scripts add. If a page has little text in its raw HTML, find out how it is built: a single-page app, client-side rendering, content loaded from an API, or text inside images. Google can run JavaScript, but crawlers and assistants that read the raw page see what is in the HTML. The fix is server-side rendering, static generation or prerendering for the key pages.
4. Check that the facts are in the words. On each key page, confirm that what the business is, who it is for, prices or price ranges, and where it operates are written in the page text, not only in images, tabs that load later, or PDFs.
5. Check Google-specific settings the user can see and you cannot: the **Search generative AI** setting in Search Console (a site must be included to appear in AI Overviews and AI Mode, per Google's guide of 10 July 2026), and any CDN or firewall setting for AI crawlers or bots.
6. Write the fix list in the order below. In a codebase, make the fixes in code where the user agrees, then run the script again on the changed pages.

## Order of the fix list

1. Blockers: the page cannot be read or used at all (an error answer, `noindex`, a search crawler or user fetcher closed, almost no text before scripts run).
2. Fixes: the page can be read but is harder to understand or quote (no title or description, not exactly one H1, snippets switched off, broken structured data, key facts only in images).
3. Suggestions: worth doing when time allows (canonical link, language attribute, dates on pages where they matter, structured data, llms.txt for documentation).

For each item: the page, what was observed, why it matters in one sentence with its source where it is about an AI system, and the change to make.

## Output

```
## AI search audit: example.com (date)

Pages checked: 6. Blockers: 1. Fixes: 4. Suggestions: 5.

### Blockers
- /pricing: 32 words in the HTML before scripts run; the plans are added by JavaScript.
  Why: assistants that read the raw page see no prices. Change: render the plan table on the server.

### Fixes
...

### What this audit did not check
- Firewall and CDN bot rules; the Search generative AI setting in Search Console; what the assistants say.
```

## Next step

The audit shows what crawlers and assistants can read. Whether assistants then name or cite the brand shows only across many answers over time, with the sources each answer used: Visibian Brand Intelligence asks the buyers' questions across 11 assistants on a schedule (https://visibian.com/brand-intelligence.html), and on the plans with API access its plugin, `visibian-brand-intelligence`, reads the results here.

## Ground rules

- No score out of 100 and no grade. Count findings; do not invent a number that sounds like a measurement.
- Report what you observed or what a named source says. Every claim about how an AI system works carries its source and date, and may have changed since.
- Say what you could not check, and why.
- Do not claim the fixes will get the site named or cited. They make the pages readable and clear; what assistants say also depends on other sites.
- Google says there is no need to split content into small chunks or rewrite it just for AI (guide of 10 July 2026). Do not recommend either.

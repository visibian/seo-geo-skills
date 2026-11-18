---
name: seo-monitoring
description: Monitor a website for SEO changes and regressions by crawling it now and comparing with an earlier crawl to find pages that disappeared or can no longer be indexed, new noindex tags, status codes and redirects that changed, titles, meta descriptions, canonicals and h1 headings that changed, structured data types lost, pages that lost content or every internal link, AI crawlers newly blocked in robots.txt, the sitemap shrinking and llms.txt removed. Use when someone asks what changed on their site, to monitor SEO, track changes after a redesign, migration, deploy or CMS update, catch SEO regressions, compare two audits, or check whether fixes from an audit are live.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# SEO change monitoring

Crawl the site, keep the crawl, and compare the next crawl with it. Most search problems start with a change nobody meant to make: a template that drops the canonical, a deploy that adds noindex, a migration that loses pages, a robots.txt rule that shuts out a crawler.

## Steps

From this skill's folder:

1. The baseline. If the user has no earlier crawl, make one and keep it:
   `python3 scripts/site_audit.py https://example.com --max-pages 200 --out seo-audit/baseline`
   Tell the user to keep the `seo-audit/` folder (in the repository, or wherever they keep reports) and to rerun step 2 after each release, migration or redesign, or on a schedule.
2. The new crawl, with the same `--max-pages`:
   `python3 scripts/site_audit.py https://example.com --max-pages 200 --out seo-audit/latest`
3. Compare:
   `python3 scripts/audit_diff.py seo-audit/baseline/audit.json seo-audit/latest/audit.json --out seo-audit/changes.md`
4. Read the result in this order:
   - Blockers: pages that could be indexed and cannot now (an error, noindex, a canonical pointing away, a robots.txt block), AI search and user crawlers newly shut out. Find the change that caused each one (a deploy, a CMS setting, a plugin, a CDN rule) and undo or fix it first.
   - Fixes: indexable pages that are gone, canonicals that moved, structured data types lost, pages that shrank or lost every internal link, a sitemap that lost addresses, llms.txt removed.
   - Notes: changed titles, descriptions and headings, new pages and redirects. Confirm each was meant; a changed title on a page that ranks deserves a look in Search Console after a few weeks (`search-console` or `keyword-research`).
5. When the user agrees the later crawl is the new normal, it becomes the baseline: copy `seo-audit/latest` over `seo-audit/baseline`.

In a codebase, run the crawl on a staging or preview address before a release and compare it with production, so regressions are caught before they ship.

## Output

- The blockers, each with its likely cause and the fix.
- The other changes grouped as the script groups them, and which ones look intended.
- The date of each crawl and the page limit, and whether a crawl reached it.

## Ground rules

- Report observed differences only. A page missing from one crawl may only be outside its page limit; say so when the report notes it, and rerun with a higher `--max-pages` before calling a page lost.
- The crawler reads pages the way search and AI crawlers do, without running scripts. Text that appears only after scripts run is not compared.
- Do not predict traffic or ranking effects from a change; Search Console shows them after the fact.

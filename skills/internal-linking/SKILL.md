---
name: internal-linking
description: Improve a website's internal links for SEO and AI search, finding orphan pages, pages buried more than three clicks deep, pages linked from only one place, generic anchor text such as "click here", and the specific links worth adding between pages on the same topic. Use when someone asks about internal linking, site structure, orphan pages, topic clusters or hub pages, link equity, or why a page is not found by search engines or crawlers. Works from the seo-audit skill's crawl.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Internal linking

Help crawlers and readers reach every important page, and make clear what each page is about through the links that point to it.

## Why it matters

Google finds most new pages by following links, and reads anchor text to understand the page linked to (Google Search Central, "SEO Starter Guide" and "Link best practices for Google", both updated 10 December 2025). A page no crawled page links to can be missed or treated as less important; the same holds for AI search crawlers that discover pages by following links.

## Steps

1. Get a crawl. If the user has run the `seo-audit` skill, use its `audit.json`. Otherwise run it first:
   `python3 scripts/site_audit.py https://example.com --out seo-audit/`
2. Read the link graph, from this skill's folder:
   `python3 scripts/link_graph.py seo-audit/audit.json`
   It lists orphan pages, weakly linked pages and deep pages, each with candidate source pages that share words in their title and main heading, plus the most linked pages and the pages reached through generic anchors. For one page in detail: `--page URL`.
3. Judge each suggestion as an editor: would a reader of the source page want the target page at that point? Keep the ones that would; drop the rest.
4. Propose the changes:
   - a link in the body text, with an anchor that says what the target page is (not "click here");
   - for a group of pages on one subject, a hub page that links to each and is linked from each (a topic cluster);
   - for important deep pages, a path from the menu, a hub or the home page;
   - for orphans that should not exist any more, a redirect or removal from the sitemap instead.
5. In a codebase, add the links where the content lives (Markdown, CMS fields or templates), then crawl again and compare.

## Output

- A table of the links to add: from page, to page, anchor text, where in the source page.
- Hub pages to create or strengthen, with the pages they gather.
- Orphans to link, redirect or retire.
- Generic anchors to rewrite.

## Ground rules

- Suggestions come from shared words and need a person's judgement; never add links just to raise counts.
- Keep anchors natural and varied; Google's spam policies count manipulative linking and keyword-stuffed anchors.
- Do not add sitewide footer links to every page as a fix for orphans; link from where the subject is discussed.

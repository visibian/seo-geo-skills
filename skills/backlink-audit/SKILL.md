---
name: backlink-audit
description: Audit a website's backlinks from free sources, namely the link exports of Google Search Console, Bing Webmaster Tools and Ahrefs' free webmaster account, and find link building opportunities. Counts referring domains and linking pages, the pages with the most links, anchor text and nofollow, ugc or sponsored links; checks live whether each link still exists; finds links pointing at broken pages to reclaim with a redirect; and lists the sites that link to competitors but not to the site. Use when someone asks about backlinks, link building, referring domains, lost links, broken backlinks, link reclamation, anchor text, a competitor backlink gap, digital PR targets, or disavowing links.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Backlink audit

Read the links other sites point at this one, check which still exist, recover the ones that point at broken pages, and find the sites worth asking next. All from free sources the site owner already has.

## Get the data

Ask the user for one or more exports (each needs the site verified in that tool; none needs a paid plan):

1. Google Search Console, Links. Export external links, "Latest links" (linking pages with their last crawl date) and the "Top linking sites" table. No anchor text or target pages there.
2. Bing Webmaster Tools, Backlinks. Export the site's backlinks (linking page, anchor text, target page). Under the similar sites tab, Bing also shows the backlinks of any other domain without verification: export one file per competitor for the gap. Bing calls its competitor data a representative sample.
3. Ahrefs' free account for verified sites (Ahrefs Webmaster Tools), Site Explorer, Backlinks, if the user has it.

Optional: the Tranco list of the top million sites (free at tranco-list.eu) to show how well known each linking site is.

Never ask for the user's passwords or for access to their accounts; work from the files they give you.

## Steps

From this skill's folder:

1. The profile:
   `python3 scripts/backlinks.py latest-links.csv bing-backlinks.csv --site example.com --brand "brand,brand name"`
   It reads each export's columns by name, merges them, drops the site's own links, and reports linking sites, linking pages, the pages with the most links, anchor text by kind (brand, address, generic, words, empty or image) and link types where the export has them.
2. Which links still exist: add `--verify --max-verify 150`. It fetches each linking page (obeying robots.txt, one at a time) and reports links that are live, pages that load without a link to the site (removed, or sent through the site's own redirect or a script), and pages that no longer answer. The live check also shows the real share of nofollow, ugc and sponsored links.
3. Links to reclaim: add `--check-targets`. Every linked page on the site that answers an error is a set of links doing nothing. Restore the page, or redirect it with a 301 to the closest live page, starting with the pages most linking sites point at. This is the fastest link building there is.
4. The competitor gap: add `--competitor rival-a.csv --competitor rival-b.csv`. Sites that link to several competitors and not to the site come first: they already cover the topic and link out. Sort them into kinds (lists and roundups, directories and marketplaces, publications, communities, partners) before planning outreach.
5. The plan, by effort and likely return:
   - Reclaim: the broken targets from step 3; then links that point at redirected addresses, by asking the linking site to update them.
   - Pages from step 2 that load without a link: where the link was removed, ask whether it can come back, with an updated resource; where the page links through its own redirect, there is nothing to ask.
   - Unlinked mentions: pages that name the brand without linking. Search for the brand name excluding the site's own domain, and ask politely for a link where the mention is about the site.
   - The competitor gap: roundups and comparison pages first (offer accurate facts, a demo or a quote), then directories and marketplaces where the product genuinely fits, then publications through original data or expert comment.
   - Assets that earn links on their own: original research, free tools, and reference pages others cite.

## Output

- The profile in numbers, with the files and the date, and the top linking sites and pages.
- The links to reclaim, ordered by linking sites, each with the fix.
- Lost links, and the gap list sorted into kinds, with the first 20 prospects and why each fits.
- What the data cannot tell: links the tools have not found, and the value of any one link.

## Ground rules

- Count and report; never score a link's worth or label links "toxic". No tool outside Google knows how Google weighs a link.
- Do not buy links, trade links in schemes, or ask for keyword-rich anchors: Google's spam policies count links meant to manipulate rankings as link spam (Google Search Central, "Spam policies for Google web search", updated 28 August 2026).
- Disavowing is rarely needed. Google's guidance is to use the disavow tool only when a site has a considerable number of spammy, artificial or low-quality links and they have caused, or are likely to cause, a manual action (Google Search Console Help, "Disavow links to your site", read 17 November 2026). Without a manual action for unnatural links, recommend against it.
- Outreach is the user's to send. Draft messages that are short, specific to the page, and honest about who is writing.

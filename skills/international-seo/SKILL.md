---
name: international-seo
description: Set up and check international SEO for a multilingual or multi-country website, covering hreflang tags (ISO language, script and region codes, x-default, return links, self-references), canonical links across language versions, html lang, sitemap hreflang, URL structure (folders, subdomains or country domains) and translation quality for search and AI assistants. Use when someone asks about hreflang, international or multilingual SEO, translating a site, country targeting, or why the wrong language version shows in Google or in AI answers.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# International SEO

Make sure each language and country version is found, shown to the right readers, and not treated as a duplicate.

## What Google asks for

From "Tell Google about localized versions of your page" (Google Search Central, updated 21 September 2026):

- hreflang values are an ISO 639-1 language code, optionally an ISO 15924 script (zh-Hant) and an ISO 3166-1 Alpha 2 region (en-GB). Other codes are not supported; Google names es-419 as an example.
- Each version lists every version, itself included, and the links must be returned: if page X names Y, Y must name X, or the pair may be ignored.
- x-default marks the page for readers who match none of the languages, such as a language selector.
- The annotations can sit in the HTML head, in HTTP headers, or in the sitemap; "the three methods are equivalent from Google's perspective".

## Steps

1. Check what the site has, from this skill's folder:
   - a few pages and their alternates: `python3 scripts/hreflang_check.py https://example.com/ https://example.com/de/`
   - the whole site, after a `seo-audit` crawl: `python3 scripts/site_audit.py https://example.com --out seo-audit/` then `python3 scripts/hreflang_check.py --audit seo-audit/audit.json`
2. Fix in this order: invalid codes, missing self-references and return links, alternates that redirect, answer an error, ask not to be indexed or name another canonical, then x-default and `<html lang>`.
3. Check the structure: one address per language or country version (a folder, subdomain or country domain), never the same address changing language by cookie or by the visitor's location alone; links between versions that a crawler can follow; the menu and footer translated too.
4. Check the translation: titles, descriptions, headings, image alt text and structured data translated, not only the body; prices, dates and numbers in each market's format; names of products and brands left as they are.
5. In a codebase, generate the hreflang set from one list of locales, so every page carries the same complete, returned set; then run the check again.

## Output

- The findings from the script, grouped, with the pages affected.
- The locale list and the hreflang block each page should carry.
- Structure and translation problems seen, with examples.

## Ground rules

- Report what the pages carry; when you cite Google's rules, give the document and its date.
- Do not machine-translate and publish without a native speaker's read; say so when the user plans to.
- Do not redirect visitors by location without a way to reach the other versions: "the default IP addresses of the Googlebot crawler appear to be based in the USA" (Google Search Central, "How Google crawls locale-adaptive pages", updated 10 December 2025), so it may never see the others.

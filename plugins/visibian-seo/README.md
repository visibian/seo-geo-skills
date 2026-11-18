# Visibian SEO & GEO

Free SEO, GEO and AEO skills: crawl, audit and monitor a site, live Search Console data and keyword research, backlinks, on-page optimization, content briefs, internal links, Core Web Vitals, hreflang, local and ecommerce SEO, structured data, client reports, and pages readable and quotable for ChatGPT, Claude, Gemini, Perplexity and Google's AI Overviews. No account needed.

The skills work from the pages, files and reports you point them at, and report what they observe with its source and date. They do not produce scores.

## Skills

| Skill | What it does |
|---|---|
| `seo-audit` | Crawls a site and lists what breaks crawling, indexing and understanding, by priority. |
| `seo-monitoring` | Compares each crawl with the last and flags pages lost, new noindex and changed canonicals. |
| `search-console` | Pulls Search Console live: queries and pages, index status of each page, sitemap errors. |
| `keyword-research` | Finds quick wins, low click-through, questions and topics in your Search Console data. |
| `backlink-audit` | Reads free link exports, checks links live, finds broken pages to reclaim and competitor gaps. |
| `on-page-seo` | Optimizes one page for its query: title, headings, opening, sources, author, links. |
| `content-brief` | Writes a brief from the pages that already answer the topic, with facts and sources. |
| `internal-linking` | Finds orphan, deep and weakly linked pages, and the links worth adding. |
| `page-speed` | Reads Core Web Vitals and their history from Google and Lighthouse, and turns them into fixes. |
| `structured-data` | Writes JSON-LD and checks it against Google's required properties. |
| `international-seo` | Checks hreflang codes, return links and canonicals across language versions. |
| `local-seo` | Business profiles, consistent addresses, reviews, location pages and LocalBusiness markup. |
| `ecommerce-seo` | Product and category pages, Product markup, merchant feeds and faceted navigation. |
| `seo-report` | Turns an audit into a client-ready, white-label HTML report. |
| `ai-search-audit` | Checks what AI assistants and crawlers can read on your key pages. |
| `geo-optimization` | Makes each section of a page quotable in AI answers, with sources and figures. |
| `ai-crawler-access` | Reads robots.txt for 24 AI crawlers and writes the rules you choose. |
| `llms-txt` | Writes or checks an llms.txt file, and says what it does not do. |
| `brand-fact-sheet` | Compares the brand's core facts across its own pages. |
| `answer-first-content` | Drafts pages that open with the answer, every claim sourced and dated. |
| `buyer-questions` | Collects the questions buyers ask, from your own data, and maps them to pages. |
| `comparison-pages` | Drafts versus and alternatives pages that keep the rows where the rival is ahead. |
| `ai-traffic-analytics` | Sets up the Google Analytics, Search Console and Bing reports that count AI traffic. |
| `brand-in-ai-answers` | Explains what can be known about a brand in AI answers without tracking, and what cannot. |

## Use it

Install the plugin, then ask in plain words, for example:

- "Run an SEO and AI search audit of my website."
- "Which keywords should I target? Here is my Search Console export."
- "Make this page easier for ChatGPT and Google's AI Overviews to quote."

Skills load when a request matches them. In Claude Code you can also run one directly, for example `/visibian-seo:seo-audit`.

## Install

| Where | How |
|---|---|
| Claude Code | `/plugin marketplace add visibian/seo-geo-skills`, then `/plugin install visibian-seo@visibian` |
| claude.ai and Cowork | Customize, Plugins, Add marketplace, with the address https://github.com/visibian/seo-geo-skills, then install Visibian SEO & GEO |
| ChatGPT and Codex | `codex plugin marketplace add visibian/seo-geo-skills`, then install Visibian SEO & GEO from the Plugins Directory in the ChatGPT desktop app or Codex |
| GitHub Copilot CLI | `copilot plugin marketplace add visibian/seo-geo-skills`, then `copilot plugin install visibian-seo@visibian` |
| Cursor, VS Code, Gemini CLI and others | see the README at https://github.com/visibian/seo-geo-skills |

## What it runs, sends and stores

- The skills are instructions and Python scripts that use only the standard library.
- The scripts run on your machine, or in your assistant's code environment, when a skill asks for them. They request only the pages and files you point them at (a site's pages, robots.txt, sitemap or llms.txt), identified as `VisibianSkill/1.0 (+https://visibian.com)`. The site crawler reads robots.txt first, skips what it closes and waits between requests.
- `page-speed` asks Google's PageSpeed Insights API and Chrome UX Report API (googleapis.com) about the address you give, with your own API key if you set one; `search-console` asks Google's Search Console API (searchconsole.googleapis.com) with an access token you set yourself, and only reads. Keys and tokens are read from your environment, sent only to Google, and never printed.
- `backlink-audit` fetches the linking pages in your exports to see whether each link still exists, and the linked pages on your own site, the same polite way.
- Search Console data, link exports, audit files and reports stay on your machine. Nothing is sent to Visibian. Nothing is stored by the plugin.
- Facts about AI crawlers come from Visibian's AI crawler directory (https://visibianhq.com/research/crawlers/), copied into the plugin as `crawlers.json`, each company's page read on the date it gives.

## Support

Write to support@visibian.com, or see https://visibian.com/contact.html.

## Licence

MIT. See LICENSE.

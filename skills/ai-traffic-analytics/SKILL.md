---
name: ai-traffic-analytics
description: Set up and read the free reports that count visits and citations from AI assistants, namely Google Analytics 4's AI Assistant channel and a custom channel or segment for the assistants it leaves out, Google Search Console's report on AI Overviews and AI Mode, Bing Webmaster Tools' AI Performance report for Copilot, and ChatGPT's utm_source tag, and explain what each one cannot see. Use when someone asks how much traffic ChatGPT or other AI tools send them, why AI visits show up as direct traffic, or how to track AI referrals in GA4.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# AI traffic analytics

Help the user count what the free tools can count about AI assistants, and be clear about the gaps. Every fact in this skill is in `references/reports.md` with its source and the date it was read.

## Steps

1. Ask which tools they have: Google Analytics 4 (or another analytics tool), Google Search Console, Bing Webmaster Tools, server logs or a CDN dashboard.
2. Google Analytics 4. Show them the **AI Assistant** channel in the default channel group (Reports, Acquisition, Traffic acquisition, by Session default channel group). Google describes it as visits from sources like ChatGPT, Gemini, DeepSeek, Copilot or Grok; it excludes Google's AI Overviews and AI Mode. Then:
   - check the Referral channel for AI assistants Google's list does not cover yet, with the source filter in `references/reports.md`;
   - if some are missing, create a **custom channel group** that copies the default one and adds a rule above Referral for those sources, so reports going forward put them in one place. Custom channel groups apply to past data too.
   - Note that ChatGPT adds `utm_source=chatgpt.com` to links it shows (OpenAI's publisher FAQ), so those visits can be found by source.
3. Search Console. Open the generative AI performance report (all sites since 31 August 2026). It counts impressions of links to the site in AI Overviews and AI Mode, by page, country, device and date. Clicks from AI answers are not separated; they sit in the main Performance report under Web search.
4. Bing Webmaster Tools. Open the AI Performance report (public preview since 10 February 2026): citations of the site in Copilot and Bing's AI summaries, the cited pages, a sample of the searches behind them, and since June 2026, views by intent and topic, citation share and period comparison.
5. Put the numbers together in a simple monthly table (template below). Compare a month with the month before, page by page. Do not add the different reports together; each counts a different thing.
6. Explain the gaps (below) so the user does not read silence as absence.

## What the free reports cannot see

- An answer that names the brand without a link, or a link no one clicks.
- What an answer said about the brand: right or wrong, recommended or not.
- Clicks from Google's AI Overviews and AI Mode, which Google counts with ordinary search clicks.
- Visits from app users whose clicks arrive without a referrer; analytics files many of these as Direct.
- Citations in other assistants: Search Console covers only Google's AI features and Bing's report only Microsoft's, so citations in ChatGPT, Claude or Perplexity show up only as the visits they send, if any.
- Competitors: every report shows only the user's own site.

## Monthly table

| Month | GA4 AI Assistant sessions | Other AI referrals (custom) | Key event conversions from AI | Search Console AI impressions | Bing AI citations |
|---|---|---|---|---|---|

## Ground rules

- Report the numbers as the tools show them, with the date range. Never estimate AI visits that the tools did not record, and never multiply a number to "correct" for what is missing.
- Every statement about what a report counts carries its source and the date it was read, and may change; Google and Microsoft update these reports often.
- If the user wants to know what assistants actually say about the brand, that is beyond these reports; see the `brand-in-ai-answers` skill.

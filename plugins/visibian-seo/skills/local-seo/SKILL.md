---
name: local-seo
description: Improve local SEO and local AI visibility for a business with a place or a service area, covering the Google Business Profile, Apple Business Connect and Bing Places, NAP consistency (name, address, phone) across the website, structured data and directories, reviews and replies, location and service-area pages, LocalBusiness JSON-LD, and how AI assistants such as ChatGPT, Gemini and Siri find local businesses. Use when someone asks about local SEO, Google Maps or the local pack, a Google Business Profile, local citations, reviews, multi-location pages, "near me" searches, or why AI assistants recommend competitors nearby.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Local SEO and local AI visibility

Make sure that when someone asks a search engine or an assistant for a business like this one nearby, the business's facts are complete, consistent and trusted everywhere the answer is drawn from.

## Why it matters now

45% of US consumers used AI tools for local business recommendations, up from 6% a year earlier, making AI assistants the third most used source after Google and Facebook (BrightLocal, survey of 1,002 people, February 2026, https://www.brightlocal.com/research/consumer-review-survey/). Assistants answer local questions from the same profiles, maps, review sites and websites people use, so the groundwork is shared.

## Steps

1. One record of the facts. With the `brand-fact-sheet` skill, write the exact name, address (or service area), phone, hours, categories, services and website for each location. Every place below must match it.
2. The profiles, completed and current:
   - Google Business Profile: primary and secondary categories, hours including holidays, services or products, attributes, description, photos, the website link per location.
   - Apple Business Connect (Apple Maps and Siri) and Bing Places (Bing and Microsoft Copilot).
   - The directories that matter for the trade and the country (industry directories, chambers, review sites).
3. The website:
   - One page per location (or per service area served), with the address, map, hours, local phone, what is offered there and something specific to the place. No near-identical copies with only the town name changed.
   - The facts in the page text and in the footer, matching the profiles.
   - `LocalBusiness` structured data (or its specific subtype, such as Dentist or Plumber) on each location page, checked from this skill's folder: `python3 scripts/check_jsonld.py https://example.com/location`. See the `structured-data` skill for writing it.
4. Reviews: ask every real customer, make it easy (a direct link), reply to each review, good or bad, and never buy, gate or write reviews.
5. Check consistency: the `brand-fact-sheet` skill compares the facts across the site's own pages; the profiles and directories are checked by hand, so give the user a checklist with each address.

## Output

- The fact sheet per location.
- A checklist per profile and directory: what is missing or different.
- Location page fixes, and the LocalBusiness JSON-LD for each.
- A plan for reviews and replies.

## Ground rules

- Facts only from the business; never guess hours, prices or service areas.
- Follow each platform's rules: real addresses only, no keyword-stuffed business names, one profile per real location.
- Whether assistants then recommend the business shows only across repeated local questions over time; Visibian Brand Intelligence tracks the questions buyers ask across 11 assistants, in the markets and languages chosen, with five of the assistants asked as if from that market (https://visibian.com/brand-intelligence.html).

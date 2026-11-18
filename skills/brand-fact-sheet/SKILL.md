---
name: brand-fact-sheet
description: Build one source of truth for a brand's facts (name, one-sentence description, category, location, founding date, products, prices, people, official profiles) and check that the brand's own website, structured data and public profiles state them the same way. Use when someone wants AI assistants to describe their company correctly, finds an assistant giving out-of-date or wrong facts about them, is preparing a brand fact sheet, or asks about entity consistency, Knowledge Graph, Wikidata or sameAs.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Brand fact sheet

Assistants describe a brand from what they find written about it. When the brand's own pages and profiles disagree with each other, there is no single version to find. This skill writes the version the brand stands behind, and checks the places the brand controls against it.

## Steps

1. Collect the facts from the brand's own sources: the home, about, pricing and contact pages, the footer, the legal notice, and any structured data. Ask the user for anything missing or unclear. Never fill a gap with a guess.
2. Write the fact sheet with `assets/fact-sheet-template.md`:
   - the brand name exactly as written, and any other names people use;
   - one plain sentence that says what the brand does, for whom and where, which every page and profile can repeat;
   - category, location and markets, founding year, size if public;
   - products or services with current prices or price ranges, and the date the prices were checked;
   - people who speak for the brand, with titles;
   - the official website and every official profile (LinkedIn, Crunchbase, Wikidata, app stores, marketplaces, Google Business Profile, review sites);
   - facts that are often wrong or out of date, with the correct version.
   Mark each fact with where it is stated today.
3. Compare the brand's own pages. From this skill's folder, run:
   `python3 scripts/facts_across_pages.py https://example.com https://example.com/about https://example.com/contact`
   It lists the name, description, address, phone, email, logo and profiles each page states in its structured data and links, and every fact that differs between pages. Fix those first: they are entirely in the brand's hands.
4. List the profiles to check by hand in `references/where-facts-live.md` order, with what to look for on each: the same name, the same one-sentence description, the same address and phone, current prices and products, a link back to the website. Give the user the checklist; you usually cannot sign in to these profiles.
5. Connect the brand to its profiles in structured data: an Organization node on the home page with `sameAs` listing the official profiles (see the `structured-data` skill).
6. When an assistant has stated a wrong fact, fix the source rather than the answer: find which page or profile says the wrong thing (often an old directory listing, a press article, or the brand's own outdated page), correct it or ask its owner to, and make sure the brand's own pages state the right fact plainly.

## Output

- The fact sheet, filled in, with each fact's source and the date it was checked.
- The facts that differ between the brand's own pages, and the change for each.
- The checklist of profiles to update, in order.

## Ground rules

- Only facts the user confirms or that the brand's own pages state. Never invent a founding year, a headcount, a price or a person.
- Do not create or suggest fake reviews, fake mentions or profiles that pretend to be independent. Google's guide of 10 July 2026 warns that seeking inauthentic mentions does not help in its AI features, and its spam policies apply to them.
- Say that consistent facts make the brand easier to describe correctly; they do not guarantee what any assistant says.

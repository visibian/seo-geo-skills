---
name: source-gap-plan
description: Build a plan to earn a place on the sites and pages AI answers rely on, from the user's Visibian source data, showing which domains and pages answers retrieve and cite, where a competitor is named and the brand is not (gap answers), and which kinds of source (editorial, reviews, forums, reference, corporate) carry the category. Use when someone asks which sites ChatGPT, Perplexity or Google's AI cite for their category, where to get mentioned, for a digital PR or outreach list for AI search, or why competitors are cited instead of them, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Source gap plan

AI answers lean on a set of pages in each field. This skill finds the ones where competitors appear and the brand does not, and turns them into a plan of honest work. How to read the data: `references/reading-visibian-data.md`.

## Steps

1. Portfolio and window. `list_portfolios`, then a window of 30 or 90 days.
2. What kinds of source matter. `get_source_types`: the share of retrievals and citations by type. This says where effort pays in this field, for example review sites in one category, trade press in another.
3. Which domains. `list_source_domains`: sort by gap answers (`gap_chats`), then by citations. Separate the brand's own domain, competitors' domains, and third-party domains.
4. Which pages. `list_source_pages` for the top third-party domains: the actual pages, their type, when they were last used, and gap answers.
5. Classify each page by what it would take to appear there, with `references/source-plays.md`: a listing or profile to claim or correct, a review program, an editorial or comparison page to pitch with something worth citing, a community where the brand can answer honestly as itself, a reference source with its own rules.
6. Write the plan: the 10 pages or domains worth the effort first, each with the play, the owner and what success looks like, then the brand's own pages to strengthen where the answers already look (see the `answer-first-content` skill).

## Format

```
## Source gap plan: [portfolio], [from] to [to]

Answers in this field lean on: [source types with shares].

| # | Page or domain | Type | Gap answers | Citations | Play | Next step |
|---|---|---|---|---|---|---|

Own pages to strengthen: [pages from list_source_pages on the brand's domain, with what to add]
```

## Ground rules

- Figures come only from tool calls, with their window.
- Never present paid placements as editorial, write or buy reviews, or post in communities without saying who you are. Google's guide of 10 July 2026 says seeking inauthentic mentions does not help in its AI features, and its spam policies apply to them.
- Do not promise that appearing on a page will get the brand cited; say it puts the brand where the answers already look.

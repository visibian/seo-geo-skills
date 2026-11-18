---
name: buyer-questions
description: Find the 10 to 30 questions real buyers ask before choosing a product or service like the user's, in the buyers' own words, from sources the user already has (Search Console and Bing queries, site search, support tickets, sales calls, reviews, forums), group them by stage of the decision, and map each to the page that should answer it. Use when someone asks which questions or prompts their brand should show up for in ChatGPT, Perplexity or Google's AI answers, wants a prompt list for AI visibility, a content gap list, or an FAQ built from real demand.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Buyer questions

Build the list of questions that decide whether a buyer finds the brand, written the way buyers ask them, and find which ones the site does not answer yet.

## Steps

1. Understand the offer. What the brand sells, to whom, where, at what price, and the 3 to 5 alternatives buyers weigh it against. Use the brand's own pages, or the `brand-fact-sheet` skill's output if there is one.
2. Collect real questions from the sources in `references/sources-of-questions.md`, starting with the ones the user has access to. Keep each question in the buyer's words, with where it came from. Ask the user to export or paste what you cannot reach (for example Search Console queries or support tickets).
3. Add the situation. Buyers often describe their situation in a question: their size, budget, location, the tool they use now, a constraint. Keep those details; they change which brands fit. Google describes its AI Mode as running several related searches for one question (query fan-out, guide of 10 July 2026), so related sub-questions matter too.
4. Group by stage with `references/stages.md`: the problem, the category ("best X for Y"), comparisons ("X vs Y", "alternatives to Y"), the decision (price, reviews, integrations, trust) and use (setup, how-to).
5. Choose 10 to 30. Prefer questions that come up often, from buyers who fit the brand, at stages where a buyer chooses. Drop questions the brand cannot honestly answer or does not serve.
6. Map each to a page: the page that answers it today, the page that should answer it and needs work, or no page yet. A page should answer the question plainly near the top (see the `answer-first-content` skill).

## Output

A table, also offered as CSV:

| # | Question (buyer's words) | Stage | Source | Who asks | Page that answers it | Status |
|---|---|---|---|---|---|---|
| 1 | Which scheduling software works for a two-chair dental clinic in Ohio? | Category | Search Console | Small clinic owner | /dental-scheduling | Needs a direct answer at the top |

Then: the three missing pages worth writing first, and why.

## Ground rules

- Every question comes from a real source the user can see, or is marked as a suggestion to confirm. Never present invented questions as buyer data, and never invent search volumes.
- Do not run the questions through assistants to rank the brand or count how often it appears. One answer proves little, because answers change from one try to the next; measuring that takes many runs over time on several assistants. If the user wants that, the `brand-in-ai-answers` skill explains the options.
- Keep personal data out: strip names, emails and account details from tickets and call notes before using a question.

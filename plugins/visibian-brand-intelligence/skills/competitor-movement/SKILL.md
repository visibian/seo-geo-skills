---
name: competitor-movement
description: Show which competitors gained or lost ground in AI answers, on which assistants, in which countries and on which topics, from the user's Visibian competitive data, with figures rebuilt from answer counts and the number of answers behind each. Use when someone asks who is beating them in ChatGPT, Gemini, Perplexity or other assistants, which competitor is rising, where they lose to a rival, or for a competitive AI visibility analysis, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Competitor movement

Find where the brand wins and loses against named competitors in AI answers. How to read the data and the reporting rules: `references/reading-visibian-data.md`.

## Steps

1. Portfolio and windows. `list_portfolios`, then pick two windows of equal length to compare, for example the last 30 days and the 30 before (use `from` and `to`).
2. Ranking. `list_competitors` for each window: who leads by share of voice, and who moved.
3. Where it happens. `get_competitive_breakdown` for each window. Group the rows by AI model, then by country, then by topic. For each group and brand, add up the counts and then divide (visibility = sum of `mentioned_chats` / sum of `chats`; share of voice = sum of `mentions` / sum of `all_mentions`). Keep the number of answers (`chats`) beside each figure.
4. Find the movements that matter: the largest changes in share of voice between the windows for the brand and its top three competitors, by model and by topic. Leave out slices with few answers, and say that you did.
5. Explain with sources, not guesses. For the biggest loss, call `list_source_domains` for the same window and look at the domains with the most gap answers (a competitor named, the brand not). Those are where the competitor is present and the brand is not.
6. Write it up in the format below.

## Format

```
## Competitor movement: [portfolio], [window A] vs [window B]

[One sentence: the biggest change, with its numbers and the answers behind them.]

| Brand | Share of voice A | Share of voice B | Change |
|---|---|---|---|

### By assistant

[Where the brand gained or lost most, with answer counts.]

### By topic

[The same, by topic.]

### Where the rival appears and you do not

[The top domains by gap answers.]

Left out for having too few answers: [slices].
```

## Ground rules

- Figures come only from tool calls, with their windows and answer counts. Never average percentages across days or slices.
- A change on few answers is noise until it repeats; say so instead of drawing a conclusion.
- Describe competitors by what the data shows; no speculation about their tactics.

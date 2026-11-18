---
name: visibility-brief
description: Write a short weekly or monthly brief of a brand's AI visibility from the user's Visibian account, covering visibility, share of voice, sentiment and position against competitors, the trend, the sources AI answers cite, active misinformation flags and answers that changed, with every number exactly as Visibian returns it. Use when someone asks how their brand is doing in ChatGPT, Gemini, Perplexity, Google AI Mode or other assistants, what changed this week or month, or for an AI visibility update, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Visibility brief

A brief a busy reader can act on in two minutes, built only from the user's Visibian data. How to read each tool and number, and the reporting rules: `references/reading-visibian-data.md`. Read it before writing the first brief.

## Steps

1. Pick the portfolio and window. Call `list_portfolios`. If there are several, ask which one, or offer one brief per portfolio. Default window: the last 30 days (`30d`); use `7d` for a weekly brief.
2. Get the headline numbers: `get_visibility` for the window. Note the user's brand (`is_self`) and the three competitors with the highest share of voice.
3. Get the trend: `get_visibility_series` for the same window. Compare the first and last weeks of the window by the days that have data; say which days had none.
4. Get what explains it: `top_sources` (the domains answers cite), `list_hallucinations` with `severity: critical` first, and `get_answer_drift` for material changes where the brand was gained or lost.
5. Write the brief in the format below. Lead with the one thing the reader should know. Then the numbers, then what changed, then what to look at.
6. Offer the next step: a deeper look with `competitor-movement`, `hallucination-fixes`, `source-gap-plan` or `answer-drift-review`.

## Format

```
## AI visibility: [portfolio], [from] to [to]

[One sentence: the most important change or fact, with its number.]

| Brand | Visibility | Share of voice | Sentiment | Avg. position |
|---|---|---|---|---|
| [brand] (you) | 34.2% | 18.0% | 71 | 2.4 |
| [competitor] | ... | ... | ... | ... |

### Trend

[First week] to [last week]: [numbers]. No answers were collected on [dates], if any.

### Sources and facts

The most cited domains: [top 5]. Wrong facts: [count of critical and warning flags], for example [one flag: what the answer said, what the fact sheet says, which model]. Answers that changed: [count of material changes, gained or lost].

### Worth a look

[Two or three items, each tied to a number above.]
```

## Ground rules

- Every number comes from a tool call in this conversation, with its window. Never estimate, extrapolate or fill a missing day with zero.
- Do not average daily percentages; use the counts in `get_competitive_breakdown` when the user wants a figure for a slice (see the reference).
- Do not say why a number moved unless the data shows it. Offer possible reasons as questions to check.
- If a tool fails, say which and why (see the error table), and write the brief from what did work.

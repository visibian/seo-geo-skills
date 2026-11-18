---
name: client-report
description: Draft a monthly AI visibility report for an agency's client from the agency's Visibian workspace, one portfolio per client, covering the headline numbers against competitors, the trend, what changed, wrong facts found, the sources answers rely on, and the work done and planned, in the agency's own voice and with every number exactly as Visibian returns it. Use when an agency asks for a client report, a monthly AI search or GEO report, or a summary for several clients, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Client report

A report an agency can send to its client after a read-through, built from the agency's Visibian workspace. How to read the data: `references/reading-visibian-data.md`.

## Steps

1. Which clients. `list_portfolios`. Each portfolio is usually one client brand. Confirm which ones, and the month (use `from` and `to` for the calendar month).
2. Ask the agency for the human part: the work done this month, what is planned, and anything the client asked about. Never invent work.
3. Collect the data for each portfolio: `get_visibility` (this month and last month, for the change), `get_visibility_series`, `list_competitors`, `top_sources`, `list_hallucinations`, `get_answer_drift`, and `get_ground_truth` if the client's plan has it.
4. Write one report per client in the format below, in the agency's voice and with the client's name. Keep it short: a client reads the first lines and the table.
5. Mark what needs a check: a big change on few answers, a tool that failed, a missing month.

## Format

```
# AI visibility report: [client], [month year]

[One sentence: the most important change this month, with its number.]

| | This month | Last month | Change |
|---|---|---|---|
| Visibility | | | |
| Share of voice | | | |
| Sentiment (0 to 100) | | | |
| Average position (1 is first) | | | |

### Against competitors

[The top three by share of voice, with numbers.]

### Answers that changed

[Answers gained or lost, from Answer Drift.]

### Wrong facts

[How many were found, and the most important one with the fix in progress.]

### Sources the answers cite

[The top sources.]

### Visits from AI

[Totals by source, if available.]

### Work done, and next month

[From the agency.]

Data from Visibian, [from] to [to], for the assistants this portfolio tracks.
```

## Ground rules

- Every number from a tool call in this conversation, with its period. No estimates, no forecasts.
- Work done and plans come only from the agency.
- Do not explain a change with a cause the data does not show. "At the same time as" is the most the data supports.
- Keep each client's report to that client's portfolio. Never mix data between clients.

# Reading Visibian data

The Visibian connector is read-only. It answers from the same data as the user's Visibian dashboard, for the one workspace its token belongs to. It changes nothing.

## The tools

| Tool | Takes | Returns |
|---|---|---|
| `list_portfolios` | nothing | the workspace name and its portfolios (tracked brands): `id`, `name`, `domain`, `status` |
| `get_visibility` | `portfolio_id`, `range` | for the brand and each competitor: `visibility`, `share_of_voice`, `sentiment`, `position`; `is_self` is true for the user's own brand |
| `get_visibility_series` | `portfolio_id`, `range` or `from` and `to` | one row per day per brand: `date`, `brand`, `is_self`, `visibility` |
| `list_competitors` | `portfolio_id`, `range` | the competitors only, ranked by share of voice |
| `top_sources` | `portfolio_id`, `range` | the 10 domains AI answers cite most |
| `list_hallucinations` | `portfolio_id`, optional `severity` (`critical` or `warn`) | a `summary`, and active flags: `detected_at`, `model`, `prompt`, `fact`, `expected` (the brand's fact sheet), `model_said`, `severity`, `verdict`, `confidence`, `evidence` |
| `list_prompts` | `portfolio_id`, optional `status` (`active`, `suggested`, `archived`) | the tracked questions: `text`, `status`, `intent_type`, `branding` |
| `get_competitive_breakdown` | `portfolio_id`, `range` or `from` and `to` | one row per day, AI model, country, topic and brand, with counts: `chats` (answers), `mentioned_chats`, `mentions`, `all_mentions`, `sentiment_sum`, `sentiment_count`, `position_sum`, `position_count` |
| `list_source_domains` | `portfolio_id`, window | every domain the answers retrieved: retrieved %, retrieval rate, citations, citation rate, `gap_chats` |
| `list_source_pages` | `portfolio_id`, window | up to 500 most-retrieved pages: `url`, `title`, `host`, `page_type`, classification, retrievals, citations, brand mentions, `gap_chats`, `last_used` |
| `get_source_types` | `portfolio_id`, window | retrievals and citations by source type (editorial, user-generated, reference, corporate and others) |
| `get_answer_drift` | `portfolio_id`, window | re-asked questions whose answer changed: a drift score from 0 to 100 against the previous answer to the same question on the same model, whether the change is material, and whether the brand was gained or lost |
| `get_ground_truth` | `portfolio_id`, window | one row per day per source: `kind` (`ai_referral` visits or `crawler_hit`), `source`, `count` |

`range` is `7d`, `30d` (the default) or `90d`. `from` and `to` are dates (YYYY-MM-DD), up to a year apart. Dated answers say the window they cover in `from` and `to`, or `range`.

## What the numbers mean

- Visibility: the share of AI answers in the window that mention the brand, as a percentage (42.1 means 42.1%).
- Share of voice: the brand's share of all brand mentions in those answers.
- Sentiment: 0 to 100, higher is more positive.
- Position: the order in which the brand is first mentioned among brands; 1 means named first. Lower is better.
- Gap answer: an answer that named a competitor and not the brand.
- Drift score: 0 to 100, how much an answer changed from the previous answer to the same question on the same model.

## Rules for reporting them

1. Report numbers exactly as the tools return them, rounded only for display, always with the portfolio name and the date window.
2. Do not average daily percentages. To get visibility for a period, a model, a country or a topic from the breakdown, add up the counts first, then divide: visibility = sum of `mentioned_chats` / sum of `chats`; share of voice = sum of `mentions` / sum of `all_mentions`; sentiment = sum of `sentiment_sum` / sum of `sentiment_count`; position = sum of `position_sum` / sum of `position_count`.
3. A missing day means no answers were collected that day, not zero visibility. Never fill gaps with zeros.
4. Say how many answers a figure rests on when you slice the breakdown finely (one model, one country, one topic, a few days). When a slice has few answers, say so plainly and do not draw a conclusion from it.
5. Do not invent causes. The data shows what changed and when; it does not say why. Offer possible reasons only as questions to check, and say they are guesses.
6. Do not recompute or rename the dashboard's measures, and do not create new scores. Use the tools' fields.
7. Quote answers and evidence as given, short, and say which model and question they came from.

## Errors

| Answer | Meaning | What to tell the user |
|---|---|---|
| 401, "invalid or expired API token" | the token is wrong, revoked, or the workspace's plan has ended | create a new token in Settings, under API & MCP access, or check the plan |
| 403, code -32003 | the plan does not include API access | API and MCP access come with the Studio, Growth and Network plans |
| 429 | more than 120 requests in a minute | wait a minute and try again |
| "Portfolio not found in this workspace" | the id is not in this token's workspace | call `list_portfolios` and use an id from it |

# The free reports, their sources and their limits

## Google Analytics 4: the AI Assistant channel

Google's "[GA4] Default channel group" help page, read 5 November 2026 (https://support.google.com/analytics/answer/9756891):

- "AI Assistant is the channel by which users arrive at your site from sources like ChatGPT, Gemini, Deepseek, Copilot, or Grok. It excludes Google's AI Overviews and AI Mode."
- Rule: the medium is set to `ai-assistant` and the campaign to `(ai-assistant)` when the referrer matches Google's list of AI assistants; the channel is sessions whose medium exactly matches `ai-assistant`.

Google does not publish the full list. To find AI referrals it may not cover, filter Session source in the Referral channel with this regular expression (the addresses the assistants' web apps used on 5 November 2026; check your own referrer report for others):

```
(chatgpt\.com|chat\.openai\.com|perplexity\.ai|claude\.ai|gemini\.google\.com|copilot\.microsoft\.com|chat\.deepseek\.com|grok\.com|chat\.qwen\.ai|kimi\.com|chat\.z\.ai|chat\.mistral\.ai|meta\.ai)
```

A custom channel group (Admin, Data display, Channel groups) can copy the default group and add a channel called, for example, "AI assistants (all)" with the rule "Session source matches regex" and the expression above, placed above Referral. Custom channel groups apply to past data as well as new data.

## ChatGPT's tag

OpenAI's publisher FAQ (https://help.openai.com/en/articles/12627856, cited on visibian.com on 30 October 2026): links in ChatGPT search results carry `utm_source=chatgpt.com`, so analytics can count those visits by source.

## Google Search Console: generative AI performance report

- Google Search Central Blog, "Introducing Search generative AI performance reports in Search Console", 3 June 2026, extended to all sites on 31 August 2026: https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- Counts impressions: how many times links to the site were shown in a generative AI feature on Google Search, AI Overviews and AI Mode together. Group by page, country, device and date; export. Two links in one answer count as one impression for the site. No view separates AI Overviews from AI Mode.
- Clicks from AI answers are counted in the main Performance report under the Web search type, mixed with ordinary results.
- Search Console Help, "Search generative AI control", read 30 October 2026 (https://support.google.com/webmasters/answer/16984139): the **Search generative AI** setting can take the site out of AI Overviews, AI Mode and the AI features in Discover. Leave it on for a brand that wants to appear there.

## Bing Webmaster Tools: AI Performance

- Bing Webmaster Blog, 10 February 2026, public preview: citations of the site in Copilot, Bing's AI summaries and some partner services, the cited pages, and a sample of the searches behind the citations. https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
- Bing Search Blog, 16 June 2026: four more views, also in preview, for intents, topics, citation share and comparing periods. https://blogs.bing.com/search/June-2026/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare

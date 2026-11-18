# What structured data does, and does not do, for AI answers

Each point names its source and the date it was published or read. These systems change; check the source before relying on a point for a decision.

## What the search engines say

- Google, 10 July 2026 ("Optimizing your website for generative AI features on Google Search"): structured data "isn't required for generative AI search, and there's no special schema.org markup you need to add", but it is "a good idea to continue using it as part of your overall SEO strategy, as it helps with being eligible for rich results". https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google, May 2025 ("Top ways to ensure your content performs well in Google's AI experiences on Search"): structured data is useful for sharing information in a machine-readable way, and everything in the markup should match what is visible on the page. https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search
- Google, 8 May 2026 (Search Central documentation updates): FAQ rich results no longer appear in Google Search from 7 May 2026. https://developers.google.com/search/updates
- Microsoft Bing, October 2025: "Schema is a type of code that helps search engines and AI systems understand your content", with the warning that nothing guarantees selection. Copilot answers from Bing's index. https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers
- OpenAI: has said little in public about structured data in web pages. For shopping in ChatGPT it asks merchants to send product details in a product feed. https://developers.openai.com/commerce/product-feeds/spec

## What the studies found

- Ahrefs, May 2026: pages that AI assistants cite are almost three times as likely to carry JSON-LD as pages they do not cite (53%). In a cleaner test of 1,885 pages that added JSON-LD between August 2025 and March 2026, compared with similar pages that did not, ChatGPT citations rose 2.2% and Google AI Mode citations 2.4% after 30 days, both too small to tell from chance; AI Overview citations fell 4.6% while both groups were already falling. The pages were already cited often, so the test says nothing about pages an assistant has not found yet. https://ahrefs.com/blog/schema-ai-citations/
- searchVIU, reported by Ahrefs, May 2026: when ChatGPT, Claude, Perplexity, Gemini and Google AI Mode fetched pages live, none of the five used the JSON-LD; they took the text a visitor can see. Search Engine Roundtable reported a similar finding for ChatGPT and Perplexity. https://www.seroundtable.com/chatgpt-perplexity-structured-data-text-40862.html

## What follows

- Write the facts in the visible page text first. That is what assistants that fetch a page live were seen to read.
- Add structured data for search engines, rich results and consistent facts, and keep it true to the page.
- Do not expect a measurable change in AI citations from markup alone.

# AI crawlers and settings

Generated from Visibian's AI crawler directory (https://visibianhq.com/research/crawlers/). Each company's page was read on 2026-10-29. Companies change these pages; follow the link to check before relying on a detail.

## Search crawlers: find and cite pages in answers

### OAI-SearchBot (OpenAI, for ChatGPT)

- What it does: Finds the pages that ChatGPT search can show and link to.
- Follows robots.txt: yes
- What blocking it changes: The site's pages stop appearing in ChatGPT's search answers, though it can still appear as a plain link. OpenAI says changes take about 24 hours.
- In the company's words: "Sites that are opted out of OAI-SearchBot will not be shown in ChatGPT search answers, though can still appear as navigational links."
- Documentation: https://developers.openai.com/api/docs/bots

### Claude-SearchBot (Anthropic, for Claude)

- What it does: Reads pages to improve the search results in Claude.
- Follows robots.txt: yes
- What blocking it changes: Claude stops indexing the site for search, which Anthropic says may make it less visible and less accurate in Claude's search results.
- In the company's words: "Disabling Claude-SearchBot on your site prevents our system from indexing your content for search optimization."
- Documentation: https://support.claude.com/en/articles/8896518

### Googlebot (Google, for Google Search, AI Overviews and AI Mode)

- What it does: Crawls the web for Google Search, including AI Overviews and AI Mode.
- Follows robots.txt: yes
- What blocking it changes: The site drops out of Google Search, AI Overviews and AI Mode alike. To limit only what is shown, Google offers nosnippet, data-nosnippet, max-snippet and noindex.
- In the company's words: "To appear in AI Overviews or AI Mode, a page must be indexed and eligible to be shown in Google Search with a snippet."
- Documentation: https://developers.google.com/search/docs/appearance/ai-features

### Bingbot (Microsoft, for Bing and Microsoft Copilot)

- What it does: Crawls the web for Bing, whose index Microsoft Copilot answers from.
- Follows robots.txt: yes
- What blocking it changes: The site drops out of Bing. To stay in Bing but out of its AI answers, Bing offers the NOARCHIVE meta tag; NOCACHE lets only the link, title and snippet be used.
- In the company's words: "Content tagged NOARCHIVE will not be included in Bing Chat answers."
- Documentation: https://blogs.bing.com/webmaster/2023/9/Announcing-new-options-for-webmasters-to-control-usage-of-their-content-in-Bing-Chat/

### PerplexityBot (Perplexity, for Perplexity)

- What it does: Finds and links pages for Perplexity's search results. Perplexity says it is not used to train AI models.
- Follows robots.txt: yes
- What blocking it changes: Perplexity asks sites to allow it so that they appear in its search results. Changes can take up to 24 hours.
- In the company's words: "It is not used to crawl content for AI foundation models."
- Documentation: https://docs.perplexity.ai/docs/resources/perplexity-crawlers

### Applebot (Apple, for Siri, Spotlight and Safari)

- What it does: Crawls for Siri, Spotlight and Safari, including answers that may link to the sources.
- Follows robots.txt: yes
- What blocking it changes: The site drops out of those results. If robots.txt does not name Applebot but names Googlebot, Applebot follows the rules for Googlebot.
- In the company's words: "Applebot respects standard robots.txt directives in general search crawls that are targeted at Applebot."
- Documentation: https://support.apple.com/en-us/119829

### meta-webindexer (Meta, for Meta AI)

- What it does: Reads pages to improve Meta AI's search results.
- Follows robots.txt: yes
- What blocking it changes: Meta says allowing it helps Meta AI cite and link to your pages, so blocking it can cost those links.
- In the company's words: "navigates the web to improve Meta AI search result quality for users."
- Documentation: https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers

### Amzn-SearchBot (Amazon, for Alexa)

- What it does: Reads pages for search in Amazon's products, such as Alexa. Amazon says it is not used for training.
- Follows robots.txt: yes
- What blocking it changes: The site's pages are no longer eligible for Amazon's search experiences. If robots.txt does not name it, it follows the rules given to other search crawlers.
- In the company's words: "Amzn-SearchBot does not crawl content for generative AI model training."
- Documentation: https://developer.amazon.com/docs/amazonbot/amazonbot.html

### MistralAI-Index (Mistral, for Le Chat)

- What it does: Crawls the web to build Mistral's index, for search in its products.
- Follows robots.txt: yes
- What blocking it changes: Mistral stops indexing the site. Its page does not say more.
- In the company's words: "MistralAI-Index is for automated crawling of the web for indexing purposes only."
- Documentation: https://docs.mistral.ai/robots

### DuckAssistBot (DuckDuckGo, for DuckDuckGo AI answers)

- What it does: Reads pages in real time for DuckDuckGo's AI answers, which cite their sources. DuckDuckGo says it is not used to train AI.
- Follows robots.txt: yes
- What blocking it changes: DuckDuckGo stops crawling the site for AI answers within 72 hours. The site's ranking in ordinary results does not change.
- In the company's words: "This data is not used in any way to train AI models."
- Documentation: https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot

## User fetchers: open a page when a person asks

### ChatGPT-User (OpenAI, for ChatGPT)

- What it does: Opens a page when someone asks ChatGPT, or a custom GPT, about it.
- Follows robots.txt: not always
- What blocking it changes: It may still open a page a user asks for. It does not decide whether a site appears in ChatGPT search: OAI-SearchBot does.
- In the company's words: "Because these actions are initiated by a user, robots.txt rules may not apply."
- Documentation: https://developers.openai.com/api/docs/bots

### Claude-User (Anthropic, for Claude)

- What it does: Opens a page when a Claude user asks a question that needs it.
- Follows robots.txt: yes
- What blocking it changes: Claude can no longer fetch the site's pages for a user's question.
- In the company's words: "Disabling Claude-User on your site prevents our system from retrieving your content in response to a user query."
- Documentation: https://support.claude.com/en/articles/8896518

### Perplexity-User (Perplexity, for Perplexity)

- What it does: Opens a page when a Perplexity user asks a question that needs it.
- Follows robots.txt: not always
- What blocking it changes: It may still open a page a user asks for.
- In the company's words: "Since a user requested the fetch, this fetcher generally ignores robots.txt rules."
- Documentation: https://docs.perplexity.ai/docs/resources/perplexity-crawlers

### meta-externalfetcher (Meta, for Meta AI)

- What it does: Opens a link when a user asks Meta AI about it.
- Follows robots.txt: not always
- What blocking it changes: It may still open a page a user asks for.
- In the company's words: "may bypass robots.txt rules"
- Documentation: https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers

### Amzn-User (Amazon, for Alexa)

- What it does: Opens a page when a customer asks Alexa something that needs up-to-date information.
- Follows robots.txt: not always
- What blocking it changes: It may still open a page a customer asks for.
- In the company's words: "it may not follow all robots.txt directives."
- Documentation: https://developer.amazon.com/docs/amazonbot/amazonbot.html

### MistralAI-User (Mistral, for Le Chat)

- What it does: Opens pages for actions a user asks for in Mistral's products.
- Follows robots.txt: not always
- What blocking it changes: Mistral's page does not say whether these fetches follow robots.txt.
- In the company's words: "MistralAI-User is for user actions in Vibe."
- Documentation: https://docs.mistral.ai/robots

## Training crawlers and settings

### GPTBot (OpenAI, for ChatGPT)

- What it does: Collects pages that may be used to train OpenAI's AI models.
- Follows robots.txt: yes
- What blocking it changes: OpenAI reads it as a request not to use the site's pages to train its models. It does not keep a site out of ChatGPT search: that is OAI-SearchBot.
- In the company's words: "Disallowing GPTBot indicates a site's content should not be used in training generative AI foundation models."
- Documentation: https://developers.openai.com/api/docs/bots

### ClaudeBot (Anthropic, for Claude)

- What it does: Collects pages that may be used to train Anthropic's models.
- Follows robots.txt: yes
- What blocking it changes: Anthropic reads it as a signal that the site's future pages should be left out of training. Anthropic also honours Crawl-delay.
- In the company's words: "When a site restricts ClaudeBot access, it signals that the site's future materials should be excluded."
- Documentation: https://support.claude.com/en/articles/8896518

### Google-Extended (Google, for Gemini)

- What it does: A setting that tells Google whether pages Googlebot collects may be used to train Gemini models and to feed facts into Gemini's answers.
- Follows robots.txt: a setting, read from robots.txt
- What blocking it changes: Google stops using the pages to train Gemini and to feed facts into its answers in the Gemini app and in Google's tools for developers. It does not change Google Search, AI Overviews or AI Mode, which follow the rules for Googlebot.
- In the company's words: "Google-Extended does not impact a site's inclusion in Google Search nor is it used as a ranking signal in Google Search."
- Documentation: https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers

### Applebot-Extended (Apple, for Apple Intelligence)

- What it does: A setting that tells Apple whether it may use the pages Applebot collects to train its foundation models.
- Follows robots.txt: a setting, read from robots.txt
- What blocking it changes: Apple stops using the pages for training. The site stays in Siri, Spotlight and Safari results, and the setting does not affect ranking.
- In the company's words: "Webpages that disallow Applebot-Extended can still be included in search results."
- Documentation: https://support.apple.com/en-us/119829

### meta-externalagent (Meta, for Meta AI)

- What it does: Collects pages for uses such as training Meta's AI models or indexing content for its products.
- Follows robots.txt: yes
- What blocking it changes: Meta stops collecting the site's pages. Meta says it may cache robots.txt for up to 24 hours.
- In the company's words: "crawls the web for use cases such as training foundation AI models or improving products by indexing content directly."
- Documentation: https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers

### Amazonbot (Amazon, for Alexa)

- What it does: Collects pages to improve Amazon's products and services, and may be used to train Amazon's AI models.
- Follows robots.txt: yes
- What blocking it changes: Amazon stops collecting the site's pages. Amazon also honours the noarchive meta tag, which keeps a page out of model training, and caches robots.txt for up to 30 days.
- In the company's words: "may be used to train Amazon AI models."
- Documentation: https://developer.amazon.com/docs/amazonbot/amazonbot.html

### MistralAI-Training (Mistral, for Le Chat)

- What it does: Collects pages to build datasets for training Mistral's AI models.
- Follows robots.txt: yes
- What blocking it changes: Mistral stops collecting the site's pages for training.
- In the company's words: "Webmasters can disallow this user agent in their robots.txt file."
- Documentation: https://docs.mistral.ai/robots

## Open archives

### CCBot (Common Crawl, for Common Crawl's public archive)

- What it does: Builds Common Crawl's open archive of the web. Many AI models have been trained on that archive, GPT-3 among them.
- Follows robots.txt: yes
- What blocking it changes: The site's pages stop being added to the archive. Pages already in it stay there.
- In the company's words: "producing and maintaining an open repository of web crawl data"
- Documentation: https://commoncrawl.org/ccbot

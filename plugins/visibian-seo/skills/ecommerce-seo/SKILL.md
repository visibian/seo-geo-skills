---
name: ecommerce-seo
description: Improve ecommerce SEO and AI shopping visibility for an online store, covering product and category pages, Product structured data (price, availability, reviews, shipping, returns), Google Merchant Center and free listings, product feeds for ChatGPT shopping, faceted navigation and filters, duplicate product variants, out-of-stock and discontinued products, and product content that AI assistants can read and recommend. Use when someone asks about ecommerce or Shopify SEO, product page SEO, product schema, merchant listings, ChatGPT or Google AI shopping, category pages, or why AI assistants recommend other stores' products.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Ecommerce SEO and AI shopping

Make products findable, readable and comparable for shoppers, search engines and the assistants that now answer "which one should I buy".

## Why it matters now

Visits from AI assistants to US retail sites grew 393% in the first quarter of 2026 against a year before, and converted 42% better than other visits in March 2026; on average only 66% of a retail product page's content could be read by AI, the lowest of the page types measured (Adobe data, reported by CMOtech, April 2026, https://cmotech.news/story/adobe-says-ai-retail-traffic-surges-as-readability-lags). ChatGPT takes product data such as price and availability from feeds merchants share with OpenAI (OpenAI, commerce documentation, https://developers.openai.com/commerce).

## Steps

1. Product pages, checked on a few best sellers:
   - `python3 scripts/check_jsonld.py https://store.com/product` (from this skill's folder) for the Product markup: name, image, offers with price, currency and availability, and, where true, aggregate rating, shipping and return policy. See the `structured-data` skill for writing it.
   - `python3 scripts/page_check.py https://store.com/product` for what a crawler reads before scripts run: price, stock, variants and the description must be in the HTML, not only added by scripts.
   - A description written for the buyer: what it is, who it suits, sizes and materials, what is in the box, how it compares; not the manufacturer's copy repeated on every store.
2. Category pages: a short introduction that helps choose, links to the subcategories and best products, and filters that do not create a new indexable address for every combination (Google, "Managing crawling of faceted navigation URLs", updated 18 December 2025).
3. Variants and duplicates: one canonical product page with its variants, or variant pages that each say what is different; consistent internal links to the canonical address.
4. Stock changes: keep a product page that is temporarily out of stock live with its availability marked; for a discontinued product, point to the replacement or the category, and remove it from the feed.
5. Feeds: Google Merchant Center for free listings and Shopping, and the product feed OpenAI describes for ChatGPT shopping; prices and availability in every feed must match the page.
6. Run the `seo-audit` skill on the store for broken links, duplicate titles and orphaned products, and `page-speed` on a product page and a category page.

## Output

- Product page fixes with the JSON-LD to add, for the template.
- Category and filter rules (which combinations are indexable).
- Feed problems found, and the matching page facts.

## Ground rules

- Prices, stock, ratings and reviews only as they really are; Google's guidelines count structured data about content hidden from the reader as a violation (Google Search Central, "General structured data guidelines", updated 10 July 2026), so never mark up reviews or ratings the page does not show.
- Do not promise placement in AI shopping answers; feeds and pages make products eligible and readable, nothing more.

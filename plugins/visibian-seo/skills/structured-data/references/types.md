# Which type for which page, with templates

Required and recommended properties follow Google Search Central's structured data pages (last updated 8 September 2026, read 5 November 2026). Replace every value with a fact the page shows. Remove a property rather than guess it.

| Page | Main node | Also |
|---|---|---|
| Home page | Organization (or a LocalBusiness subtype for a place people visit) | WebSite |
| Software or app product page | SoftwareApplication (or WebApplication) | BreadcrumbList |
| Product page in a shop | Product with Offer | BreadcrumbList |
| Branch, clinic, office, shop | LocalBusiness subtype (Dentist, LegalService, Store, Restaurant) | BreadcrumbList |
| Article, guide, blog post | Article or BlogPosting, with author as Person | BreadcrumbList |
| Event page | Event | BreadcrumbList |
| About or team page | AboutPage with Organization; Person for each named person | BreadcrumbList |

## Organization and WebSite (home page)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example Co",
      "url": "https://example.com/",
      "logo": "https://example.com/logo.png",
      "description": "One plain sentence that says what the company does and for whom.",
      "sameAs": [
        "https://www.linkedin.com/company/example",
        "https://www.wikidata.org/wiki/Q00000000"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@example.com"
      }
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com/",
      "name": "Example Co",
      "publisher": { "@id": "https://example.com/#organization" }
    }
  ]
}
```

`sameAs` lists the brand's own profiles on other sites. Only list profiles the brand controls or that describe it (for example its Wikidata item), never a similar company's.

## SoftwareApplication

Google requires `name`, `offers.price` and one of `aggregateRating` or `review`. Without a real rating or review on the page, the markup is still valid schema.org but is not eligible for the rich result; do not add a rating to get one.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Example App",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "79", "priceCurrency": "EUR" },
  "publisher": { "@id": "https://example.com/#organization" }
}
```

## Product with Offer

Google requires `name` and one of `review`, `aggregateRating` or `offers`; an Offer requires `price`.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Trail Runner 2",
  "image": "https://example.com/img/trail-runner-2.jpg",
  "description": "Text the product page shows.",
  "brand": { "@type": "Brand", "name": "Example" },
  "offers": {
    "@type": "Offer",
    "price": "129.00",
    "priceCurrency": "EUR",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/trail-runner-2"
  }
}
```

## LocalBusiness

Google requires `name` and `address`.

```json
{
  "@context": "https://schema.org",
  "@type": "Dentist",
  "name": "Example Family Dental",
  "url": "https://example.com/",
  "telephone": "+1-312-555-0100",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "100 Main St",
    "addressLocality": "Chicago",
    "addressRegion": "IL",
    "postalCode": "60601",
    "addressCountry": "US"
  },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "09:00",
    "closes": "17:00"
  }]
}
```

Keep the name, address and phone exactly as they appear on the business's Google Business Profile.

## Article

Google lists no required properties and recommends `headline`, `image`, `author`, `datePublished` and `dateModified`.

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "The headline as shown on the page",
  "image": "https://example.com/img/post.png",
  "datePublished": "2026-10-30",
  "dateModified": "2026-11-05",
  "author": { "@type": "Person", "name": "Jane Doe", "url": "https://example.com/team/jane-doe" },
  "publisher": { "@id": "https://example.com/#organization" }
}
```

## BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog" },
    { "@type": "ListItem", "position": 3, "name": "This post" }
  ]
}
```

## FAQPage

Valid schema.org, but Google stopped showing FAQ rich results on 7 May 2026. Add it only if the questions and answers are on the page and the user wants it for other consumers.

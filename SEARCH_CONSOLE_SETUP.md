# Google Search Console setup — GlobalFlowHub

This is an operator guide, not proof that the site is verified or indexed.

## Prepared in this repository

- Canonical homepage: `https://globalflowhub.org/` (already in `index.html`).
- Sitemap: `https://globalflowhub.org/sitemap.xml` (one currently canonical HTML page).
- Robots file: `https://globalflowhub.org/robots.txt` (allows general crawling; points to sitemap).

## Ownership verification (manual Google account step)

1. Go to `https://search.google.com/search-console/welcome` and sign in with the Google account that should own the property.
2. If the domain is not already registered, use **URL prefix** property: `https://globalflowhub.org/` (include `https://` and trailing slash). This can be verified by an HTML tag or by an HTML verification file.
3. Select **HTML tag** under the verification options. Google gives you a unique `<meta name="google-site-verification" content="...">` tag. Add that exact tag inside the `<head>` of the homepage; do not invent a token. To have a collaborator add the tag, share the exact tag. Alternatively, use Google's HTML verification file unchanged.
4. Publish the change to GitHub Pages and confirm that the tag/file is publicly retrievable on the live domain, then click **Verify** in Google Search Console.
5. In **Sitemaps**, submit `https://globalflowhub.org/sitemap.xml` (or `sitemap.xml` when the UI requests the suffix). Optionally use **URL inspection** to inspect the homepage.
6. Monitor **Pages/Indexing** and **Performance** reports. Search indexing and reported query data are not immediate and are not guaranteed.

## Other option: Domain property

A **Domain** property named `globalflowhub.org` includes all protocols and subdomains, but requires Google-provided DNS TXT record verification at the domain's authoritative DNS provider. Do not change existing DNS records blindly or publish guessed tokens. The domain DNS host may differ from Cloudflare's analytics service.

## Maintenance

- Leave ownership verification tag/file in place while using the property.
- Update the sitemap whenever a new canonical public HTML page is published; do not list research drafts or private routes.
- Never interpret a sitemap or this document as a claim that Google has verified ownership, indexed the site, or sent traffic.
- Cloudflare Web Analytics measures site usage; Google Search Console measures search visibility and indexing. These are independent services.

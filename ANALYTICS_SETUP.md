# GlobalFlowHub website analytics setup

## Status
**Prepared but disabled.** The website's `index.html` contains a conditional loader for Cloudflare Web Analytics, but its `gfh-cf-analytics-token` meta field is empty. As shipped, it makes **no analytics request**. This document contains no account credentials.

## Activation (site owner)
1. Visit https://dash.cloudflare.com/ and sign in or create a free account.
2. In **Web Analytics**, add `globalflowhub.org` as a site and choose the manual JavaScript installation option (menu labels can vary).
3. Cloudflare provides a beacon snippet with a **site token**. The site token is not a secret API key. Keep passwords, API keys, and session tokens out of the repository.
4. Update the blank field in `index.html`:
   `<meta name="gfh-cf-analytics-token" content="">`
   Put only the site's 32-character hex token or UUID-formatted token between the quotes. Do **not** paste the whole Cloudflare script tag; the loader already inserts the beacon when configured.
5. Merge/publish the website change, then visit the public site with tracking not blocked. Verify the beacon loads and check Cloudflare Web Analytics for page views and aggregate referrer/country data. The dashboard may take some time to populate.
6. Keep the privacy notice visible. Review privacy obligations for any future analytics changes.

## Security and privacy
- The conditional loader uses Cloudflare's official `https://static.cloudflareinsights.com/beacon.min.js` script. Loading it means browser visitors send analytics information to Cloudflare under its policies.
- Cloudflare Web Analytics is intended to be cookie-free and does not require fingerprint-based identity tracking; it is still a third-party service.
- Never record or publish individual visitors' identities; treat aggregate stats as directional indicators.
- A new analytics installation **cannot report historical visits** made before collection began.
- Analytics is separate from private GFH/LITHARA repositories, agent tools, runtime controls, and project evidence.

## Removal
To fully disable tracking, clear the meta tag token. To remove the integration entirely, delete the conditional loader and the accompanying privacy statement.

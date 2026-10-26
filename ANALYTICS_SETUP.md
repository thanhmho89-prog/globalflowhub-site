# GlobalFlowHub — Cloudflare Web Analytics

## Configuration status
The official Cloudflare Web Analytics beacon for `globalflowhub.org` has been added to `index.html` on branch `add-privacy-friendly-analytics-setup`.

**Not deployed until merged and published.** GitHub pull request #2 is the review gate. Cloudflare will begin collecting supported analytics after the updated site is published and people visit it.

The token embedded in the static script is a public *site analytics token*, not a Cloudflare account password or API credential.

## After publishing
1. Merge pull request #2 into `main` following normal review.
2. Allow the website hosting pipeline to publish, then load https://globalflowhub.org/ in a browser with analytics blocking disabled.
3. Inspect page source or developer tools to confirm a single script pointing to `https://static.cloudflareinsights.com/beacon.min.js` and a `data-cf-beacon` token.
4. In Cloudflare **Web Analytics**, choose the `globalflowhub.org` site and verify new page views. Reporting may take time; zero initially does not prove failure.
5. Keep the footer privacy notice; evaluate additional privacy and consent requirements if services or tracking practices change.

## Privacy and boundaries
- Cloudflare Web Analytics is a third-party, cookie-free analytics service and may collect aggregate traffic and performance data. Review Cloudflare's policy and documentation.
- Avoid adding identification-level tracking, visitor profiling, or additional cookies unless independently justified and disclosed.
- No past visit data can be recovered merely by enabling the beacon today.
- Tracking is unrelated to private GFH/LITHARA repositories, authority grants, runtime control, or any other operational project system.

## Removal
Delete the Cloudflare Web Analytics script block to disable the integration, then update the privacy notice accordingly.

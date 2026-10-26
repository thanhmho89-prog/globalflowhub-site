# GlobalFlowHub website performance and accessibility review

## Verified in the repository (source-only, October 2026)

- GitHub Pages serves three compact static pages: homepage, privacy notice, custom 404.
- No downloaded web fonts or framework bundles are referenced in these pages.
- The only external JavaScript included is the Cloudflare Web Analytics beacon.
- The 1200×630 social preview PNG is linked in metadata; it is **not downloaded as a visible image in the homepage markup**.
- Responsive layout breakpoints and reduced-motion CSS are present.
- Read-only static checks validate internal links, sitemap, canonical URLs, and the verification file.
- `scripts/check_performance_budget.py` adds deliberately conservative page/asset size thresholds and an allowlist for scripts. It is a regression guard, not a measurement of speed.

## Not yet verified

No live network Lighthouse report, Core Web Vitals measurement, device-based screen reader evaluation, or real-device mobile layout test has been established by the source checks. No performance or WCAG conformance score is claimed.

## Browser audit workflow

1. Open `https://globalflowhub.org/` in Chrome, preferably in a private window without extensions.
2. Open DevTools -> Lighthouse. Run **Mobile**, **Navigation** with Performance, Accessibility, Best Practices and SEO. Save the report and record its test date, URL, device emulation and environment.
3. Repeat with **Desktop**, then separately open `https://globalflowhub.org/privacy.html` and a deliberately unknown URL to inspect the custom 404.
4. In **Performance**, record LCP, CLS, TBT, FCP and any reported opportunities. For real visitors, review available field data; do not equate lab TBT with real-world INP.
5. In **Accessibility**, investigate flagged contrast, keyboard focus, landmarks, headings, labels, and target size. A high automated score is not a substitute for manual checks.
6. Check narrow viewports (320px, 375px, 390px, 768px): no horizontal scrolling; menu opens and links work; contact information wraps; text zoom at 200% remains usable.
7. Test keyboard-only navigation (Tab, Shift+Tab, Enter, Space). Confirm focus is visible, skip-to-content works, and the mobile `<details>` menu is usable.
8. If a concrete issue is found, log the exact browser/device/viewport, expected result, observed result, screenshot, and reproducible steps. Fix narrowly and rerun checks.

## Safety and maintenance

- Do not publish GFH/LITHARA private design details or security-sensitive implementation information in public reports.
- CI requires no credentials or deployment authority and checks only checked-out public files.
- Keep `google6bffe20b3f4143aa.html` unchanged for Search Console ownership verification.
- If site scope or analytics providers change, update privacy disclosures and the checks deliberately.
- Avoid adding dependencies or optimization services unless measurements demonstrate a real benefit.

## Current source-budget targets

| Resource | Limit (uncompressed repository bytes) |
| --- | ---: |
| index.html | 56 KiB |
| privacy.html | 16 KiB |
| 404.html | 16 KiB |
| Inline CSS per page | 25 KiB |
| favicon.svg | 8 KiB |
| social-preview.png | 550 KiB |

These limits detect unexpectedly large additions; they are not page-speed goals. Network transfer size, caching, image decoding, browser rendering, and provider behavior require separate measurement.

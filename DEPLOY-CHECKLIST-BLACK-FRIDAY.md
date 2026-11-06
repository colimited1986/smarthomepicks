# SmartHomePicks — Black Friday / Cyber Monday deployment checklist

Prepared: 2026-11-06

## Included in this update
- Added `/black-friday-deals/` seasonal buying guide with page title, meta description, canonical URL, Open Graph basics, and WebPage JSON-LD.
- Added a visible holiday-guide link to the homepage navigation and a homepage campaign banner.
- Added the new landing page to `sitemap.xml`.
- The page avoids invented sale prices and clearly says that prices and availability must be checked at the retailer.

## Before/at deployment
1. Commit and push the contents of this repository to the GitHub Pages publishing branch. Confirm Pages build/deployment succeeds.
2. Open `https://colimited1986.github.io/smarthomepicks/black-friday-deals/` in desktop and mobile browsers. Check all Amazon links, page layout, and internal links.
3. Verify each product's ASIN, exact model name, current availability, and any claims on the Amazon listing. The repository's own QC notes that product/ASIN/name matching was not network-verified.
4. Review Amazon Associates compliance for the current program and locale. Keep the disclosure conspicuous and do not show prices/discount percentages unless maintained through a compliant, current source.
5. In Google Search Console, inspect the homepage and landing page, run URL inspection, request indexing if available, and submit/resubmit `https://colimited1986.github.io/smarthomepicks/sitemap.xml`.
6. Test outbound affiliate click tracking and analytics (if configured) on a real device. Check that no privacy/consent requirements are missed for any analytics scripts added later.
7. Check mobile performance, image loading, keyboard focus, and console/network errors. A browser-based performance run was not available during this source audit.

## Findings from static repository audit
- Homepage has core SEO metadata, canonical, Open Graph, one H1, and WebSite / ItemList / FAQ structured data.
- `robots.txt` allows crawling and points to the sitemap.
- The sitemap already lists the existing editorial/legal pages; this update adds the campaign page.
- The repository's `qc.py` reports repeated ASINs among homepage affiliate cards and flags empty `alt` on category images. Empty alt is correct only if those images are decorative; otherwise add meaningful alt text. Repeated ASINs should be reviewed to ensure they are intentional rather than duplicate product cards.
- QC flags three compare-page anchor links as requiring verification; confirm those links land on the intended sections in the deployed page.
- QC could not run its Playwright browser checks because the browser binary was unavailable. These are not represented as passed.
- A static source audit cannot verify live prices, live Amazon product/ASIN matches, indexing status, Core Web Vitals, or current search rankings.

## Important SEO/affiliate priorities
- Publish useful, distinct content rather than thin pages made only of affiliate links.
- Keep author/editorial process and affiliate disclosure easy to find; don't imply first-hand testing unless performed.
- Track Search Console impressions/clicks and affiliate outbound clicks separately. Seasonal rankings may not arrive immediately, so support the landing page with prominent internal links and relevant social/email distribution.

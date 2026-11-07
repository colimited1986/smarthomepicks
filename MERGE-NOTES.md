# SmartHome Picks — merged repository notes

## Merge strategy
- Claude's `smarthomepicks-main-updated` is the base for content pages, SEO metadata, structured data, editorial pages, and the updated quality-check script.
- ChatGPT's `smarthomepicks-black-friday-optimized` contributes the dedicated Black Friday & Cyber Monday 2026 landing page, homepage campaign banner/navigation, and the campaign deployment checklist.
- The shared teal, warm-neutral visual system and existing image assets are retained.
- Brand wording is standardized to **SmartHome Picks** in the site wordmark and **SmartHome Picks** in titles, descriptions, editorial copy, and structured data.
- Canonical URLs, Open Graph URLs, sitemap URLs, and the GitHub Pages CNAME target use `https://smarthomepicks.online/`.
- Buying-guide pages use the shared site stylesheet, header, and navigation for a more consistent experience.
- Product review summaries use the label “Product review & buying notes”; the copy is kept practical and US-English, with claims framed around listed specifications and buyer checks rather than invented hands-on testing.

## Validation
- Static homepage QC: 69 PASS, 1 NEEDS VERIFICATION, 1 NOT TESTED.
- The remaining verification item is Amazon product/model/ASIN matching. It is intentionally not marked verified without checking each live retailer listing.
- Playwright browser checks were not run because Chromium is not installed in the build environment.
- Local navigation paths and fragment targets were checked against the merged files.

## Before publishing
1. Run `python qc.py index.html .` from the repository root.
2. Install/run Playwright Chromium and test desktop/mobile navigation, search, filters, category anchors, and the Black Friday page.
3. Manually verify each product's exact Amazon model/ASIN, current availability, affiliate tag, and any product claims.
4. Confirm the custom domain and HTTPS are active in GitHub Pages, then submit `https://smarthomepicks.online/sitemap.xml` in Google Search Console.

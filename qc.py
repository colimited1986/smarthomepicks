#!/usr/bin/env python3
"""QC for SmartHomePicks / HomeFit Picks index.html.
Usage: python3 qc.py path/to/index.html [project_root]
Static checks (bs4) + headless-browser checks (playwright). Only reports what was actually run."""
import sys, re, json, os, collections
from bs4 import BeautifulSoup

path = sys.argv[1]
root = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(path))
src = open(path, encoding='utf-8').read()
soup = BeautifulSoup(src, 'lxml')
R = []  # (status, check, detail)
def add(st, chk, det=''): R.append((st, chk, det))

# ---------- metadata ----------
t = soup.title.string.strip() if soup.title else ''
add('PASS' if 20 <= len(t) <= 65 else 'FAIL', 'title length', f'{len(t)} chars: {t}')
md = soup.find('meta', attrs={'name': 'description'})
d = md['content'] if md else ''
add('PASS' if 70 <= len(d) <= 160 else 'FAIL', 'meta description length', f'{len(d)} chars')
can = soup.find('link', rel='canonical')
add('PASS' if can and can['href'].startswith('https://') else 'FAIL', 'canonical', can['href'] if can else 'missing')
for p in ['og:title', 'og:description', 'og:url', 'og:type', 'og:site_name']:
    add('PASS' if soup.find('meta', property=p) else 'FAIL', p)
add('PASS' if soup.find('meta', property='og:image') else 'NEEDS VERIFICATION', 'og:image', 'no verified shareable image available' if not soup.find('meta', property='og:image') else '')
add('PASS' if soup.find('meta', attrs={'name': 'twitter:card'}) else 'FAIL', 'twitter:card')
add('PASS' if soup.html.get('lang') else 'FAIL', 'html lang', soup.html.get('lang', ''))
add('PASS' if soup.find('meta', attrs={'name': 'viewport'}) else 'FAIL', 'viewport meta')

# ---------- headings ----------
hs = [(int(h.name[1]), h.get_text(' ', strip=True)[:50]) for h in soup.find_all(re.compile('^h[1-6]$'))]
h1n = sum(1 for l, _ in hs if l == 1)
add('PASS' if h1n == 1 else 'FAIL', 'exactly one H1', str(h1n))
skips = [(a, b) for (a, _), (b, _) in zip(hs, hs[1:]) if b - a > 1]
add('PASS' if not skips else 'FAIL', 'heading levels do not skip downward', str(skips[:5]))

# ---------- ids / structure ----------
ids = [e['id'] for e in soup.find_all(id=True)]
dups = [k for k, c in collections.Counter(ids).items() if c > 1]
add('PASS' if not dups else 'FAIL', 'duplicate ids', str(dups))
for tag in ['main', 'header', 'footer', 'nav']:
    add('PASS' if soup.find(tag) else 'FAIL', f'<{tag}> present')
secs = soup.find_all('section')
nested = [s.get('id') or s.get('aria-labelledby') for s in secs if s.find_parent('section')]
add('PASS' if not nested else 'FAIL', 'no nested <section> wrappers', str(nested))

# ---------- JSON-LD ----------
card_ids = {a['id'] for a in soup.select('#grid > article')}
for i, sc in enumerate(soup.find_all('script', type='application/ld+json')):
    try:
        j = json.loads(sc.string)
    except Exception as e:
        add('FAIL', f'JSON-LD #{i} parses', str(e)); continue
    ty = j.get('@type')
    add('PASS', f'JSON-LD #{i} parses', ty)
    if ty == 'ItemList':
        bad = [x['url'] for x in j['itemListElement'] if x['url'].split('#')[-1] not in card_ids]
        add('PASS' if not bad else 'FAIL', 'ItemList urls point to existing card ids', str(bad[:3]))
        names = {x['name'] for x in j['itemListElement']}
        page_names = {a.find('h3').get_text(strip=True) for a in soup.select('#grid > article')}
        add('PASS' if names == page_names else 'FAIL', 'ItemList names match visible card names', str(names ^ page_names)[:200])
    if ty == 'FAQPage':
        vis = {s.get_text(strip=True) for s in soup.select('.faq summary')}
        miss = [q['name'] for q in j['mainEntity'] if q['name'] not in vis]
        add('PASS' if not miss else 'FAIL', 'FAQ schema questions are visible on page', str(miss))
    blob = json.dumps(j)
    add('PASS' if not re.search(r'aggregateRating|"offers"|"price"|"review"', blob) else 'FAIL', f'JSON-LD #{i} has no rating/price/review claims')

# ---------- affiliate ----------
tag_match = re.search(r"const TAG = '([^']+)'", src)
alinks = soup.select('a[href*="amazon."]')
# Pages without the homepage's JS affiliate-tag constant still carry the tag
# directly in their Amazon URLs; infer the expected tag from the first link.
TAG = tag_match.group(1) if tag_match else (re.search(r'[?&]tag=([^&]+)', alinks[0]['href']).group(1) if alinks and re.search(r'[?&]tag=([^&]+)', alinks[0]['href']) else '')
bad_tag = [a['href'] for a in alinks if not TAG or f'tag={TAG}' not in a['href']]
add('PASS' if alinks and not bad_tag else 'FAIL', f'all {len(alinks)} Amazon links carry tag={TAG}', str(bad_tag[:3]))
bad_rel = [a['href'] for a in alinks if not {'sponsored', 'nofollow'} <= set(a.get('rel', []))]
add('PASS' if not bad_rel else 'FAIL', 'Amazon links have rel=sponsored nofollow', str(bad_rel[:3]))
asins = [a['data-asin'] for a in soup.select('a[data-asin]')]
card_asins = [a.get('data-asin') for a in soup.select('#grid > article') if a.get('data-asin')]
add('PASS' if len(card_asins) == len(set(card_asins)) else 'FAIL', 'no duplicate product-card ASINs', f'{len(card_asins)} product cards, {len(set(card_asins))} unique ASINs')
badfmt = [a for a in asins if not re.fullmatch(r'B0[A-Z0-9]{8}', a)]
add('PASS' if not badfmt else 'FAIL', 'ASIN format (format only, NOT existence)', str(badfmt))
mism = [a['data-asin'] for a in soup.select('a[data-asin]') if a['data-asin'] not in a['href']]
add('PASS' if not mism else 'FAIL', 'href ASIN matches data-asin', str(mism))
unver = [a['id'] for a in soup.select('#grid > article') if a.get('data-verified') != 'yes']
add('NEEDS VERIFICATION', 'product/ASIN/name match on Amazon (no network)', f'{len(unver)} of {len(card_ids)} cards flagged data-verified != yes in source')
add('PASS' if soup.select('#disclosure') else 'FAIL', 'footer affiliate disclosure')
add('PASS' if soup.select('.top-disclosure') else 'FAIL', 'disclosure before first affiliate link')
cards_no_disc = [a['id'] for a in soup.select('#grid > article') if 'affiliate link' not in a.get_text().lower()]
add('PASS' if not cards_no_disc else 'FAIL', 'per-card affiliate note', str(cards_no_disc))

# ---------- images ----------
imgcfg = re.findall(r"'(B0[A-Z0-9]{8})':\s*\{\s*src:\s*'([^']+)'", src)
missing = [(a, p) for a, p in imgcfg if not os.path.exists(os.path.join(root, p))]
imgdir = os.path.isdir(os.path.join(root, 'images', 'products'))
add(('NEEDS VERIFICATION' if not imgdir else ('FAIL' if missing else 'PASS')), 'configured image files exist on disk',
    f'{len(missing)} of {len(imgcfg)} missing from {root}' + ('' if imgdir else ' (images/products folder not present here; run qc.py from the repo root)'))
orphan = [a for a in asins if a not in {x for x, _ in imgcfg}]
add('PASS' if not orphan else 'NEEDS VERIFICATION', 'every ASIN has an image config entry', str(orphan))
generic_alt = re.findall(r"alt:\s*'([^']*(?:Budget|Mid-range|Premium)[^']*)'", src)
add('FAIL' if generic_alt else 'PASS', 'image alt names the actual product (not tier label)', f'{len(generic_alt)} generic alts')
for img in soup.find_all('img'):
    if not img.get('alt') and not (img.parent and img.parent.name == 'a' and img.parent.get_text(' ', strip=True)):
        add('FAIL', 'static <img> alt', str(img)[:80])

# ---------- internal links ----------
rel = sorted({a['href'] for a in soup.find_all('a', href=True)
              if not a['href'].startswith(('#', 'http', 'mailto', 'data:', 'javascript'))})
page_dir = os.path.dirname(os.path.abspath(path))
for h in rel:
    clean_h = h.split('#', 1)[0]
    if h == './' or clean_h in ('', '.', '..'): continue
    if clean_h.startswith('/'):
        target = os.path.join(root, clean_h.lstrip('/'))
    else:
        target = os.path.normpath(os.path.join(page_dir, clean_h))
    p = os.path.join(target, 'index.html') if h.endswith('/') or os.path.isdir(target) else target
    if h.endswith('/') and not os.path.isdir(target):
        p = os.path.join(target, 'index.html')
    add('PASS' if os.path.exists(p) else 'NEEDS VERIFICATION', f'internal link {h}', 'file found' if os.path.exists(p) else 'target not in provided files; verify in repo/live site')
for a in soup.find_all('a', href=True):
    if a['href'].startswith('#') and len(a['href']) > 1 and a['href'][1:] not in ids:
        add('FAIL', 'hash link target', a['href'])

# ---------- CSS class coverage ----------
css = ''.join(s.string or '' for s in soup.find_all('style'))
# Include locally linked stylesheets as well as inline styles. This matters now
# that the site uses a shared visual-system stylesheet across all pages.
for link in soup.find_all('link', rel=lambda value: value and 'stylesheet' in value):
    href = link.get('href', '')
    if href.startswith(('http://', 'https://', 'data:')):
        continue
    local_css = os.path.join(root, href.lstrip('/'))
    if os.path.isfile(local_css):
        try:
            css += open(local_css, encoding='utf-8').read()
        except OSError:
            pass
defined = set(re.findall(r'\.([A-Za-z_][\w\\:.\-]*)', css.replace('\\:', ':').replace('\\.', '.')))
defined = {re.sub(r':(hover|focus|focus-visible|active|before|after)$','',d.replace('\\', '')) for d in defined} | {d.replace('\\', '') for d in defined}
used = set()
for e in soup.find_all(class_=True): used |= set(e['class'])
JSCLS = {'chip', 'ex', 'card', 'hidden', 'has-img'}
undef = sorted(c for c in used if c not in defined and c not in JSCLS)
add('FAIL' if undef else 'PASS', 'every class in HTML has a CSS rule', f'{len(undef)} undefined: {undef[:30]}')

# ---------- accessibility (static) ----------
for inp in soup.find_all('input'):
    iid = inp.get('id')
    ok = inp.get('aria-label') or (iid and soup.find('label', attrs={'for': iid}))
    add('PASS' if ok else 'FAIL', f'input #{iid} has label')
for b in soup.find_all('button'):
    if not b.get_text(strip=True) and not b.get('aria-label'): add('FAIL', 'button without name', str(b)[:60])
for tb in soup.find_all('table'):
    add('PASS' if tb.find('caption') or tb.get('aria-label') else 'FAIL', 'table has caption/aria-label')
    ths = [th for th in tb.find_all('th') if not th.get('scope')]
    add('PASS' if not ths else 'FAIL', 'table <th> have scope', f'{len(ths)} without')
def lum(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def cr(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + .05) / (lb + .05)
for nm, fg, bg in [('stone-500 on white', '#78716c', '#ffffff'), ('stone-500 on page bg', '#78716c', '#faf8f5'),
                   ('stone-600 on white', '#57534e', '#ffffff'), ('accent on white', '#0f766e', '#ffffff'),
                   ('white on accent', '#ffffff', '#0f766e'), ('accent-dark on accent-soft', '#115e59', '#e6f4f1'),
                   ('amber-800 on amber-50', '#92400e', '#fffbeb')]:
    c = cr(fg, bg); add('PASS' if c >= 4.5 else 'FAIL', f'contrast {nm}', f'{c:.2f}:1 (WCAG AA 4.5)')

# ---------- browser ----------
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        for w, h in [(360, 740), (390, 844), (768, 1024), (1366, 768)]:
            pg = br.new_page(viewport={'width': w, 'height': h})
            errs, failed = [], []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('requestfailed', lambda r: failed.append(r.url))
            pg.on('response', lambda r: failed.append(r.url) if r.status >= 400 else None)
            pg.goto('file://' + os.path.abspath(path)); pg.wait_for_timeout(300)
            # scroll to trigger lazy images
            H = pg.evaluate('document.documentElement.scrollHeight')
            for y in range(0, H, 400): pg.evaluate(f'window.scrollTo(0,{y})'); pg.wait_for_timeout(40)
            pg.wait_for_timeout(400)
            sw = pg.evaluate('document.documentElement.scrollWidth')
            add('PASS' if sw <= w else 'FAIL', f'{w}px: no horizontal page overflow', f'scrollWidth={sw}')
            wide = pg.evaluate('''(w)=>[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>w+1&&!e.closest('.overflow-x-auto,.tbl-wrap,.hdr-nav')&&getComputedStyle(e).position!=='absolute'}).slice(0,5).map(e=>e.tagName+'.'+e.className)''', w)
            add('PASS' if not wide else 'FAIL', f'{w}px: no element pokes past viewport', str(wide))
            add('PASS' if not errs else 'FAIL', f'{w}px: JS page errors', str(errs))
            if w == 390:
                add(('NEEDS VERIFICATION' if (failed and not imgdir) else ('FAIL' if failed else 'PASS')), 'failed/404 resource requests after full scroll (file://)', f'{len(set(failed))} unique: {sorted(set(failed))[:3]}')
                # functionality
                pg.evaluate('window.scrollTo(0,0)')
                n0 = pg.evaluate("[...document.querySelectorAll('#grid>article')].filter(c=>!c.classList.contains('hidden')).length")
                add('PASS' if n0 == 6 else 'FAIL', 'initial 6 cards shown', str(n0))
                pg.fill('#q', 'pet hair'); pg.press('#q', 'Enter'); pg.wait_for_timeout(300)
                cnt = pg.inner_text('#count')
                top = pg.evaluate("[...document.querySelectorAll('#grid>article')].find(c=>!c.classList.contains('hidden')).id")
                add('PASS' if 'robot-vacuum' in top else 'FAIL', 'search "pet hair" surfaces robot vacuum first', f'{cnt} | {top}')
                pg.click('#reset'); pg.wait_for_timeout(200)
                pg.click('.chip[data-key="tier"][data-id="premium"]'); pg.wait_for_timeout(200)
                tiers = pg.evaluate("[...document.querySelectorAll('#grid>article:not(.hidden)')].map(c=>c.dataset.tier)")
                add('PASS' if tiers and set(tiers) == {'premium'} else 'FAIL', 'premium filter chip', str(set(tiers)))
                pg.click('#reset'); pg.wait_for_timeout(200)
                pg.click('#more'); pg.wait_for_timeout(200)
                n1 = pg.evaluate("[...document.querySelectorAll('#grid>article')].filter(c=>!c.classList.contains('hidden')).length")
                add('PASS' if n1 == 12 else 'FAIL', 'Show more adds 6 cards', str(n1))
                pg.click('#browse [data-setcat="smart"]'); pg.wait_for_timeout(300)
                cats = pg.evaluate("[...document.querySelectorAll('#grid>article:not(.hidden)')].map(c=>c.dataset.cat)")
                add('PASS' if cats and set(cats) == {'smart'} else 'FAIL', 'category tile "Smart Home" sets category', str(set(cats)))
                small = pg.evaluate('''()=>[...document.querySelectorAll('button,.hdr-nav a,.flinks a,a.btn')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.height<32}).map(e=>e.textContent.trim().slice(0,20))''')
                add('PASS' if not small else 'FAIL', 'tap targets >= 32px tall (visible)', str(small[:8]))
            if w in (390, 1366):
                pg.evaluate('document.querySelector("#clear")')  # noop
                hts = pg.evaluate("""()=>{const v=[...document.querySelectorAll('#grid>article:not(.hidden)')];const rows={};v.forEach(c=>{const t=Math.round(c.getBoundingClientRect().top+scrollY);(rows[t]=rows[t]||[]).push(c.getBoundingClientRect().height)});return Object.values(rows).map(r=>Math.max(...r)-Math.min(...r))}""")
                add('PASS' if all(x < 2 for x in hts) else 'FAIL', f'{w}px: card heights equal within each row', str([round(x) for x in hts]))
            pg.close()
        br.close()
except Exception as e:
    add('NOT TESTED', 'browser checks', repr(e))

order = {'FAIL': 0, 'NEEDS VERIFICATION': 1, 'NOT TESTED': 2, 'PASS': 3}
for st, c, d in sorted(R, key=lambda x: order[x[0]]):
    print(f'[{st}] {c}' + (f' — {d}' if d else ''))
cnt = collections.Counter(s for s, _, _ in R)
print('\nSUMMARY', dict(cnt))

#!/usr/bin/env python3
"""Run from the repo root. Lists the homepage plus every folder that really contains an index.html.
Usage: python3 make_sitemap.py [base_url]"""
import os, sys, datetime
base = (sys.argv[1] if len(sys.argv) > 1 else 'https://colimited1986.github.io/smarthomepicks/').rstrip('/') + '/'
skip = {'.git', '.github', 'images', 'node_modules', 'assets', 'css', 'js'}
urls = [base]
for d in sorted(os.listdir('.')):
    if os.path.isdir(d) and d not in skip and os.path.exists(os.path.join(d, 'index.html')):
        urls.append(f'{base}{d}/')
today = datetime.date.today().isoformat()
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
out += [f'  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>' for u in urls]
out.append('</urlset>')
open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'{len(urls)} URLs written to sitemap.xml')
for u in urls: print(' ', u)

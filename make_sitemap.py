#!/usr/bin/env python3
"""Run from the repo root. Lists the homepage plus every folder (including nested ones such as guides/*) that really contains an index.html.
Usage: python3 make_sitemap.py [base_url]"""
import os, sys, datetime
base = (sys.argv[1] if len(sys.argv) > 1 else 'https://colimited1986.github.io/smarthomepicks/').rstrip('/') + '/'
skip = {'.git', '.github', 'images', 'node_modules', 'assets', 'css', 'js'}
urls = [base]
for dirpath, dirnames, _files in sorted(os.walk('.')):
    dirnames[:] = sorted(x for x in dirnames if x not in skip and not x.startswith('.'))
    rel = os.path.relpath(dirpath, '.').replace(os.sep, '/')
    if rel != '.' and os.path.exists(os.path.join(dirpath, 'index.html')):
        urls.append(f'{base}{rel}/')
today = datetime.date.today().isoformat()
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
out += [f'  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>' for u in urls]
out.append('</urlset>')
open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'{len(urls)} URLs written to sitemap.xml')
for u in urls: print(' ', u)

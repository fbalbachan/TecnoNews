"""Add a collapsible lead excerpt (publisher teaser, max 2 sentences) to each row of reports/farandula.html."""
import html
import re
import sys

import requests
from bs4 import BeautifulSoup

REPORT = sys.argv[1]
MAX_CHARS = 320
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"}


def two_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?…])\s+", text)
    lead = " ".join(parts[:2])
    if len(lead) > MAX_CHARS:
        lead = lead[:MAX_CHARS].rsplit(" ", 1)[0] + "…"
    return lead


def fetch_lead(url):
    soup = BeautifulSoup(requests.get(url, headers=UA, timeout=20).text, "html.parser")
    for attrs in ({"property": "og:description"}, {"name": "description"}, {"name": "twitter:description"}):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content", "").strip():
            return two_sentences(html.unescape(tag["content"])), "bajada del medio"
    for p in soup.select("article p, p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 80:
            return two_sentences(text), "primer párrafo"
    return None, None


src = open(REPORT, encoding="utf-8").read()
if 'class="lead"' in src:
    sys.exit("leads already present")

css = (".lead { margin: 8px 0 4px; border: 1px solid var(--line); border-radius: 6px; }\n"
       ".lead > summary { cursor: pointer; padding: 6px 10px; font: 600 12px/1.4 var(--body); color: var(--muted); }\n"
       ".lead > p { margin: 0; padding: 4px 10px 10px; max-width: 70ch; }\n"
       ".lead small { color: var(--muted); font-weight: 400; }\n")
src = src.replace("</style>", css + "</style>", 1)
# Without a declared charset, a locally opened file is read as Windows-1252 and accents break
if "<meta charset" not in src:
    src = ('<!doctype html>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + src)

meta_re = re.compile(r'(<details class="art"[^>]*>.*?<p class="meta">.*?<a href="([^"]+)">nota original</a></p>)', re.S)
ok = fail = 0


def add(m):
    global ok, fail
    url = html.unescape(m.group(2))
    try:
        lead, kind = fetch_lead(url)
    except Exception as e:
        lead, kind = None, None
        print("ERR", url, type(e).__name__)
    if not lead:
        fail += 1
        return m.group(1)
    ok += 1
    return (m.group(1) + '\n    <details class="lead"><summary>Bajada <small>(' + kind + ')</small></summary>'
            '<p>' + html.escape(lead, quote=False) + '</p></details>')


src = meta_re.sub(add, src)
open(REPORT, "w", encoding="utf-8").write(src)
print(f"added {ok}, missing {fail}")

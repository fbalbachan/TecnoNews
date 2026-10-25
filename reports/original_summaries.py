"""Re-render the "Resumen" sections of reports/farandula.html from the original article text.

The summary is still chosen by the pipeline's TextSummarizer, but instead of the clause rebuilt from parse-tree
tokens ("a el", " ,", dropped complements) each selected clause is shown as the original sentence it belongs to
(Sentence.text), at most MAX_SENTENCES per article.

Run from prototype/ with a `config` file present:  python ../reports/original_summaries.py ../reports/farandula.html
"""
import contextlib
import html
import io
import os
import re
import sys

sys.path.insert(0, os.getcwd())

import requests
from bs4 import BeautifulSoup

from src.model.sentilecto import Sentilecto
from src.utils.textSummarizer import TextSummarizer

REPORT = sys.argv[1]
MAX_SENTENCES = 2
MAX_CHARS = 280
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
quiet = lambda: contextlib.redirect_stdout(io.StringIO())


def article_text(url):
    """Same extraction the report generator used (showbiz.py GenericArticleParser), minus the NewsEntry step."""
    soup = BeautifulSoup(requests.get(url, headers=UA, timeout=30).content, "html.parser")
    for tag in soup(["script", "style", "aside", "figure", "nav", "footer", "form"]):
        tag.extract()
    # The body is usually an <article>, but La Nación's <article>s are related-news teasers and its body sits in a
    # plain div: take whichever container (an <article>, or the parent of long <p>s) holds the most long paragraphs
    long_ps = lambda node: [p for p in node.find_all("p") if len(p.get_text(strip=True)) >= 60]
    candidates = soup.find_all("article") + list({id(p.parent): p.parent for p in long_ps(soup)}.values())
    body = max(candidates, key=lambda node: len(long_ps(node)), default=soup)
    paragraphs = [p.get_text(" ", strip=True) for p in body.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) >= 60 and not re.search(r"©|copyright|suscrib|newsletter", p, re.I)]
    return "\n".join(paragraphs)


def tidy(sentence):
    """get_text(" ") puts a space around inline tags (links, bold): drop it before closing punctuation."""
    sentence = re.sub(r"\s+([,.;:!?)\]»”])", r"\1", sentence)
    return re.sub(r"([(\[«“¿¡])\s+", r"\1", sentence)


NO_SUMMARY = '<p class="cls">El resumidor no seleccionó ninguna oración de esta nota.</p>'


def original_summary(text):
    with quiet():
        analysis = Sentilecto.analyze(text)
        summarizer = TextSummarizer(analysis)
        selected = []
        rebuild = summarizer._summarize_clause
        summarizer._summarize_clause = lambda clause: selected.append(clause) or rebuild(clause)
        summarizer.summarize(extended=True)
    picked = []
    for sentence in analysis["paragraph"].sentences:
        if any(clause in sentence.clauses for clause in selected) and sentence.text.strip() not in picked:
            picked.append(sentence.text.strip())
    picked = [tidy(s) for s in picked]
    picked = [s if len(s) <= MAX_CHARS else s[:MAX_CHARS].rsplit(" ", 1)[0] + "…" for s in picked[:MAX_SENTENCES]]
    return "".join("<p>%s</p>" % html.escape(s, quote=False) for s in picked)


ONLY_SOURCE = sys.argv[2] if len(sys.argv) > 2 else None  # e.g. "La Nación Espectáculos": redo just that source
LABEL = " <small>(oraciones del original)</small>"

src = open(REPORT, encoding="utf-8").read()
row_re = re.compile(r'(<details class="art" data-source="([^"]*)">.*?<a href="([^"]+)">nota original</a>.*?'
                    r'<h4>Resumen(?: <small>\(oraciones del original\)</small>)?</h4><div class="summary">)(.*?)(</div>)', re.S)

new_by_url, ok, failed = {}, 0, 0


def replace_row(m):
    global ok, failed
    if ONLY_SOURCE and html.unescape(m.group(2)) != ONLY_SOURCE:
        return m.group(0)
    url = html.unescape(m.group(3))
    try:
        summary = original_summary(article_text(url))
    except Exception as e:
        print("ERR", url, type(e).__name__, str(e)[:100])
        summary = None
    if summary is None:
        failed += 1
        return m.group(0)
    if not summary:
        summary = NO_SUMMARY
    ok += 1
    new_by_url[url] = (m.group(4), summary)
    head = m.group(1).replace("<h4>Resumen</h4>", "<h4>Resumen" + LABEL + "</h4>")
    return head + summary + m.group(5)


src = row_re.sub(replace_row, src)

# Story cards repeat the summary of their most-covered article. Identify that article among the card's own links
# by its previous summary (several rows can share the same "no selection" note, so the text alone is not enough).
card_re = re.compile(r'(<ol class="arts">(.*?)</ol>.*?<h4>Resumen \(nota con más coberturas\)'
                     r'(?: <small>\(oraciones del original\)</small>)?</h4><div class="summary">)(.*?)(</div>)', re.S)
cards = 0


def replace_card(m):
    global cards
    for url in (html.unescape(u) for u in re.findall(r'<a href="([^"]+)"', m.group(2))):
        if url in new_by_url and new_by_url[url][0] == m.group(3):
            cards += 1
            head = m.group(1)
            if LABEL not in head:
                head = head.replace("coberturas)</h4>", "coberturas)" + LABEL + "</h4>")
            return head + new_by_url[url][1] + m.group(4)
    return m.group(0)


src = card_re.sub(replace_card, src)
open(REPORT, "w", encoding="utf-8").write(src)
print("articles: %d updated, %d unchanged | story cards updated: %d" % (ok, failed, cards))

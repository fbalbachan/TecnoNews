"""Re-analyse the rows of one source in reports/farandula.html and refresh their stats, entity ranking and facts.

Analysis is the one the report was generated with (showbiz.py: GenericParser.create_news_entry -> set_analisys_info
-> Sentilecto, ReferentRanker, fact clauses) and rendering is gen_report.py's, but the article text comes from the
fixed extraction (the container with most long paragraphs, not the first <article>). The bajada, the summary and
the related coverage of each row are left untouched: relations depend on the whole crawled corpus.

Run from prototype/ with a `config` file present:
    python ../reports/refresh_rows.py ../reports/farandula.html "La Nación Espectáculos"
"""
import contextlib
import html
import io
import os
import re
import sys

sys.path.insert(0, os.getcwd())

import mongomock
from src.services.mongodb import connector

DB = mongomock.MongoClient()["showbiz"]
connector.MongoConnector.get_instance = classmethod(lambda cls, mode=None: DB)

import requests
from bs4 import BeautifulSoup

from src.model.referent.referentRanker import ReferentRanker
from src.model.sentilecto import Sentilecto
from src.sentinews.parsers.generic_parser import GenericParser

REPORT, SOURCE = sys.argv[1], sys.argv[2]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
CLASS_LABEL = {"person": "persona", "place": "lugar", "organization": "organización", "other": "otro", None: "—"}
quiet = lambda: contextlib.redirect_stdout(io.StringIO())
e = html.escape


class GenericArticleParser(GenericParser):
    """showbiz.py's parser, with the body taken from the container holding the most long paragraphs."""

    def parse(self, url, source):
        soup = BeautifulSoup(requests.get(url, headers=UA, timeout=30).content, "html.parser")
        for tag in soup(["script", "style", "aside", "figure", "nav", "footer", "form"]):
            tag.extract()
        meta = lambda **kw: (soup.find("meta", attrs=kw) or {}).get("content")
        title = meta(property="og:title") or (soup.h1.get_text(" ", strip=True) if soup.h1 else None)
        long_ps = lambda node: [p for p in node.find_all("p") if len(p.get_text(strip=True)) >= 60]
        candidates = soup.find_all("article") + list({id(p.parent): p.parent for p in long_ps(soup)}.values())
        body = max(candidates, key=lambda node: len(long_ps(node)), default=soup)
        paragraphs = [p.get_text(" ", strip=True) for p in body.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p) >= 60 and not re.search(r"©|copyright|suscrib|newsletter", p, re.I)]
        tags = [t.strip() for t in (meta(name="news_keywords") or meta(name="keywords") or "").split(",") if t.strip()]
        tags += [m["content"] for m in soup.find_all("meta", attrs={"property": "article:tag"}) if m.get("content")]
        if not title or len(paragraphs) < 2:
            return None
        return self.create_news_entry(title=title.strip(), content="\n".join(paragraphs), tags=tags or ["espectáculos"],
                                      source=source, url=url, original_categories=["espectaculos"])


def understand(entry):
    """showbiz.py's understand(), without the summary (already rendered from the original by original_summaries.py)."""
    with quiet():
        analysis = Sentilecto.analyze(entry.content)
    paragraph = analysis["paragraph"]
    ranking = ReferentRanker(paragraph).rank()
    entities = [{"name": str(r.name()).replace("_", " "), "class": r.semantic_classification(),
                 "occurrences": r.ref_count(), "score": round(score, 2)} for r, score in ranking]
    facts = []
    for clause in paragraph.clauses():
        if not clause.voice or not clause.verb or not clause.is_fact():
            continue
        slots = {}
        for structure in clause.syntactic_structures:
            if structure.name in ("subject", "od", "oi", "equative", "regimen") and structure.all_entities():
                slots[structure.name] = ", ".join(lexical(x) for x in structure.all_entities())
        if "subject" in slots and len(slots) > 1:
            facts.append({"verb": clause.verb.lemma(), "voice": clause.voice, **slots})
    sentiment = analysis["summary"].get(paragraph, {})
    return {"entities": entities, "facts": facts,
            "sentiment": {k: round(v, 1) for k, v in sentiment.items() if k in ("positive", "negative")},
            "sentences": len(paragraph.sentences), "clauses": len(paragraph.clauses())}


def lexical(entity):
    """lexical_form is a method on most entities but a plain str attribute on some (e.g. implicit ones)."""
    form = entity.lexical_form
    return str(form() if callable(form) else form).replace("_", " ")


# --- gen_report.py rendering -------------------------------------------------------------------------------------
def entity_table(entities, limit=12):
    rows = "".join(
        "<tr><td>%d</td><td>%s</td><td><span class=\"cls\">%s</span></td><td class=\"num\">%d</td><td class=\"num\">%s</td></tr>"
        % (i + 1, e(x["name"]), CLASS_LABEL.get(x["class"], x["class"]), x["occurrences"], x["score"])
        for i, x in enumerate(entities[:limit]))
    return ('<div class="scroll"><table class="ent"><thead><tr><th>#</th><th>Entidad</th><th>Clase</th>'
            '<th class="num">Menciones</th><th class="num">Puntaje</th></tr></thead><tbody>%s</tbody></table></div>' % rows)


def facts_list(facts, limit=6):
    def slot(f, k, label):
        return '<span class="slot"><i>%s</i> %s</span>' % (label, e(f[k])) if k in f else ""
    items = "".join('<li>%s <b class="verb">%s</b>%s%s%s%s</li>' % (
        slot(f, "subject", "sujeto"), e(f["verb"]) + (" (pasiva)" if f["voice"] == "passive" else ""),
        slot(f, "od", "objeto"), slot(f, "oi", "a"), slot(f, "equative", "es"), slot(f, "regimen", "con"))
        for f in facts[:limit])
    return '<ul class="facts">%s</ul>' % items


# --- patch the report ----------------------------------------------------------------------------------------------
META_RE = re.compile(r'<p class="meta">\d+ palabras · \d+ oraciones · \d+ cláusulas · sentimiento \+[\d.]+ / −[\d.]+ · '
                     r'categorías: (?:(?!</p>).)*? · <a href=')
ENT_RE = re.compile(r'(<section><h4>Ranking de entidades</h4>).*?(</section>)', re.S)
FACTS_RE = re.compile(r'(<h4>Cómo se entendió: hechos principales</h4>)<ul class="facts">.*?</ul>', re.S)
# A row nests <details class="lead"> (add_leads.py) on an indented line; the row's own </details> starts a line
ROW_RE = re.compile(r'<details class="art" data-source="([^"]*)">.*?\n</details>', re.S)

parser = GenericArticleParser()
ok, skipped = 0, 0


def refresh(m):
    global ok, skipped
    row = m.group(0)
    if html.unescape(m.group(1)) != SOURCE:
        return row
    url = html.unescape(re.search(r'<a href="([^"]+)">nota original</a>', row).group(1))
    try:
        with quiet():
            entry = parser.parse(url, SOURCE)
        if entry is None:
            raise ValueError("no article text")
        if "entretenimiento" not in (entry.categories or []):
            entry.categories = list(entry.categories or []) + ["entretenimiento"]
        with quiet():
            entry.set_analisys_info()
        info = understand(entry)
    except Exception as ex:
        print("ERR", url, type(ex).__name__, str(ex)[:100])
        skipped += 1
        return row
    sent = info["sentiment"]
    meta = ('<p class="meta">%d palabras · %d oraciones · %d cláusulas · sentimiento +%s / −%s · categorías: %s · <a href='
            % (len(entry.content.split()), info["sentences"], info["clauses"], sent.get("positive", 0),
               abs(sent.get("negative", 0)), e(", ".join(entry.categories))))
    new = META_RE.sub(lambda _: meta, row, count=1)
    new = ENT_RE.sub(lambda x: x.group(1) + entity_table(info["entities"]) + x.group(2), new, count=1)
    new = FACTS_RE.sub(lambda x: x.group(1) + facts_list(info["facts"]), new, count=1)
    if new.count("<details") != row.count("<details"):
        raise RuntimeError("row structure changed for " + url)
    ok += 1
    print("ok %3d palabras  %-60s" % (len(entry.content.split()), entry.title[:60]), flush=True)
    return new


src = open(REPORT, encoding="utf-8").read()
src = ROW_RE.sub(refresh, src)
if ok:
    open(REPORT, "w", encoding="utf-8").write(src)
print("rows refreshed: %d, failed: %d" % (ok, skipped))

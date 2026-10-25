"""Add a collapsible fact map to each convergent story ("historia") in reports/farandula.html.

For every article in the story the original is fetched and analysed with Sentilecto; its facts are extracted the
same way as the report's "Cómo se entendió" (fact main/sub clauses with a subject and at least one other slot).
Facts from different sources are grouped when FactCompare.test_compare scores them >= SAME_FACT, and each fact
is tagged with the colour of every source that states it.

Run from prototype/ with a `config` file present:  python ../reports/fact_map.py ../reports/farandula.html
"""
import contextlib
import html
import io
import os
import re
import sys

sys.path.insert(0, os.getcwd())

from src.model.sentilecto import Sentilecto
from src.utils.fact_compare import FactCompare

import requests
from bs4 import BeautifulSoup

REPORT = sys.argv[1]
SAME_FACT = 0.75
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
quiet = lambda: contextlib.redirect_stdout(io.StringIO())
compare = FactCompare()


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


def lexical(entity):
    """lexical_form is a method on most entities but a plain str attribute on some (e.g. implicit ones)."""
    form = entity.lexical_form
    return str(form() if callable(form) else form).replace("_", " ")


def facts_of(text):
    with quiet():
        analysis = Sentilecto.analyze(text)
    facts = []
    for clause in analysis["paragraph"].clauses():
        if not clause.voice or not clause.verb or not clause.is_fact():
            continue
        slots = {}
        for structure in clause.syntactic_structures:
            if structure.name in ("subject", "od", "oi", "equative", "regimen") and structure.all_entities():
                slots[structure.name] = ", ".join(lexical(e) for e in structure.all_entities())
        if "subject" in slots and len(slots) > 1:
            with quiet():
                data = compare.extract_comparable_data(clause)
            facts.append({"verb": clause.verb.lemma() + (" (pasiva)" if clause.voice == "passive" else ""),
                          "slots": slots, "data": data})
    return facts


SLOT_LABEL = {"subject": "sujeto", "od": "objeto", "oi": "a", "equative": "es", "regimen": "rég."}


def render_fact(fact):
    parts = ['<span class="slot"><i>%s</i> %s</span>' % (SLOT_LABEL[k], html.escape(v)) for k, v in fact["slots"].items() if k == "subject"]
    parts.append('<b class="verb">%s</b>' % html.escape(fact["verb"]))
    parts += ['<span class="slot"><i>%s</i> %s</span>' % (SLOT_LABEL[k], html.escape(v)) for k, v in fact["slots"].items() if k != "subject"]
    return " ".join(parts)


def fact_map(articles):
    """articles: [(source, css_class, url)] -> HTML for the collapsible map."""
    facts = []
    for source, css, url in articles:
        for f in facts_of(article_text(url)):
            facts.append({**f, "source": source, "css": css})

    # Group facts across *different* sources (union-find on FactCompare matches)
    parent = list(range(len(facts)))
    find = lambda i: i if parent[i] == i else find(parent[i])
    for i in range(len(facts)):
        for j in range(i + 1, len(facts)):
            if facts[i]["source"] != facts[j]["source"]:
                with quiet():
                    score = compare.test_compare(facts[i]["data"], facts[j]["data"])
                if score >= SAME_FACT:
                    parent[find(j)] = find(i)
    groups = {}
    for i in range(len(facts)):
        groups.setdefault(find(i), []).append(facts[i])

    sources = list(dict.fromkeys((s, c) for s, c, _ in articles))
    shared = [g for g in groups.values() if len({f["source"] for f in g}) > 1]
    only = {s: [g for g in groups.values() if {f["source"] for f in g} == {s}] for s, _ in sources}

    def item(group):
        dots = "".join('<span class="dot %s" title="%s"></span>' % (c, html.escape(s))
                       for s, c in dict.fromkeys((f["source"], f["css"]) for f in group))
        lines = "".join('<li class="fx %s">%s<small> · %s</small></li>' % (f["css"], render_fact(f), html.escape(f["source"]))
                        for f in group)
        return '<li class="fgroup"><span class="dots">%s</span><ul>%s</ul></li>' % (dots, lines)

    tally = "".join('<li><span class="src %s">%s</span> %d hechos · %d solo de esta fuente</li>'
                    % (c, html.escape(s), sum(f["source"] == s for f in facts), len(only[s])) for s, c in sources)
    body = ['<ul class="ftally">%s<li><b>%d</b> hechos compartidos entre fuentes</li></ul>' % (tally, len(shared))]
    if shared:
        body.append('<h4>Compartidos</h4><ul class="fmap">%s</ul>' % "".join(item(g) for g in shared))
    for s, c in sources:
        if only[s]:
            body.append('<h4>Solo en <span class="src %s">%s</span></h4><ul class="fmap">%s</ul>'
                        % (c, html.escape(s), "".join(item(g) for g in only[s])))
    return ('<details class="factmap"><summary>Mapa de hechos por fuente <small>(%d hechos, %d compartidos)</small></summary>'
            '<div class="fbody">%s<p class="meta">Mismo hecho = FactCompare.test_compare ≥ %.2f entre notas de fuentes distintas.</p></div></details>'
            % (len(facts), len(shared), "".join(body), SAME_FACT))


CSS = """.factmap { margin-top: 14px; border: 1px solid var(--line); border-radius: 8px; }
.factmap > summary { cursor: pointer; padding: 10px 14px; font-weight: 600; }
.factmap > summary small { color: var(--muted); font-weight: 400; }
.factmap .fbody { padding: 0 14px 14px; }
.ftally { list-style: none; padding: 0; margin: 4px 0 8px; display: grid; gap: 6px; }
.fmap { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.fgroup { display: flex; gap: 8px; align-items: flex-start; }
.fgroup ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 4px; min-width: 0; }
.dots { display: flex; gap: 3px; padding-top: 6px; flex: none; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.s0 { background: var(--s0); } .dot.s1 { background: var(--s1); } .dot.s2 { background: var(--s2); } .dot.s3 { background: var(--s3); } .dot.s4 { background: var(--s4); }
.fx { border-left: 4px solid; padding: 2px 8px; overflow-wrap: anywhere; }
.fx small { color: var(--muted); }
li.fx.s0 { border-color: var(--s0); } li.fx.s1 { border-color: var(--s1); } li.fx.s2 { border-color: var(--s2); } li.fx.s3 { border-color: var(--s3); } li.fx.s4 { border-color: var(--s4); }
"""

if __name__ == "__main__":
    src = open(REPORT, encoding="utf-8").read()
    if 'class="factmap"' in src:
        sys.exit("fact maps already present")
    src = src.replace("</style>", CSS + "</style>", 1)  # only written out if at least one map is built
    story_re = re.compile(r'(<article class="story".*?<ol class="arts">(.*?)</ol>.*?)(</article>)', re.S)
    done = 0

    def add(m):
        global done
        arts = re.findall(r'<span class="src (s\d)">(.*?)</span><a href="([^"]+)"', m.group(2))
        articles = [(html.unescape(s), c, html.unescape(u)) for c, s, u in arts]
        try:
            block = fact_map(articles)
        except Exception as e:
            print("ERR", articles[0][2] if articles else "?", type(e).__name__, str(e)[:100])
            return m.group(0)
        done += 1
        return m.group(1) + block + "\n" + m.group(3)

    src = story_re.sub(add, src)
    if not done:
        sys.exit("no fact maps built; report left unchanged")
    open(REPORT, "w", encoding="utf-8").write(src)
    print("stories with fact map:", done)

# TecnoNews

TecnoNews (also known internally as NaturalNews / Sentilecto) is an automated news pipeline for Spanish-language content. It crawls RSS feeds from news sites, analyzes each article linguistically, rewrites and enriches it, and publishes the result to WordPress blogs.

## How it works

Each running instance loops forever, once a minute:

1. **Health check** — verifies the spaCy model and the language identifier work.
2. **Crawl** — reads the feeds assigned to the instance from MongoDB, downloads new articles and extracts title, content and tags with a site-specific parser. Articles already seen, duplicates and unwanted sections/tags are discarded.
3. **Relate** — finds other outlets' coverage of the same story and older background stories ("raconto").
4. **Analyze** — parses the text locally with spaCy (converted to FreeLing-style parse trees, see below) and builds a linguistic model (paragraphs, sentences, clauses, syntax, entities, referents, anaphora, sentiment).
5. **Rewrite** — applies paraphrasing strategies (active/passive voice, tense changes, direct/indirect quotes, synonyms, clause reordering, …) and injects generated content: Wikipedia information, paragraphs from other coverage, background, entity tables, countries and sentiment.
6. **Publish** — if content was injected and the result is at least 300 characters long, posts it to the WordPress blog chosen for its category via XML-RPC.
7. **Store** — saves every processed article to MongoDB, published or not.

## Repository layout

| Path | Contents |
|---|---|
| `prototype/src/sentinews/` | Pipeline driver (`tecnonews.py`), crawler, rewriter, categorizer, WordPress publisher |
| `prototype/src/sentinews/parsers/` | One parser per news site |
| `prototype/src/nlp/` | NLU engine: spaCy analysis converted to FreeLing-style parse trees |
| `prototype/src/model/`, `src/ling/` | Linguistic model built from those parse trees |
| `prototype/src/rewrite/` | Rewriting engine and its strategies |
| `prototype/src/services/mongodb/` | MongoDB access (feeds, news entries, hosts) |
| `prototype/src/utils/` | Parser and language identification clients, text similarity, summarization, sanitizing, logging, configuration |
| `prototype/instance_config/` | One configuration file per instance/environment |
| `prototype/publishing/` | Category → WordPress host mappings and category priorities |
| `prototype/resources/`, `resources-fl/` | Lexical resources (synonyms, stopwords, demonyms, FreeLing data, …) |
| `prototype/tests/` | Linguistic, pipeline and per-parser tests |
| `prototype/webapp/` | web.py demo interface |
| `prototype/api-server/` | Flask REST API (entity extraction, sentiment, rewriting, summarizing, …) |
| `runners/` | Scripts to start/stop production instances |
| `externals/` | Old FreeLing client binaries (no longer used) and auxiliary visualization projects |

## Requirements

- Python 3.11 with the packages in `requirements.txt` (includes spaCy 3.8 and its Spanish model `es_core_news_md`)
- System libraries for the image handling: cairo (SVG to PNG) and ImageMagick (Wand)
- MongoDB
- WordPress blogs with XML-RPC enabled (for publishing)

```bash
python3.11 -m venv .
source bin/activate
pip install -r requirements.txt
pip install --no-deps -r requirements-nodeps.txt   # flask-restful-swagger, see the file
```

Set `[wikipedia] user_agent` in the instance configuration to a User-Agent with contact information:
Wikimedia throttles generic clients (see `prototype/src/utils/wikipediaClient.py`).

## Running

Everything runs from `prototype/`, which must be on `PYTHONPATH`. The configuration is always read from a file named `config` in that directory, so copy the instance configuration you want first:

```bash
cd prototype
mkdir -p logs
export PYTHONPATH=$PYTHONPATH:`pwd`
cp instance_config/config_instance_dev config
python src/sentinews/tecnonews.py
```

`runners/runDev.sh` and `runners/runTest.sh` do the same. For production, `runners/run_all_instances.sh` / `runners/instances.sh start|stop|restart` launch several instances, each with its own configuration (feeds, database and publishing targets). These scripts assume the repository lives in `~/NaturalNews-merge` or `~/NaturalNews`.

Logs are written to `prototype/logs/instance-<id>-*.log`.

### Configuration

An instance configuration file contains, among others:

- `[instance] id` — instance name, used in log file names
- `[news_sources] feeds_to_process` — comma-separated feed ids to crawl
- `[spacy] model` — spaCy pipeline used for the analysis (`es_core_news_md`)
- `[mongodb]` — host, port and database
- `[publishing]` — category/host mapping files and default category
- `[resources]` — paths to lexical resources (`freeling_dict` and `locutions` are also used by the NLU engine)

### NLU engine

The analysis used to be done by a remote FreeLing (Sentilecto) server. It now runs locally with spaCy, in `prototype/src/nlp/`:

- `spacy_engine.py` loads the model named in `[spacy] model` once per process.
- `freeling_tree.py` turns spaCy's dependency parse into the FreeLing full-parse tree format (`grup-verb`, `verb-pass`, `sn`, `grup-sp`, `subord`, `subord-rel`, `patons`, `coor-n`…, with EAGLES tags on the words), which is what `src/parser/freelingTreeParser.py` and the whole linguistic model and rewriting strategies expect. Dates become FreeLing `W` words (`[??:3/5/2015:??.??:??]`), named entities and multiwords are joined with `_`, `del`/`al` are split.
- `lexicon.py` uses FreeLing's own dictionary and multiword list (`resources/freeling_es.dic`, `resources/locucions_extended.dat`) so lemmas, tags and multiwords match what FreeLing produced.
- Language identification (`src/utils/languageDetectorClient.py`) uses `langdetect`; spaCy has none.

The Spanish word lists in `freeling_tree.py` (dates, contractions, clitics, periphrases) assume Spanish text; the Portuguese API endpoints would need a Portuguese model and those lists adapted.

## Adding a news source

See `prototype/docs/parsers.md` (Spanish). In short:

1. Create `prototype/src/sentinews/parsers/<site>_parser.py` with a class extending `GenericParser` whose `parse(url)` returns a `NewsEntry`.
2. Insert the feed into the MongoDB `feeds` collection:
   ```js
   db.feeds.insert({"id": "elpais", "url": ["http://ep00.epimg.net/rss/tags/ultimas_noticias.xml"],
                    "parser": "elpais_parser.ElPaisParser", "default_tags": null,
                    "lastupdated": ISODate("2015-01-26T14:31:11.531Z")})
   ```
   `url` must be an array, `parser` is `module.Class`, and `id` must be unique.
3. Add the id to `feeds_to_process` in the instance configuration.
4. Add a test under `prototype/tests/Tecnonews/crawling_parsers/` — parsers break whenever a site changes its HTML.

## Tests

Tests are `unittest` scripts run directly from `prototype/` (a `config` file must exist; most tests contact live sites and MongoDB):

```bash
cd prototype
./run_test tests/Tecnonews/crawling_parsers/cnn_parser_test.py   # one file
./run_tests                                                     # all tests/*.py → test_results.log
```

For an end-to-end publishing test against a test blog, see `prototype/docs/test_integral.md`.

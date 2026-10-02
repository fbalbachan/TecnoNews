# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TecnoNews (a.k.a. NaturalNews / Sentilecto) is a **Python 3.11** pipeline (ported from Python 2.7) that crawls Spanish-language news feeds, analyzes each article linguistically (spaCy, converted locally to FreeLing-style parse trees), rewrites it (syntactic paraphrasing + injected content), and publishes the result to WordPress blogs over XML-RPC. Code, comments, docs and logs are a mix of Spanish and English. Dependencies are pinned in `requirements.txt` (plus `requirements-nodeps.txt`, installed with `--no-deps`: flask-restful-swagger's stale Jinja2<3 pin conflicts with spaCy).

Python 2 behaviours the port deliberately keeps (don't "fix" them without checking callers): `Gender`/`Number`/`Animity` are `StrEnum`s because under the old `enum==0.4.4` package their members were plain strings; `TextDistance.cosine` returns `1 - nltk.cosine_distance` because nltk 2 returned the similarity; `SentenceSplitter` has no zero-width delimiter because Python < 3.7 ignored empty matches in `re.split`; its `re.split(..., re.U)` passes `re.U` as maxsplit, as it always did. Text is `str` everywhere (the old code shuttled utf-8 bytes); files are opened with `encoding="utf-8"`. Scripts run from their own directory (`api-server/`, `webapp/`, `tests/`) use absolute sibling imports, not relative ones.

## Running

All Python code lives under `prototype/` and is imported as `src.…`, so **the working directory must be `prototype/`** and `PYTHONPATH` must include it. Several things depend on that cwd:

- `ConfigProvider` (`src/utils/configProvider.py`, a singleton) always reads a file literally named `config` in the cwd. That file is gitignored; the runners create it by copying one of `prototype/instance_config/config_instance_*`.
- Loggers write to `logs/instance-<id>-*.log` relative to cwd (`src/utils/logger_utils.py`), so `prototype/logs/` must exist.
- Resource paths in the config (`resources/...`, `publishing/...`) are relative to `prototype/`.

Run one pipeline instance (loops forever: health-check spaCy + language identifier → crawl → process → sleep 60s):

```bash
cd prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
cp instance_config/config_instance_test config   # or _dev, _0.._6, etc.
python src/sentinews/tecnonews.py
```

`runners/runDev.sh` / `runners/runTest.sh` do exactly this. `runners/run<N>.sh`, `run_all_instances.sh`, `instances.sh` and `tecnonews-service.sh` are production launchers that hard-code `~/NaturalNews-merge` / `~/NaturalNews` and a virtualenv in the repo root; multiple instances run concurrently, each with its own config (different `[news_sources] feeds_to_process`, Mongo DB, and publishing targets). Because every instance overwrites the same `prototype/config` before starting, launchers sleep between starts.

Other entry points: `prototype/webapp/` (web.py demo UI, `webapp.sh start|stop|restart`) and `prototype/api-server/` (Flask-RESTful API, `run_webapi_*.sh`).

## Tests

Tests are plain `unittest` scripts run as files (no pytest), from `prototype/`:

```bash
cd prototype
./run_test tests/Tecnonews/crawling_parsers/cnn_parser_test.py   # single file (rt is a symlink to run_test)
./run_tests            # runs tests/*.py, collects <test_output> XML into test_results.log
./alexis_run_tests     # same, but prints output directly
```

`run_tests` only covers top-level `tests/*.py` (linguistic tests built on `tests/base_test.py`, which emits XML pass/fail blocks). `tests/Tecnonews/` (pipeline) and `tests/Tecnonews/crawling_parsers/` (per-site parsers) must be run individually. Most tests are integration tests that hit live websites and MongoDB as configured in `config`, so a `config` file must be present and those services reachable. Linguistic tests need the spaCy model from `[spacy] model` installed; `tests/input/trees/` holds old FreeLing outputs (file name = sha1 of the sentence) that can be compared with the new trees.

## Architecture

Pipeline driver: `src/sentinews/tecnonews.py` (`TecnoNews.run` / `_process`).

1. **Feeds** — `NewsCrawler` (`src/sentinews/news_crawler.py`) reads feed definitions from the Mongo `feeds` collection (seeded with a hard-coded list on first run if empty) and keeps only the ids listed in config `[news_sources] feeds_to_process`.
2. **Crawling/parsing** — `Crawler.crawl` (`src/sentinews/crawler.py`) fetches the RSS with `feedparser`, skips URLs already in Mongo and unwanted sections, then instantiates the parser by `eval`-ing the feed's `parser` string (`"<module>.<Class>"`, e.g. `"cnn_parser.CNNParser"`) — this works because `src/sentinews/parsers/__init__.py` exports every module in the folder via glob and `crawler.py` does `from src.sentinews.parsers import *`. Parsers subclass `GenericParser` and return a `NewsEntry`(title, content, url, tags…). Entries whose tags match `resources/tags_to_filter` are dropped.
3. **Adding a source** (see `prototype/docs/parsers.md`): drop `<site>_parser.py` into `src/sentinews/parsers/`, then insert a document into Mongo `feeds` (`url` must be a JSON array, `parser` = `module.Class`, unique `id`, optional `default_tags`) and add the id to an instance config's `feeds_to_process`. Add a matching test under `tests/Tecnonews/crawling_parsers/` — site HTML changes are the most common breakage.
4. **Analysis & enrichment** — for each entry: related coverage from other sources (`RelatedNewsEntries`, `RacontoFinder` in `src/utils/`), then `NewsRewriter` (`src/sentinews/news_rewriter.py`) builds the linguistic model in `src/model/` (paragraph → sentence → clause/syntax/entity/referent/anaphora). Each sentence is parsed by `SpacyClientParser` (`src/utils/spacyClientParser.py`), which returns the exact text format the old remote FreeLing server printed; `src/parser/freelingTreeParser.py` reads it. The conversion lives in `src/nlp/`: `freeling_tree.py` maps the spaCy dependency parse to FreeLing chunk labels (`grup-verb`, `verb-pass`, `sn`, `grup-sp`, `sp-de`, `subord`, `subord-rel`, `subord-ger`, `patons`, `morfema-verbal`, `coor-n`/`coor-vb`, `F-no-c`/`Fc`/`F-term`…) and `lexicon.py` picks EAGLES tags/lemmas and multiwords from FreeLing's dictionary and locutions in `resources/`. The model code depends on those labels and on details such as quote marks being siblings of the cited clause, a sentence starting with `"` having an `F-no-c` root, and dates being `W` leaves under a `data` node — change the converter, not the model, when adapting the analysis. Language identification is `src/utils/languageDetectorClient.py` (`langdetect`).
5. **Rewriting** — `GlobalRewriter` / `Rewriter` (`src/rewrite/`) apply transformation strategies from `src/rewrite/strategy/` (voice passive, tense swaps, cite direct↔indirect, synonyms, clause dislocation, etc.). `TextInserter` then injects generated content (Wikipedia info, paragraphs from other coverage, raconto/background).
6. **Publish gate** — `TecnoNews.valid_to_publish`: requires `injected_count > 0` and ≥300 characters of rewritten text.
7. **Publishing** — `BlogPublisher` (`src/sentinews/blog_publisher.py`) chooses the target WordPress host/category using `publishing/*.json` (paths from config `[publishing]`) and posts via `python-wordpress-xmlrpc`.
8. Every entry is saved to MongoDB (`src/services/mongodb/`, `MongoConnector` singleton) whether published or not.

`externals/` holds the old FreeLing client binaries (unused since the spaCy migration) plus separate, mostly independent projects (PHP/JS visualization `infovis`, `topic_cloud`, `custom-graph-generation`, `sentituit_ui`).

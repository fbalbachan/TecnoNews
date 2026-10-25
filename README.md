# TecnoNews

TecnoNews (also known internally as NaturalNews / Sentilecto) is an automated news pipeline for Spanish-language content. It crawls RSS feeds from news sites, analyzes each article linguistically, rewrites and enriches it, and publishes the result to WordPress blogs.

## How it works

Each running instance loops forever, once a minute:

1. **Health check** — verifies the FreeLing language-identification and parsing servers respond.
2. **Crawl** — reads the feeds assigned to the instance from MongoDB, downloads new articles and extracts title, content and tags with a site-specific parser. Articles already seen, duplicates and unwanted sections/tags are discarded.
3. **Relate** — finds other outlets' coverage of the same story and older background stories ("raconto").
4. **Analyze** — sends the text to FreeLing and builds a linguistic model (paragraphs, sentences, clauses, syntax, entities, referents, anaphora, sentiment).
5. **Rewrite** — applies paraphrasing strategies (active/passive voice, tense changes, direct/indirect quotes, synonyms, clause reordering, …) and injects generated content: Wikipedia information, paragraphs from other coverage, background, entity tables, countries and sentiment.
6. **Publish** — if content was injected and the result is at least 300 characters long, posts it to the WordPress blog chosen for its category via XML-RPC.
7. **Store** — saves every processed article to MongoDB, published or not.

## Repository layout

| Path | Contents |
|---|---|
| `prototype/src/sentinews/` | Pipeline driver (`tecnonews.py`), crawler, rewriter, categorizer, WordPress publisher |
| `prototype/src/sentinews/parsers/` | One parser per news site |
| `prototype/src/model/`, `src/ling/` | Linguistic model built from FreeLing output |
| `prototype/src/rewrite/` | Rewriting engine and its strategies |
| `prototype/src/services/mongodb/` | MongoDB access (feeds, news entries, hosts) |
| `prototype/src/utils/` | FreeLing clients, text similarity, summarization, sanitizing, logging, configuration |
| `prototype/instance_config/` | One configuration file per instance/environment |
| `prototype/publishing/` | Category → WordPress host mappings and category priorities |
| `prototype/resources/`, `resources-fl/` | Lexical resources (synonyms, stopwords, demonyms, FreeLing data, …) |
| `prototype/tests/` | Linguistic, pipeline and per-parser tests |
| `prototype/webapp/` | web.py demo interface |
| `prototype/api-server/` | Flask REST API (entity extraction, sentiment, rewriting, summarizing, …) |
| `runners/` | Scripts to start/stop production instances |
| `externals/` | FreeLing client binaries and auxiliary visualization projects |

## Requirements

- Python 3.11 with the packages in `requirements.txt`
- A reachable FreeLing server (parser and language identification)
- MongoDB
- WordPress blogs with XML-RPC enabled (for publishing)

```bash
virtualenv -p python3.11 .
source bin/activate
pip install -r requirements.txt
```

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
- `[freeling]`, `[freeling_language]` — FreeLing host, ports and client binary
- `[mongodb]` — host, port and database
- `[publishing]` — category/host mapping files and default category
- `[resources]` — paths to lexical resources

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

Tests are `unittest` scripts run directly from `prototype/` (a `config` file must exist; most tests contact live sites, FreeLing and MongoDB):

```bash
cd prototype
./run_test tests/Tecnonews/crawling_parsers/cnn_parser_test.py   # one file
./run_tests                                                     # all tests/*.py → test_results.log
```

For an end-to-end publishing test against a test blog, see `prototype/docs/test_integral.md`.

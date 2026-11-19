# Agentic RAG local setup

## Hybrid retrieval experiment

Run `python scripts/ingestion.py --query "Why do chunks overlap?"` to load,
chunk, embed, and search the sample corpus using dense search, BM25, and RRF.
Use `--documents PATH` to select another corpus. Blank queries and empty corpora
are rejected. Unreadable documents stop the run with their path; AGENTS.md files
are excluded. BM25 contributes only chunks with matching query tokens.

Importing the module does not load the embedding model. Model creation happens
only when running the command. Each run still rebuilds embeddings and BM25 in
memory; PostgreSQL persistence and incremental ingestion are not implemented.
Chunks carry content/source/position hashes as metadata, but printed numeric IDs
remain positions local to one run. Repeated identical inputs retain hash IDs;
editing a document may change them and will require stale-record cleanup when
persistence is added.

Results are ranked candidates, not verified answers. An unrelated query may
still receive dense results; no unvalidated relevance threshold is imposed.
Before embedding, chunks are checked against the model token limit so oversized
inputs fail clearly instead of being silently truncated.

Run regression checks with `python -m unittest scripts.test_ingestion`.

Python 3.11 virtual environment: `.venv`.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`requirements.txt` lists the core packages. `requirements.lock.txt`, when present,
records the installed versions; use it instead for a repeatable installation.
The vector store is PostgreSQL with pgvector; `psycopg[binary]` supplies the Python driver.

## Local database

Start Docker Desktop with its Linux container engine. The initial setup creates
an ignored `.env` containing a generated local database password. On a new checkout,
copy `.env.example` to `.env` and replace its password before starting.

```powershell
docker compose up -d --wait
docker compose ps
docker compose exec -T postgres psql -U rag -d rag -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

Connect to `127.0.0.1:5432`, database `rag`, user `rag`, with the password from
`.env`. The connection URI is `postgresql://rag:<password>@127.0.0.1:5432/rag`.
If port 5432 is occupied, change `POSTGRES_PORT` in `.env`.
Compose reads `.env` automatically; Python applications must load it explicitly
or receive these variables through their environment.

The official [pgvector image](https://github.com/pgvector/pgvector) includes the
extension files. `docker/postgres/init.sql` enables `vector` when the data volume
is first initialized. For a preexisting database volume, enable it manually:

```powershell
docker compose exec -T postgres psql -U rag -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Data persists in the `postgres_data` named volume. `docker compose down` stops
the database and retains its data. Changing credentials in `.env` after initial
database creation does not change the stored database credentials.

## Package checks

```powershell
python -m pip check
python -c "import langchain, langgraph, fastapi, uvicorn, pgvector, psycopg, sentence_transformers, ragas; print('Core imports OK')"
```

Embedding models are downloaded separately when first loaded. Ragas evaluations
may require a configured model provider and its API credentials.

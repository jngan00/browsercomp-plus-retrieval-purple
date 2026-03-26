# BrowseComp-Plus Retrieval Purple Agent

BM25 retrieval agent for the BrowseComp-Plus benchmark.

This service receives a plain-text search query over A2A and returns the top-k matching documents from a Lucene BM25 index.

## What It Does

For each incoming A2A message, the retrieval agent:

1. Treats the message text as a search query
2. Runs BM25 search with Pyserini over the local Lucene index
3. Returns both:
   - a text summary with ranked hits
   - structured JSON data under `results`

The default result count is `5`.

## Architecture

```text
Purple research agent
  → plain-text query → Retrieval Purple
    → BM25 / Pyserini search over mounted index
    → ranked documents returned to caller
```

## Project Structure

```text
src/
├─ server.py      # A2A server
├─ executor.py    # A2A request handling
└─ agent.py       # BM25 retrieval logic
Dockerfile
pyproject.toml
```

## Request And Response

Input:

- A plain-text A2A message containing the search query

Output artifact:

- `TextPart`: human-readable ranked summary
- `DataPart`: JSON payload of the form

```json
{
  "results": [
    {
      "docid": "123",
      "score": 12.34,
      "text": "document contents"
    }
  ]
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BM25_INDEX_PATH` | No | Path to the Lucene BM25 index. Defaults to `/data/indexes/bm25` |
| `DEFAULT_K` | No | Number of hits to return. Defaults to `5` |

## Data Requirements

This agent expects a Lucene BM25 index to exist at `BM25_INDEX_PATH`. The current Dockerfile sets the default path to `/data/indexes/bm25`, and the Amber manifest uses that same path.

The retrieval service does not download the index at runtime. The index must already be present in the container filesystem or mounted into it by the surrounding deployment.

## Running Locally

```bash
uv sync
BM25_INDEX_PATH=/path/to/bm25 uv run src/server.py --host 0.0.0.0 --port 9009
```

Java is required because Pyserini depends on the Lucene/Anserini stack.

## Running With Docker

```bash
docker build -t browsecomp-plus-retrieval-purple .
docker run -p 9009:9009 \
  -e BM25_INDEX_PATH=/data/indexes/bm25 \
  -v /path/to/indexes:/data/indexes:ro \
  browsecomp-plus-retrieval-purple
```

## Amber Manifest

The current Amber manifest exposes one A2A endpoint and sets `BM25_INDEX_PATH` to `/data/indexes/bm25`. It does not use Amber's experimental Docker feature.

## Testing

```bash
uv sync --extra test
uv run pytest --agent-url http://localhost:9009
```

The tests cover A2A surface behavior only. They do not verify real BM25 search results unless you provide a valid index at runtime.

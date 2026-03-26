#!/bin/bash
set -euo pipefail

BM25_INDEX_PATH="${BM25_INDEX_PATH:-/data/indexes/bm25}"

echo "[entrypoint] Downloading BM25 index from HuggingFace..."
uv run python - <<'PYEOF'
import os
from huggingface_hub import snapshot_download

index_path = os.environ["BM25_INDEX_PATH"]
os.makedirs(index_path, exist_ok=True)

snapshot_download(
    repo_id="Tevatron/browsecomp-plus-indexes",
    repo_type="dataset",
    allow_patterns=["bm25/*"],
    local_dir=os.path.dirname(index_path),
)
print(f"[entrypoint] BM25 index downloaded to {index_path}")
PYEOF

exec uv run src/server.py "$@"

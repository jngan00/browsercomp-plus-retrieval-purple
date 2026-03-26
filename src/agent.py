"""
BM25 retrieval agent for BrowseComp-Plus.

Receives a search query as a plain-text A2A message and returns the top-k
matching documents from the BM25 index mounted at BM25_INDEX_PATH.
"""
import json
import os

from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Message, Part, TaskState, TextPart
from a2a.utils import get_message_text, new_agent_text_message

BM25_INDEX_PATH = os.environ.get("BM25_INDEX_PATH", "/data/indexes/bm25")
DEFAULT_K = int(os.environ.get("DEFAULT_K", "5"))


class Agent:
    def __init__(self) -> None:
        self._searcher = None

    def _get_searcher(self):
        if self._searcher is None:
            from pyserini.search.lucene import LuceneSearcher

            self._searcher = LuceneSearcher(BM25_INDEX_PATH)
        return self._searcher

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        query = get_message_text(message).strip()

        await updater.update_status(
            TaskState.working,
            new_agent_text_message(f"Searching: {query[:100]}..."),
        )

        results = _search(self._get_searcher(), query, DEFAULT_K)

        lines = [f"Found {len(results)} document(s) for query: {query[:80]}"]
        for i, r in enumerate(results, 1):
            lines.append(f"\n[{i}] docid={r['docid']}  score={r['score']:.4f}\n{r['text']}")
        summary = "\n".join(lines)

        await updater.add_artifact(
            parts=[
                Part(root=TextPart(text=summary)),
                Part(root=DataPart(data={"results": results})),
            ],
            name="SearchResults",
        )


def _search(searcher, query: str, k: int) -> list[dict]:
    try:
        hits = searcher.search(query, k)
        results = []
        for hit in hits:
            raw = json.loads(hit.lucene_document.get("raw"))
            results.append(
                {
                    "docid": hit.docid,
                    "score": float(hit.score),
                    "text": raw["contents"],
                }
            )
        return results
    except Exception as exc:
        print(f"[retrieval-purple] BM25 search failed: {exc}")
        return []

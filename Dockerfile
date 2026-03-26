FROM ghcr.io/astral-sh/uv:python3.13-trixie

# Install Java 21 (required by the bundled Anserini build in current Pyserini).
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

RUN adduser agent
RUN mkdir -p /data/indexes && chown -R agent:agent /data
USER agent
WORKDIR /home/agent

COPY pyproject.toml uv.lock README.md ./
COPY src src

RUN \
    --mount=type=cache,target=/home/agent/.cache/uv,uid=1000 \
    uv sync --locked

# Path where the corpus volume is mounted at runtime
ENV BM25_INDEX_PATH=/data/indexes/bm25
ENV DEFAULT_K=5

COPY entrypoint.sh ./
ENTRYPOINT ["./entrypoint.sh"]
CMD ["--host", "0.0.0.0"]
EXPOSE 9009

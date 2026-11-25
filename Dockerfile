FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY examples ./examples
COPY schemas ./schemas
COPY scripts ./scripts
COPY tests ./tests

RUN pip install --no-cache-dir .

ENTRYPOINT ["defi-arbitrage-core"]
CMD ["examples/market_snapshot.json"]

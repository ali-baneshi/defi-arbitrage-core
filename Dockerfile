FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples
COPY schemas ./schemas
COPY scripts ./scripts
COPY contracts ./contracts
COPY docs ./docs
COPY tests ./tests
COPY .env.example ./
COPY rust ./rust
COPY CHANGELOG.md CONTRIBUTING.md SECURITY.md RELEASE.md LICENSE ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["defi-arbitrage-core"]
CMD ["examples/market_snapshot.json"]

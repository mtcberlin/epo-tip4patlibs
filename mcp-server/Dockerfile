# Production Dockerfile for deploying query-mcp to cloud (e.g. Azure Container Apps).
# Build and run from the HOST machine (not inside the dev container).
#
#   docker build -t query-mcp .
#   docker run -p 8080:8080 query-mcp
#
# Serves both SSE (/sse) and Streamable HTTP (/mcp) on port 8080.

FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/
COPY config/ config/
COPY data/ data/

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["query-mcp", "--http", "--port", "8080"]

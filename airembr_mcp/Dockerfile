# Build context is this repo's root (airembr/sdk):
#
#   docker build -f airembr_mcp/Dockerfile -t airembr-mcp:local /home/risto/PycharmProjects/dev/airembr/sdk
#
# airembr_sdk has no working standalone installable package at the repo root
# (the only setup script, airembr/sdk/_setup.py, is stale and packages the
# wrong directory under the wrong distribution name) — instead, exactly like
# the PyCharm source-root setup this dev environment already relies on, we
# put the whole airembr/sdk source tree on PYTHONPATH.

FROM python:3.11-slim-bookworm AS base

WORKDIR /app

COPY airembr_sdk/requirements.txt /tmp/airembr_sdk-requirements.txt
COPY airembr_mcp/requirements.txt /tmp/airembr_mcp-requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/airembr_sdk-requirements.txt \
    && pip install --no-cache-dir -r /tmp/airembr_mcp-requirements.txt

COPY airembr /app/sdk-src/airembr
COPY airembr_sdk /app/sdk-src/airembr_sdk
COPY airembr_mcp /app/sdk-src/airembr_mcp

ENV PYTHONPATH=/app/sdk-src
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8800

EXPOSE 8800

CMD ["python", "-m", "airembr_mcp.main"]

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "[1/3] Create Python venv..."
python3 -m venv "$ROOT_DIR/.venv"
source "$ROOT_DIR/.venv/bin/activate"

echo "[2/3] Install deps..."
pip install --upgrade pip
pip install -r "$ROOT_DIR/fastapi_service/requirements.txt"

echo "[3/3] Start FastAPI on :8000"
export DATABASE_URL=${DATABASE_URL:-"postgresql+psycopg://dify:dify@localhost:5432/difydb"}
export LLM_BASE_URL=${LLM_BASE_URL:-"http://localhost:11434/v1"}
export LLM_API_KEY=${LLM_API_KEY:-"ollama"}
export LLM_MODEL=${LLM_MODEL:-"deepseek-r1:7b"}
export OUTPUT_DIR="$ROOT_DIR/outputs"

uvicorn fastapi_service.app.main:app --host 0.0.0.0 --port 8000


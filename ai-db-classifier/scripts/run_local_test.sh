#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "[1/3] Building and starting stack..."
docker compose -f "$ROOT_DIR/docker-compose.yml" up -d --build

echo "[2/3] Waiting for schema service..."
for i in {1..60}; do
  if curl -sf http://localhost:8000/health >/dev/null; then
    break
  fi
  sleep 2
done

echo "[3/3] Running classify_and_export..."
curl -s -X POST http://localhost:8000/classify_and_export \
  -H 'Content-Type: application/json' \
  -d '{
    "database_url": "postgresql+psycopg://dify:dify@postgres:5432/difydb",
    "policy_text": "根据字段名识别PII、支付、凭证等，输出level与tags",
    "output_filename": "sample_db_classification.xlsx"
  }' | jq .

echo "Done. See outputs/ directory for Excel file."


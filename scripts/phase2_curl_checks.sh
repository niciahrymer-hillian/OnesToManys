#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"
EXPORT_FILE="${EXPORT_FILE:-$(mktemp -t ones-to-manys-export.XXXXXX.json)}"

cleanup() {
  rm -f "$EXPORT_FILE"
}

trap cleanup EXIT

echo "[1/6] Health check"
curl --silent --show-error --fail "$BASE_URL/" | python3 -c 'import json, sys; data = json.load(sys.stdin); assert "running" in data["message"].lower(); print(data["message"])'

echo "[2/6] Create manufacturer"
manufacturer_response=$(curl --silent --show-error --fail \
  -X POST "$BASE_URL/api/manufacturers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CurlMfg",
    "country": "USA",
    "founded_year": 2001,
    "headquarters_city": "Austin"
  }')
manufacturer_id=$(printf '%s' "$manufacturer_response" | python3 -c 'import json, sys; print(json.load(sys.stdin)["manufacturer_id"])')
printf 'manufacturer_id=%s\n' "$manufacturer_id"

echo "[3/6] Create nested product"
product_response=$(curl --silent --show-error --fail \
  -X POST "$BASE_URL/api/manufacturers/$manufacturer_id/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "CurlWidget",
    "category": "Demo",
    "price": 19.99,
    "stock_quantity": 7,
    "description": "Created from curl smoke test"
  }')
product_id=$(printf '%s' "$product_response" | python3 -c 'import json, sys; print(json.load(sys.stdin)["product_id"])')
printf 'product_id=%s\n' "$product_id"

echo "[4/6] Verify one-to-many route"
curl --silent --show-error --fail "$BASE_URL/api/manufacturers/$manufacturer_id/products" \
  | python3 -c 'import json, sys; data = json.load(sys.stdin); assert len(data) == 1; assert data[0]["product_name"] == "CurlWidget"; print("nested route ok")'

echo "[5/6] Export dataset to JSON"
curl --silent --show-error --fail "$BASE_URL/api/export/json" > "$EXPORT_FILE"
python3 -c 'import json, pathlib, sys; data = json.loads(pathlib.Path(sys.argv[1]).read_text()); assert "manufacturers" in data; print(f"exported_manufacturers={len(data["manufacturers"])}")' "$EXPORT_FILE"

echo "[6/6] Re-import exported JSON"
curl --silent --show-error --fail \
  -X POST "$BASE_URL/api/import/json" \
  -H "Content-Type: application/json" \
  --data-binary "@$EXPORT_FILE" \
  | python3 -c 'import json, sys; data = json.load(sys.stdin); assert data["manufacturer_count"] >= 1; assert data["product_count"] >= 1; print(f"imported_manufacturers={data["manufacturer_count"]}, imported_products={data["product_count"]}")'

echo "curl Phase 2 checks passed"
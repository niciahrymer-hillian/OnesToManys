#!/usr/bin/env bash

# [FILE] phase2_curl_checks_annotated_cp.sh
# [WHY] Runs the Phase 2 requirements through curl without relying on a GUI REST client.
# [EFFECT] Gives a repeatable black-box check for nested routes and JSON import/export.

set -euo pipefail

# [CONFIG] Target server can be overridden without editing the script.
BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"

# [CONFIG] Export path defaults to a temp file because the smoke test only needs transient storage.
EXPORT_FILE="${EXPORT_FILE:-$(mktemp -t ones-to-manys-export.XXXXXX.json)}"

# [FUNCTION] Remove the temporary export file when the script exits.
cleanup() {
  rm -f "$EXPORT_FILE"
}

trap cleanup EXIT

echo "[1/6] Health check"
# [ASSERT] Confirms the API is running before any stateful request is attempted.
curl --silent --show-error --fail "$BASE_URL/" | python3 -c 'import json, sys; data = json.load(sys.stdin); assert "running" in data["message"].lower(); print(data["message"])'

echo "[2/6] Create manufacturer"
# [WHY] A fresh parent record makes the script independent of whatever seed data already exists.
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
# [WHY] Uses the nested route so the one-to-many endpoint itself is part of the smoke test.
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
# [ASSERT] Confirms the nested GET route returns the product inside manufacturer scope.
curl --silent --show-error --fail "$BASE_URL/api/manufacturers/$manufacturer_id/products" \
  | python3 -c 'import json, sys; data = json.load(sys.stdin); assert len(data) == 1; assert data[0]["product_name"] == "CurlWidget"; print("nested route ok")'

echo "[5/6] Export dataset to JSON"
# [EFFECT] Produces the same JSON shape expected by the import endpoint.
curl --silent --show-error --fail "$BASE_URL/api/export/json" > "$EXPORT_FILE"
python3 -c 'import json, pathlib, sys; data = json.loads(pathlib.Path(sys.argv[1]).read_text()); assert "manufacturers" in data; print(f"exported_manufacturers={len(data["manufacturers"])}")' "$EXPORT_FILE"

echo "[6/6] Re-import exported JSON"
# [WHY] Import replaces the current dataset, so posting the exported file proves round-trip portability.
curl --silent --show-error --fail \
  -X POST "$BASE_URL/api/import/json" \
  -H "Content-Type: application/json" \
  --data-binary "@$EXPORT_FILE" \
  | python3 -c 'import json, sys; data = json.load(sys.stdin); assert data["manufacturer_count"] >= 1; assert data["product_count"] >= 1; print(f"imported_manufacturers={data["manufacturer_count"]}, imported_products={data["product_count"]}")'

echo "curl Phase 2 checks passed"
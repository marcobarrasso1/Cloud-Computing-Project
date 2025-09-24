#!/usr/bin/env bash
set -euo pipefail

# --- CONFIG ---
USER="locust_user0"                  
PASS='test_password1234!'            
BASE_URL="http://localhost:8080"
DAV_BASE="${BASE_URL}/remote.php/dav/files/${USER}"
TEST_DIR="sizebench"

OUT="size_times.csv"
DATA_DIR="test_files"

# Ordered labels and their sizes in BYTES (parallel arrays)
labels=( "1KB"  "512KB"   "2MB"     "8MB"      "32MB"       "128MB" )
bytes=(  1024   524288    2097152   8388608    33554432     134217728 )

mkdir -p "$DATA_DIR"

echo "Generating test files in ${DATA_DIR}/ ..."
for i in "${!labels[@]}"; do
  sz="${bytes[$i]}"
  f="${DATA_DIR}/test_${sz}B"
  [[ -f "$f" ]] || dd if=/dev/zero of="$f" bs=1 count="$sz" status=none
done

echo "Preparing remote dir: ${DAV_BASE}/${TEST_DIR}"
# Create once; ignore error if it already exists
curl --silent --show-error -u "${USER}:${PASS}" -X MKCOL "${DAV_BASE}/${TEST_DIR}" -o /dev/null || true

# CSV header
echo "size_label,size_bytes,op,time_s,code" > "$OUT"

# One upload + one download per size
for i in "${!labels[@]}"; do
  label="${labels[$i]}"
  sz="${bytes[$i]}"
  local_path="${DATA_DIR}/test_${sz}B"
  remote_path="${DAV_BASE}/${TEST_DIR}/${label}.bin"

  echo "=== ${label} (${sz} B) ==="

  # Upload timing
  up_time=$(curl --silent --show-error \
    -u "${USER}:${PASS}" \
    --output /dev/null \
    --write-out '%{time_total}' \
    --request PUT --upload-file "${local_path}" \
    "${remote_path}")
  up_code=$(curl -s -o /dev/null -w '%{http_code}' -u "${USER}:${PASS}" -I "${remote_path}")
  echo "${label},${sz},upload,${up_time},${up_code}" >> "$OUT"
  echo " upload: ${up_time}s (HTTP ${up_code})"

  # Download timing
  dl_time=$(curl --silent --show-error \
    -u "${USER}:${PASS}" \
    --output /dev/null \
    --write-out '%{time_total}' \
    "${remote_path}")
  dl_code=$(curl -s -o /dev/null -w '%{http_code}' -u "${USER}:${PASS}" -I "${remote_path}")
  echo "${label},${sz},download,${dl_time},${dl_code}" >> "$OUT"
  echo " download: ${dl_time}s (HTTP ${dl_code})"
done

echo "Done. Wrote ${OUT}"


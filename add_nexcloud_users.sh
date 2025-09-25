#!/usr/bin/env bash
set -euo pipefail

SERVICE="${SERVICE:-nextcloud}"    
COUNT="${COUNT:-30}"
PREFIX="${PREFIX:-locust_user}"
PASS="${PASS:-test_password1234!}"
DISPLAY_PREFIX="${DISPLAY_PREFIX:-Locust}"

echo "Creating ${COUNT} users: ${PREFIX}0..$((COUNT-1)) on service '${SERVICE}'"
for i in $(seq 0 $((COUNT-1))); do
  USER="${PREFIX}${i}"
  DISPLAY="${DISPLAY_PREFIX} ${i}"
  docker compose exec -T -u www-data "${SERVICE}" bash -lc \
    "OC_PASS='${PASS}' php occ user:add --password-from-env --display-name='${DISPLAY}' '${USER}'" \
    && echo " ✓ created ${USER}" || echo " ! skipped ${USER} (exists?)"
done
echo "Done."

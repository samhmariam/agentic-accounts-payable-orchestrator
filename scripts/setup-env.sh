#!/usr/bin/env bash
set -euo pipefail

TRACK="${1:-core}"
OUTPUTS_FILE="${2:-}"

if [[ "$TRACK" != "core" && "$TRACK" != "full" ]]; then
  echo "Track must be 'core' or 'full'." >&2
  exit 1
fi

if [[ -z "$OUTPUTS_FILE" ]]; then
  OUTPUTS_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.day0/${TRACK}.json"
fi

if [[ ! -f "$OUTPUTS_FILE" ]]; then
  echo "Day 0 state file not found: $OUTPUTS_FILE. Run scripts/provision-$TRACK.ps1 first." >&2
  exit 1
fi

if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
  echo "Python is required to load the Day 0 environment into bash." >&2
  exit 1
fi

PYTHON_BIN="$(command -v python || command -v python3)"

echo "Loading Day 0 environment for track '$TRACK' from $OUTPUTS_FILE"

eval "$(
  "$PYTHON_BIN" - "$OUTPUTS_FILE" "$TRACK" <<'PY'
import json
import shlex
import sys

outputs_file, track = sys.argv[1], sys.argv[2]

with open(outputs_file, "r", encoding="utf-8") as f:
    state = json.load(f)

if not state.get("environment"):
    raise SystemExit(f"Day 0 state file is missing the 'environment' object: {outputs_file}")

required = [
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_RESOURCE_GROUP",
    "AZURE_LOCATION",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_CHAT_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "AZURE_STORAGE_ACCOUNT_URL",
    "AZURE_STORAGE_CONTAINER",
]

if track == "full":
    required.extend(
        [
            "AZURE_POSTGRES_HOST",
            "AZURE_POSTGRES_PORT",
            "AZURE_POSTGRES_DB",
            "AZURE_POSTGRES_USER",
            "AZURE_KEY_VAULT_URI",
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
        ]
    )

env = state["environment"]
for key in required:
    value = env.get(key, "")
    if not str(value).strip():
        raise SystemExit(f"Missing required value for {key} in the Day 0 state file.")

for key, value in env.items():
    if value is None:
        continue
    text = str(value)
    if text.strip():
        print(f"export {key}={shlex.quote(text)}")
PY
)"

echo "Done. Azure auth still comes from az login or DefaultAzureCredential environment variables."

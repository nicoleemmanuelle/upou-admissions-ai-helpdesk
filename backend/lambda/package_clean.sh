#!/usr/bin/env bash
set -euo pipefail

# Create a clean Lambda deployment package containing only the project's
# python source files and prompt.txt (no installed site-packages).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Create the lambda.zip in the backend/lambda directory (no dependencies)
TARGET_ZIP="$SCRIPT_DIR/lambda.zip"

echo "Creating clean lambda.zip at $TARGET_ZIP (no dependencies)"

rm -f "$TARGET_ZIP"

pushd "$SCRIPT_DIR" >/dev/null
  zip -r9 "$TARGET_ZIP" handler.py openai_service.py s3_retriever.py prompt.txt >/dev/null
popd >/dev/null

echo "Clean lambda.zip created at $TARGET_ZIP"

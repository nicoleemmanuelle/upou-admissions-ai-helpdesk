#!/usr/bin/env bash
set -euo pipefail

# Create a clean Lambda deployment package containing only the project's
# python source files and prompt.txt (no installed site-packages).
# The produced zip is written to infrastructure/terraform/lambda.zip

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# terraform directory is two levels up from backend/lambda
TF_DIR="$(cd "$SCRIPT_DIR/../../infrastructure/terraform" && pwd)"

echo "Creating clean lambda.zip (no dependencies)"


mkdir -p "$TF_DIR"
rm -f "$TF_DIR/lambda.zip"

pushd "$SCRIPT_DIR" >/dev/null
  zip -r9 "$TF_DIR/lambda.zip" handler.py openai_service.py s3_retriever.py prompt.txt >/dev/null
popd >/dev/null

echo "Clean lambda.zip created at $TF_DIR/lambda.zip"

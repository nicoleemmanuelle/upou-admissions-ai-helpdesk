#!/usr/bin/env bash
set -euo pipefail

# Build a deployment package (lambda.zip) for the Python Lambda in this folder.
#
# Usage:
#   ./build_lambda.sh            -> build using local Python (installs deps into build/)
#   ./build_lambda.sh --docker   -> build inside lambci/lambda:build-python3.11 (recommended for compatibility)
#   ./build_lambda.sh --dry-run  -> skip installing Python deps, only package local source files (safe quick check)
#
# The produced archive is placed at ../../infrastructure/terraform/lambda.zip (where Terraform expects it).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TF_DIR="$ROOT_DIR/../infrastructure/terraform"
BUILD_DIR="$SCRIPT_DIR/build"
ZIP_PATH="$TF_DIR/lambda.zip"

USE_DOCKER=0
DRY_RUN=0

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --docker) USE_DOCKER=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) echo "Usage: $0 [--docker] [--dry-run]"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

echo "Building lambda package (dry-run=$DRY_RUN, docker=$USE_DOCKER)"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

if [[ "$DRY_RUN" -eq 0 ]]; then
  if [[ "$USE_DOCKER" -eq 1 ]]; then
    echo "Building dependencies inside Docker (lambci/lambda:build-python3.11). This requires Docker installed and running."
    docker run --rm -v "$SCRIPT_DIR":/var/task -w /var/task lambci/lambda:build-python3.11 /bin/sh -c '
      pip install -r requirements.txt -t build && exit'
  else
    echo "Installing dependencies locally into $BUILD_DIR (may produce platform-specific wheels)."
    # Use system python3 by default
    python3 -m venv "$SCRIPT_DIR/.venv" || true
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.venv/bin/activate" || true
    pip install --upgrade pip >/dev/null
    pip install -r "$SCRIPT_DIR/requirements.txt" -t "$BUILD_DIR"
    deactivate || true
  fi
else
  echo "Dry-run: skipping pip installs. Only packaging local source files."
fi

# Copy our lambda source files into the build directory (handler and helpers)
cp "$SCRIPT_DIR/handler.py" "$BUILD_DIR/" || true
cp "$SCRIPT_DIR/openai_service.py" "$BUILD_DIR/" || true
cp "$SCRIPT_DIR/s3_retriever.py" "$BUILD_DIR/" || true
cp "$SCRIPT_DIR/prompt.txt" "$BUILD_DIR/" || true

# Make sure terraform target directory exists
mkdir -p "$TF_DIR"

pushd "$BUILD_DIR" >/dev/null
  echo "Creating zip at $ZIP_PATH"
  # Zip contents so files are at the root of the archive
  zip -r9 "$ZIP_PATH" . >/dev/null
popd >/dev/null

echo "Lambda package created: $ZIP_PATH"

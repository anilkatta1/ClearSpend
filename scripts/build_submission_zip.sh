#!/usr/bin/env bash
set -euo pipefail

role_name="${1:-Anil_Katta}"
role_file="ROLE_EVIDENCE_${role_name}.md"
archive_dir="dist"
archive_path="${archive_dir}/ClearSpend-${role_name}.zip"

if [[ ! -f "${role_file}" ]]; then
  echo "Missing required role evidence: ${role_file}" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree must be clean so the ZIP exactly matches a reviewed commit." >&2
  exit 1
fi

mkdir -p "${archive_dir}"
git archive --format=zip --prefix=ClearSpend/ --output="${archive_path}" HEAD
unzip -tq "${archive_path}" >/dev/null

if unzip -Z1 "${archive_path}" | grep -Eq '(^|/)(node_modules|\.next|\.venv|venv|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache)(/|$)'; then
  echo "Archive contains a forbidden environment, dependency, or cache path." >&2
  exit 1
fi

if unzip -Z1 "${archive_path}" | grep -E '(^|/)\.env($|\.)' | grep -Ev '(^|/)\.env\.example$'; then
  echo "Archive contains a forbidden .env file." >&2
  exit 1
fi

uncompressed_bytes="$(unzip -l "${archive_path}" | awk 'END {print $1}')"
limit_bytes=$((500 * 1024 * 1024))
if (( uncompressed_bytes >= limit_bytes )); then
  echo "Archive exceeds the 500 MB uncompressed limit: ${uncompressed_bytes} bytes" >&2
  exit 1
fi

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${archive_path}"
fi

echo "Created ${archive_path}"
echo "Uncompressed bytes: ${uncompressed_bytes}"

#!/bin/bash
# SessionStart hook for the ai-news-video workflow.
# Restores everything the pipeline needs that does NOT survive an ephemeral
# Claude Code on the web container: ffmpeg/ffprobe (render + assemble), bc
# (duration math in scripts/assemble.sh), jq (JSON body in scripts/voiceover.sh),
# and the Higgsfield CLI skills (payloads are gitignored; restored from skills-lock.json).
#
# Web-only and idempotent — safe to run on every session start.
set -euo pipefail

# Only run inside Claude Code on the web; do nothing in a local terminal.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Keep hook stdout clean (SessionStart stdout is fed into context); send tool
# chatter to stderr and surface only a short status line.
{
  export DEBIAN_FRONTEND=noninteractive

  # System tools. apt-get update can exit non-zero on unrelated third-party PPAs,
  # so tolerate it; the install itself pulls from the Ubuntu archive.
  if ! command -v ffmpeg >/dev/null 2>&1 \
     || ! command -v ffprobe >/dev/null 2>&1 \
     || ! command -v bc >/dev/null 2>&1 \
     || ! command -v jq >/dev/null 2>&1; then
    apt-get update || true
    apt-get install -y ffmpeg bc jq
  fi

  # Restore the Higgsfield skills pinned in skills-lock.json.
  if [ -f "$CLAUDE_PROJECT_DIR/skills-lock.json" ]; then
    (cd "$CLAUDE_PROJECT_DIR" && npx --yes skills add higgsfield-ai/skills)
  fi
} >&2

echo "ai-news-video env ready: ffmpeg $(ffmpeg -version 2>/dev/null | head -n1 | awk '{print $3}'), bc/jq present, Higgsfield skills restored."

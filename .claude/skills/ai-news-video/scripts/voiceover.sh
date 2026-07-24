#!/usr/bin/env bash
# voiceover.sh — generate an MP3 voiceover in Andy's ElevenLabs voice.
#
# Usage:  scripts/voiceover.sh <script.txt> <out.mp3>
# Needs:  ELEVENLABS_API_KEY   (export in your shell or a .env)
#         ELEVENLABS_VOICE_ID  (your cloned voice's ID from the ElevenLabs dashboard)
# Optional: ELEVENLABS_MODEL_ID (default: eleven_multilingual_v2)
#
# Get the voice ID: ElevenLabs dashboard -> Voices -> your clone -> "ID" / "Copy voice ID".

set -euo pipefail

SCRIPT_TXT="${1:?Usage: voiceover.sh <script.txt> <out.mp3>}"
OUT_MP3="${2:?Usage: voiceover.sh <script.txt> <out.mp3>}"
MODEL_ID="${ELEVENLABS_MODEL_ID:-eleven_multilingual_v2}"

: "${ELEVENLABS_API_KEY:?Set ELEVENLABS_API_KEY}"
: "${ELEVENLABS_VOICE_ID:?Set ELEVENLABS_VOICE_ID}"

[ -f "$SCRIPT_TXT" ] || { echo "Script file not found: $SCRIPT_TXT" >&2; exit 1; }

# Build a JSON body safely (jq handles quoting/escaping of the script text).
BODY="$(jq -n \
  --rawfile text "$SCRIPT_TXT" \
  --arg model "$MODEL_ID" \
  '{
     text: $text,
     model_id: $model,
     voice_settings: { stability: 0.5, similarity_boost: 0.8, style: 0.0, use_speaker_boost: true }
   }')"

echo "Generating voiceover with voice ${ELEVENLABS_VOICE_ID} (${MODEL_ID})..." >&2

HTTP_CODE="$(curl -sS -w '%{http_code}' -o "$OUT_MP3" \
  -X POST "https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}?output_format=mp3_44100_128" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: audio/mpeg" \
  -d "$BODY")"

if [ "$HTTP_CODE" != "200" ]; then
  echo "ElevenLabs request failed (HTTP $HTTP_CODE). Response:" >&2
  cat "$OUT_MP3" >&2 || true
  rm -f "$OUT_MP3"
  exit 1
fi

echo "Voiceover saved: $OUT_MP3" >&2

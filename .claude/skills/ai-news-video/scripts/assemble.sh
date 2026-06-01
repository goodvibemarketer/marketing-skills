#!/usr/bin/env bash
# assemble.sh — stitch a finished video from a working directory.
#
# Usage:  scripts/assemble.sh <workdir>
#
# Expects inside <workdir>:
#   voiceover.mp3        (required)  the spine — final length follows this
#   clips/               (optional)  *.mp4 cutaways + your real screen captures, in filename order
#   captions.srt         (optional)  burned-in subtitles
#   intro.mp4 outro.mp4  (optional)  channel bookends
# Produces:
#   final.mp4
#
# Notes:
#   - Clips are normalised to 1920x1080 / 30fps and looped in order to cover the voiceover length,
#     then the video is trimmed to exactly the voiceover length.
#   - This is the leg most likely to need hand-tuning. If a cut feels wrong, assemble in your editor
#     instead — everything upstream still saved you the time.

set -euo pipefail

WORK="${1:?Usage: assemble.sh <workdir>}"
VO="$WORK/voiceover.mp3"
CLIPS_DIR="$WORK/clips"
SRT="$WORK/captions.srt"
INTRO="$WORK/intro.mp4"
OUTRO="$WORK/outro.mp4"
OUT="$WORK/final.mp4"

W=1920; H=1080; FPS=30
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

[ -f "$VO" ] || { echo "Missing voiceover: $VO" >&2; exit 1; }

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VO")"
echo "Voiceover length: ${DUR}s" >&2

norm() {  # normalise any clip to the common spec (video only)
  ffmpeg -y -v error -i "$1" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},setsar=1" \
    -an -c:v libx264 -preset veryfast -pix_fmt yuv420p "$2"
}

# 1. Collect + normalise body clips (or make a fallback background if none exist).
CONCAT="$TMP/concat.txt"; : > "$CONCAT"
i=0
shopt -s nullglob
CLIP_FILES=()
[ -d "$CLIPS_DIR" ] && CLIP_FILES=("$CLIPS_DIR"/*.mp4 "$CLIPS_DIR"/*.mov)
shopt -u nullglob

if [ "${#CLIP_FILES[@]}" -eq 0 ]; then
  echo "No clips found — using a plain background so the pipeline still completes." >&2
  ffmpeg -y -v error -f lavfi -i "color=c=#141413:s=${W}x${H}:r=${FPS}:d=${DUR}" \
    -c:v libx264 -preset veryfast -pix_fmt yuv420p "$TMP/body.mp4"
else
  NORMED=()
  for f in "${CLIP_FILES[@]}"; do
    out="$TMP/n_$(printf '%03d' "$i").mp4"; norm "$f" "$out"; NORMED+=("$out"); i=$((i+1))
  done
  # Loop the normalised clips in order until total length >= voiceover length.
  total=0; j=0
  while (( $(echo "$total < $DUR" | bc -l) )); do
    clip="${NORMED[$((j % ${#NORMED[@]}))]}"
    echo "file '$clip'" >> "$CONCAT"
    clen="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")"
    total="$(echo "$total + $clen" | bc -l)"; j=$((j+1))
  done
  ffmpeg -y -v error -f concat -safe 0 -i "$CONCAT" -c:v libx264 -preset veryfast -pix_fmt yuv420p "$TMP/body_full.mp4"
  # Trim to exact voiceover length.
  ffmpeg -y -v error -i "$TMP/body_full.mp4" -t "$DUR" -c:v libx264 -preset veryfast -pix_fmt yuv420p "$TMP/body.mp4"
fi

# 2. Mux the voiceover onto the body. Burn captions here if present.
if [ -f "$SRT" ]; then
  echo "Burning captions from $SRT" >&2
  ffmpeg -y -v error -i "$TMP/body.mp4" -i "$VO" \
    -vf "subtitles=${SRT}:force_style='Fontsize=22,PrimaryColour=&Hffffff&,Outline=2,Shadow=0'" \
    -map 0:v:0 -map 1:a:0 -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$TMP/core.mp4"
else
  ffmpeg -y -v error -i "$TMP/body.mp4" -i "$VO" \
    -map 0:v:0 -map 1:a:0 -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$TMP/core.mp4"
fi

# 3. Bookend with intro/outro if present (normalise them to match, give them silent audio tracks).
SEGMENTS=()
add_bookend() {
  local src="$1" tag="$2"
  ffmpeg -y -v error -i "$src" \
    -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -map 0:v:0 -map 1:a:0 \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},setsar=1" \
    -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$TMP/$tag.mp4"
}

FINAL_CONCAT="$TMP/final_concat.txt"; : > "$FINAL_CONCAT"
[ -f "$INTRO" ] && { add_bookend "$INTRO" intro; echo "file '$TMP/intro.mp4'" >> "$FINAL_CONCAT"; }
echo "file '$TMP/core.mp4'" >> "$FINAL_CONCAT"
[ -f "$OUTRO" ] && { add_bookend "$OUTRO" outro; echo "file '$TMP/outro.mp4'" >> "$FINAL_CONCAT"; }

if [ "$(wc -l < "$FINAL_CONCAT")" -gt 1 ]; then
  ffmpeg -y -v error -f concat -safe 0 -i "$FINAL_CONCAT" -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k "$OUT"
else
  cp "$TMP/core.mp4" "$OUT"
fi

echo "Done: $OUT" >&2

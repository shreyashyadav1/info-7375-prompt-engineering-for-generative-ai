#!/usr/bin/env bash
# build.sh: rebuild the four-part ClaimCheck film from its sources.
# Usage: ./build.sh /path/to/brutalist.art   (run inside an activated venv with the toolkit's requirements)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ART_HOME="$(cd "${1:?usage: ./build.sh /path/to/brutalist.art}" && pwd)"
SLUG="$(basename "$HERE")"
cd "$HERE"
python3 make_sheet.py
(cd .. && python3 "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" "$SLUG")
ffmpeg -v error -y -i mp3/beat-BOUT.mp3 -af "apad=pad_dur=1.0" -c:a libmp3lame -b:a 192k mp3/_p.mp3
mv mp3/_p.mp3 mp3/beat-BOUT.mp3
python3 sync_durations.py
python3 build_scenes.py "$ART_HOME"
python3 "$ART_HOME/runtime/qc/factcheck_check.py" .
(cd .. && "$ART_HOME/art" run "$SLUG" --height 2160)
(cd .. && "$ART_HOME/art" final "$SLUG" --height 2160 --out "$SLUG/exports/landscape")

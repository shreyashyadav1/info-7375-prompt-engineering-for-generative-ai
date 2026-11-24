#!/usr/bin/env python3
"""sync_durations.py: write each beat's measured mp3 duration back into beat_sheet.json.

Run after generate_audio_kokoro.py, after padding BOUT, and after any re-run of make_sheet.py
(which rebuilds the sheet without durations). The audio is the clock: never type a duration by hand.
Card beats also get props.durationSeconds, which ShowTellCard sizes itself from.
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sheet_path = HERE / "beat_sheet.json"
sheet = json.loads(sheet_path.read_text())
for b in sheet["beats"]:
    mp3 = HERE / "mp3" / f"beat-{b['beat_id']}.mp3"
    if not mp3.exists():
        raise SystemExit(f"missing {mp3}: generate audio first")
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", str(mp3)]).decode().strip())
    b["actual_duration_s"] = round(d, 3)
    b["audio_file"] = f"mp3/beat-{b['beat_id']}.mp3"
    props = (b.get("shot", {}).get("remotion") or {}).get("props")
    if isinstance(props, dict) and b.get("lane") in ("card", "bookend"):
        props["durationSeconds"] = round(d + float(b.get("lead_silence_s", 0) or 0), 3)
sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
total = sum(b["actual_duration_s"] + float(b.get("lead_silence_s", 0) or 0) for b in sheet["beats"])
print(f"{len(sheet['beats'])} beats, {total:.1f} s total")

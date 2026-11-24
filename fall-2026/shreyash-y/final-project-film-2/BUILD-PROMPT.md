# BUILD-PROMPT: rebuild the four-part ClaimCheck film

## Environment

- Brutalist toolkit, fresh clone at commit `3a6d397` (2026-11-07):
  `git clone https://github.com/nikbearbrown/brutalist.art`
- Python 3.14 venv with the toolkit's `requirements.txt` (Manim 0.20, kokoro-onnx, faster-whisper),
  Node 24, ffmpeg 8. `./setup` reports every feature ready except Manim equation beats (no LaTeX; the
  film has no equations).
- Kokoro model files in `runtime/models/kokoro/` (`./setup --install` downloads them).
- Remotion renders used `ART_CHROME` pointing at a Chrome for Testing 149 headless shell
  (`runtime/remotion/node_modules/.remotion/chrome-headless-shell/...`).

## Commands (or run `./build.sh /path/to/brutalist.art`)

```bash
export ART_HOME=/path/to/brutalist.art
python3 make_sheet.py                                    # beat_sheet.json (narration + shots)
(cd .. && python3 $ART_HOME/runtime/scripts/generate_audio_kokoro.py <this-folder>)   # audio = the clock
ffmpeg -y -i mp3/beat-BOUT.mp3 -af apad=pad_dur=1.0 -c:a libmp3lame -b:a 192k mp3/_p.mp3 && mv mp3/_p.mp3 mp3/beat-BOUT.mp3
python3 sync_durations.py                                # measured durations back into the sheet
python3 build_scenes.py $ART_HOME                        # scenes.py = iso_kit + original props + scene_body.py
python3 $ART_HOME/runtime/qc/factcheck_check.py .        # Gate F, content half
(cd .. && $ART_HOME/art run <this-folder> --height 2160) # Gates A/B/V + review cut
(cd .. && $ART_HOME/art final <this-folder> --height 2160 --out <this-folder>/exports/landscape)   # GATE T + master
```

Note: re-running `make_sheet.py` wipes measured durations and build stamps; always follow it with
`sync_durations.py`, and re-run `art final` after a sheet change.

## Prompts used

This film was built in one Claude Code session on 2026-11-23. My request was the course brief
("What your project film needs to show": executive summary, what others have done, methods,
evaluation, in that order) plus the Brutalist repository link, with "use this". Claude asked three
questions, which I answered:

1. API key status: still no key; offline only.
2. Plan ClaimCheck as an agent loop in Methods: yes.
3. Success bar: no wrong answer gets through on the held-out set.

No image, video or music generation prompts were used (see PROMPTS.md).

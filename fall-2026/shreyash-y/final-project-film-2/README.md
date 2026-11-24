# Quote It or Refuse. Final Project Film (four-part cut)

- **Name:** Shreyash Yadav
- **Course:** INFO 7375, Prompt Engineering & Agentic AI, Fall 2026
- **Project:** ClaimCheck
- **Film:** `Yadav_Shreyash_INFO7375_FinalProjectFilm.mp4` (5:02, 302.1 s, 3840×2160, 24 fps), SHA-256 `05d97a07919c1e7d616f26d89722eac7180b633f71ba4924d78568004b189d53`
- **Made with:** [Brutalist](https://github.com/nikbearbrown/brutalist.art) (commit `3a6d397`), show-tell
  format, free local pipeline (Kokoro voice, Manim, Remotion, ffmpeg). The narration is a local AI voice
  (Kokoro `am_onyx`) reading my script; the first and last frames say so.
- **Narration approved:** I read the full script (`beat_sheet.json`) and approved it on 2026-11-23. After
  reviewing FACTCHECK.md I had three lines corrected to match the code: B01 and B07 now say ClaimCheck
  *should* refuse when the file has no answer (no answerer has shown that yet), and B09 says the checker
  needs at least half the answer's key words.

## What the film is about

ClaimCheck answers questions about an insurance claim file only with a word-for-word quote from the
file, checked by plain code before anyone sees it, and otherwise says "not in the documents".
The first piece already runs offline (one synthetic policy, ten frozen questions, the checker, a dated
report); the agent loop, the larger data set and the live Claude run are the plan. I have no Claude
API key yet, and the film says so.

## How the film is structured

The four parts the film guidance asks for, in order:

| Part | Time | Beats | What it covers |
|---|---|---|---|
| 1 · Executive summary | 0:00–0:52 | BIDEA–B03 | What ClaimCheck does and why it matters, including what citing the wrong clause costs (an excluded claim paid, or a covered claim denied, behind a quote that looks checked), with no "how" |
| 2 · What others have done | 0:52–2:00 | B04–B07 | AI search engines (51.5% of sentences fully supported), legal research tools (17–33% hallucinated), Claude's Citations feature (a real quote, not necessarily the right one); both studies side by side with the gap ClaimCheck addresses (B07A); why mine is still worth building |
| 3 · Methods | 2:00–3:55 | B08–B15 | What runs today, the answer contract and checker, the agent loop, read-only tools, the human gate, the data, the five steps, and what I have versus what is still unresolved (an API key and credits; a second question writer) |
| 4 · Evaluation | 3:55–4:57 | B16–B20 | The four grades, the baseline to beat (4 wrong answers reached the reader, all with real quotes), the pass bar in numbers (0 wrong answers, 100% of not-in-the-documents traps refused, 100% of answerable questions answered correctly), the failure I'll trigger on purpose, and the limit |

The detail behind Parts 2–4 is in [APPENDIX.md](APPENDIX.md).

## Files

| File | What it is |
|---|---|
| `Yadav_Shreyash_INFO7375_FinalProjectFilm.mp4` | the film (in the Canvas zip; video is kept out of GitHub) |
| `APPENDIX.md` | prior work with sources, method detail, resources and the cost estimate, evaluation targets |
| `beat_sheet.json` | narration and visual plan for all 25 beats, with measured audio durations |
| `make_sheet.py`, `sync_durations.py` | write the beat sheet; copy measured durations into it |
| `scene_body.py`, `build_scenes.py`, `scenes.py` | the drawn scenes; `scenes.py` is the assembled file the toolkit renders |
| `images/` | the five tool logos, copied from the toolkit |
| `evidence/` | ClaimCheck's tests and baseline re-run on 2026-11-23 (the film's only results) |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | the toolkit's Gate F paperwork |
| `SOURCES.md` | what I used, what I made, what Claude contributed, licences |
| `FRICTIONAL.md` | dated log of what went wrong and what changed |
| `BUILD-PROMPT.md`, `build.sh` | how to rebuild |
| `qc/` | gate reports for the final master |

## Rebuild

```bash
source /path/to/venv/bin/activate        # Python 3.14 with brutalist.art's requirements.txt
./build.sh /path/to/brutalist.art
```

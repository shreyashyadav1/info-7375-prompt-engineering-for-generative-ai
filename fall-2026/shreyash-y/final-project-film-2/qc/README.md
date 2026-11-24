# qc: gate reports for the final master (second cut with the 100% pass bar, 2026-11-23 evening)

| Gate | Result | File |
|---|---|---|
| Gate F (paperwork exists) | pass | `ART-RUN.log.txt` |
| Gate F, content (`factcheck_check.py`) | clean: 41 rows, every claim-bearing beat covered | `FACTCHECK-CHECK.txt` |
| Gate A (static pre-flight) | pass on every scene of the final `scenes.py` | `GATE-A-W-ALL-SCENES.txt`, `ART-RUN.log.txt` |
| Gate W (WCAG contrast, margins, text overlap) | pass on every scene | `GATE-A-W-ALL-SCENES.txt`, `ART-RUN.log.txt` |
| Layout audit (Manim) | 0 errors, 0 warnings | `LAYOUT-AUDIT.md`, `layout_audit.json` |
| Gate V (frame-level visual QC, 50 frames) | 0 blockers, 0 majors | `GATE-V-REPORT.md`, `gate-v-contact-sheet.png` |
| GATE T (type lock, all 25 beats) | PASS; one advisory: B16's narration reads the card aloud, which is the point of that beat (it reads the real report) | `GATE-T-TYPECHECK.md` |
| Bookend check (manual, not part of `art run`) | expected fail: wants the @NikBearBrown handle and ClaudeTitleOutro; a student film uses its own drawn outro | `BOOKEND-CHECK.txt` |
| Master | 3840×2160, 24 fps, H.264 + AAC 48 kHz stereo, 302.125 s, mean -27.0 dB, silent last second | `master.verified.json`, `ART-FINAL.log.txt` |

The second cut re-rendered only the seven beats that changed (B02, B02B, B07A, B07, B15, B18, B19),
and the switch to a 100% bar re-rendered B18 once more; `ART-RUN.log.txt` holds both runs. The other
beats' renders are the ones gated in the first cut (`ART-RUN-first-cut.log.txt`,
`ART-FINAL-first-cut.log.txt`). Gate V and GATE T above ran on the whole final master.

Earlier failures and their fixes (Gate V low contrast in B03/B14; GATE T in B01, B02, B06, B11, B15;
Gate A in B07A) are in `../FRICTIONAL.md`. A gate pass does not mean a viewer understands the film.

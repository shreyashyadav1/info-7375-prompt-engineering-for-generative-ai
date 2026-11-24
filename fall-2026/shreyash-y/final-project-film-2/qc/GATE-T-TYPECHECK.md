# TYPECHECK.md — GATE T

Reel: `yadav-shreyash-final-project-film`  |  Checked: 2026-11-23T23:09  |  Overall: PASS  |  Beats checked: 25  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

> **§8.10 REDUNDANCY (advisory — does not block cut):**
> Narration should DISCUSS on-screen text, not recite it.
> Exception: LITERAL beats (viewer types/copies/runs the text) are exempt.

> - §8.10 [B16] narration recites the card (1.00) — discuss it, don't read it

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BIDEA | bookend | light | min-size §8.1: min text-run height 83px >= floor 41px | PASS | — |
| B00 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B02B | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B07A | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 55px >= floor 41px | PASS | — |
| B09 | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| B10 | manim | light | min-size §8.1: min text-run height 92px >= floor 41px | PASS | — |
| B11 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B12 | manim | light | min-size §8.1: min text-run height 58px >= floor 41px | PASS | — |
| B13 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B14 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B15 | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| B16 | card | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B17 | manim | light | min-size §8.1: min text-run height 572px >= floor 41px | PASS | — |
| B18 | manim | light | min-size §8.1: min text-run height 72px >= floor 41px | PASS | — |
| B19 | manim | light | min-size §8.1: min text-run height 55px >= floor 41px | PASS | — |
| B20 | manim | light | min-size §8.1: min text-run height 52px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| BOUT | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 25 | 0 |
| overflow §8.2 | 25 | 0 |
| contrast §8.3 | 25 | 0 |
| contrast-local §8.3b | 25 | 0 |
| bbox-overlap §8.6b | 25 | 0 |
| card-clip §8.13 | 25 | 0 |
| kerning §8.4 | 23 | 0 |
| redundancy §8.10 (advisory) | 1 | 1 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*

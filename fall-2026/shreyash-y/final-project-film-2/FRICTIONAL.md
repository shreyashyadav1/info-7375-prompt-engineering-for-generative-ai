# FRICTIONAL.md: Final Project Film (four-part cut)

## 1. What changed and why (2026-11-23)

The course posted guidance for the project film: four parts in order (executive summary, what others
have done, methods, evaluation). My October pitch film followed the seven brief questions instead, so
it had no prior-work section with results and no evaluation targets. I re-cut it rather than patch it.

Since the pitch, the first piece of ClaimCheck exists (2026-10-25): one synthetic policy, ten frozen
questions, the checker, the grading and a dated report. That changed what I could say in past tense.
I re-ran the tests and the baseline on 2026-11-23 so the film's numbers are from that day: 17 tests
passed; baseline 5 correct, 0 caught, 1 missed, 4 wrong.

Decisions I made: say plainly that I still have no API key; plan ClaimCheck as an agent (one retry,
read-only tools, a three-call budget, an examiner who approves each answer), because the final
project requires a loop, tools, a stop condition and a human gate; and commit to the bar "no wrong
answer reaches the reader" on the held-out set.

## 2. Toolkit friction

- My October checkout of Brutalist (2026-09-20) had no show-tell skill, which classmates now use. I
  cloned the current toolkit (commit `3a6d397`) into a new folder instead of updating the old one, so
  the pitch film stays rebuildable, and made a new venv (Python 3.14, Manim 0.20). The old Manim 0.18
  venv would not match: the toolkit warns that 0.18 renders every scene one frame short.
- The voice model (about 340 MB) and the Chrome headless shell were copied from the October install
  instead of downloaded again.
- `ClaudeTitleOutro` has the @NikBearBrown handle built into the component, so, as in the pitch, the
  outro is a drawn card with my name and the AI-narration disclosure. `bookend_check.py` expects that
  handle and will flag the outro; that is expected.
- The `ShowTellCard` dashboard rounds its number (51.5% would show as 52), so the prior-work numbers
  are drawn in Manim instead; only B16, the real report, is a card.

## 3. Narration fixes (whisper transcript)

- "Anthropic gave Claude a citations feature" came out as "gave claw to"; and "In 2025, Anthropic"
  as "and Thoropic". Reworded to "Anthropic added a citations feature to Claude in 2025."
- "A permission list in code" fused into "listing code"; added commas.
- "the overridden clause" sounded like "overwritten"; changed to "the base clause an endorsement
  overrides", which is also clearer.
- My name was voiced "SHRAY-ash YAD-av"; added a pronunciation entry so it is closer.
- First draft defined "caught" as "when the checker blocks a wrong answer" and "missed" as "when it
  wrongly refuses". The grading code is narrower: CAUGHT only applies when the file has no answer, and
  MISSED covers any case where the answer existed but the reader got nothing. B16 was re-voiced to
  match the code.
- B03 called the rest of the film "the plan", but Part 2 is other people's work, not my plan; it now
  says the rest of the film "covers" the three parts. B10's "one retry, and then ClaimCheck refuses"
  could be heard as "always refuses after a retry"; it now says "If that fails too, ClaimCheck refuses."
- After the fact-check review: B01 "it says: not in the documents" became "it should say", and B07 "the
  tool refuses when the file is silent" became "the tool should refuse", because the baseline answered
  both not-in-the-documents questions and no answerer has shown the refusal yet. B09 "the answer's
  numbers and key words" became "at least half its key words", to match checker rule 5.

## 4. Drawing fixes (contact sheet before the 4K render)

- The binder floated above its shadow and the shadow drew over it; moved it and put it behind.
- Small answer slips had tiny squiggles that the type gate could read as unreadable text; made them blank.
- The stamp's mark landed on top of the page's lines; moved it to a clear corner.
- The GitHub logo rendered as a white disc (its SVG uses an even-odd fill); used the PNG instead.
- The outro failed Gate A ("shapes never change"); added a second accent.

## 5. Gate failures during the 4K render, and fixes

- Gate V, first review cut: low contrast in B03 and B14 (0.21 to 0.30 against a 0.30 floor). The pale
  "planned" crates and the rail were counted as content but sat too close to the background. Gave the
  planned crates card-white faces with grey outlines and the rail a darker grey; Gate V then had 0
  majors.
- GATE T, first `art final`: 5 failures. B01: the question slip was shrunk, leaving 35 px marks (floor
  41 px). B01, B02, B06: an ink page edge around handwriting lines read as two labels printed on top
  of each other. B11: handwriting 40 px tall. B15: the terracotta Claude Code mark read as accent text
  (2.74:1 contrast). Fixes: grey page edges, taller handwriting lines, the question slip leaves
  instead of shrinking, grey bars in the permission list, the Claude Code mark in ink. Re-rendered 14
  scenes; GATE T passed. One advisory stays: B16's narration reads the report card aloud, which is
  what that beat is for.
- The toolkit warned that Remotion 4.0.535 is behind 4.0.546; I kept the version the repository pins.
- `bookend_check.py` fails on the outro, as expected (it wants the @NikBearBrown handle).

## 6. Feedback on the first cut and changes in the second cut (2026-11-23)

After getting feedback on my first film, I found four things that needed improvement.

- Executive summary: My first film explained the problem but did not explain why it matters enough. I added an example of how using the wrong clause could lead to paying a claim that is not covered or rejecting a claim that should be covered.
- Prior work: I already had two research studies in my film, but they were shown separately. I added a scene showing both studies together, their results, and what my project is trying to solve.
- Methods: I wanted to make it clear what I already have and what I still need. I have the tools and a laptop to build the project, but I still need an API key with token credits. I also haven't found a second person to write some of the evaluation questions. I decided to keep both as unresolved instead of saying everything is ready.
- Evaluation: Claude suggested setting the correct-answer target at 80%. I chose 100% because every question has an expected answer. If the system misses even one answer, I want to know why it failed. My three targets are zero wrong answers, 100% of trap questions refused, and 100% of answerable questions answered correctly. This also stops the system from passing by refusing every question.

### Problems during the second cut

- Whisper did not understand some words correctly, especially "Claude's citations" and the sentence about the endorsement. These sentences were changed and tested again.
- Some check marks were hidden behind the answer slips. Their layer was changed to make them visible.
- Gate A failed because some shapes were detected outside the frame. Their positions were fixed.
- The longer evaluation label was too close to another panel, so the panel was moved to create more space.
- After the changes, Gate W passed on all seven changed scenes. Gate V showed no blockers or major issues across 50 frames. The layout audit showed zero errors, and Gate T passed all 25 beats.
- The final film is 5 minutes and 1 second long.

### What I learned

A citation can be real but still support the wrong answer. My baseline showed this when four wrong answers passed the checker. This helped me understand that checking the quote alone is not enough. I also need to compare the answer against the expected answer during evaluation.

I kept the missing resources and project limitations in the film because I don't want to claim that something is working when I haven't built or tested it yet.

## 7. Not checked / still open

- I have not watched either cut start to finish on a phone.
- Gate results for the final master are in `qc/`; a gate pass does not mean a viewer understands it.
- The cost estimate is arithmetic from list prices, not a measured run.
- I haven't found a second person to write some of the held-out questions yet. That has to be
  settled before step 2 freezes the held-out set.

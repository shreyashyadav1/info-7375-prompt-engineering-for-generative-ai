# SOURCES: Quote It or Refuse. (ClaimCheck final project film, four-part cut)

## Executive summary

What this film was made with, what I made, what Claude contributed, and the licence of every
third-party piece. There is no stock footage, no AI-generated image or video, and no real claim or
personal data. Every document drawn on screen is a stand-in for synthetic text written for this project.

## What I used

| Thing | What for | Licence / terms |
|---|---|---|
| Brutalist toolkit (`github.com/nikbearbrown/brutalist.art`, fresh clone at commit `3a6d397`, 2026-11-07) | pipeline: beat sheet, audio, render, QC gates; show-tell skill, its drawing kit and its approved original props | course toolkit, used as the assignment instructs; not modified (a local copy of its Chrome headless shell was reused from my October install) |
| Kokoro TTS v1.0 (`kokoro-v1.0.onnx`, voice `am_onyx`) via `kokoro-onnx` | narration, generated locally from my script | Apache-2.0 |
| Manim Community 0.20 | the 22 drawn scenes and the outro card (`scenes.py`) | MIT |
| Remotion 4.0.535 (toolkit `runtime/remotion`) | `BrutalistHesitantWriter` (opening) and `ShowTellCard` kind `focus` (B16) | Remotion licence: free for individuals |
| EB Garamond (bundled with the toolkit) | all type | SIL Open Font License 1.1 |
| Logos from the toolkit's `icons/logos/` (Claude, Anthropic, Python, Claude Code, GitHub) | B06, B10, B15, where the film names those tools (the toolkit's logo rule) | trademarks of their owners; used to identify the tools |
| faster-whisper `base.en` | transcribing the narration to catch mispronunciations (not shown in the film) | MIT |
| ffmpeg | audio padding and assembly (called by the toolkit) | LGPL/GPL |

No paid service and no API key were used to make the film. Nothing was uploaded.

## Prior work cited in Part 2

- Liu, N. F., Zhang, T., & Liang, P. (2023). Evaluating Verifiability in Generative Search Engines.
  Findings of EMNLP 2023, 7001-7025. https://aclanthology.org/2023.findings-emnlp.467/
- Magesh, V., Surani, F., Dahl, M., Suzgun, M., Manning, C. D., & Ho, D. E. (2024). Hallucination-Free?
  Assessing the Reliability of Leading AI Legal Research Tools. arXiv:2405.20362; Journal of Empirical
  Legal Studies 22(2), 216-242 (2025). https://arxiv.org/abs/2405.20362
- Anthropic. Citations (Claude API documentation and API release notes, January 23, 2025).
  https://platform.claude.com/docs/en/build-with-claude/citations
- Appendix only: Gao, T., Yen, H., Yu, J., & Chen, D. (2023). Enabling Large Language Models to
  Generate Text with Citations (ALCE). EMNLP 2023. https://arxiv.org/abs/2305.14627 ; LlamaIndex
  `CitationQueryEngine` documentation.

## What I made

- The project and every decision in it: ClaimCheck, the scope, what is out on purpose, the data
  boundary (synthetic only).
- ClaimCheck's first piece (2026-10-25): the synthetic policy, the ten frozen questions, the contract,
  the checker, the grading, the eval runner and its 17 tests. The film's only real results come from
  re-running that code on 2026-11-23 (`evidence/`).
- On 2026-11-23: that the project is still offline with no API key; that the methods plan the agent
  loop (retry once, read-only tools, three-call budget, examiner approval); and the success bar (no
  wrong answer reaches the reader on the held-out set, every trap refused, most answerable questions
  answered). After feedback on the first cut, I asked for four fixes, one of them a measurable pass
  bar, and set it at 100% (B18; APPENDIX.md C.3).

## What Claude contributed

In a Claude Code session on 2026-11-23 (model: Claude Opus 5.5):

- Read the course's four-part film brief, my pitch film, PROJECT-BRIEF.md and the ClaimCheck code, and
  proposed the four-part structure, the agent-loop design details (the two read-only tools, the
  three-call budget) and the success-bar wording, which I chose from options.
- Researched the prior work in Part 2 from primary sources, through a research sub-agent, and wrote
  FACTCHECK.md.
- Drafted the narration (`make_sheet.py`), wrote `scene_body.py` (all drawn scenes),
  `build_scenes.py`, `sync_durations.py`, `build.sh`, and drafted this file, APPENDIX.md, SHOTLIST.md,
  PROMPTS.md, README.md, BUILD-PROMPT.md and FRICTIONAL.md.
- Ran the toolkit (audio, renders, gates), read the frames and transcripts, and fixed what failed
  (logged in FRICTIONAL.md).
- After feedback on the first cut (same evening): added the consequence beat (B02B) and the
  side-by-side prior-work beat (B07A), split B15 into "have" and "unresolved", and proposed a numeric
  pass bar with 80% for the answerable questions; I chose 100% instead.
- No Claude response appears in the film: there has been no live Claude run of ClaimCheck yet.

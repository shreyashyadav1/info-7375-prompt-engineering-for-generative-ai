# Appendix: ClaimCheck, the detail behind the film

The film keeps the executive summary free of "how". The detail for Parts 2 to 4 is here.
Past tense is used only for what ran; everything else is the plan. Checked 2026-11-23.

---

## A. What other people have done (Part 2)

| Work | What they did | What they got | Where ClaimCheck differs |
|---|---|---|---|
| Liu, Zhang & Liang, "Evaluating Verifiability in Generative Search Engines", Findings of EMNLP 2023 ([ACL Anthology](https://aclanthology.org/2023.findings-emnlp.467/)) | Human audit of four AI search engines (Bing Chat, NeevaAI, perplexity.ai, YouChat), responses collected late February to late March 2023 | 51.5% of generated sentences fully supported by their citations; 74.5% of citations support the sentence they are attached to (averages over the four engines) | They measured after the fact. ClaimCheck checks each answer before anyone sees it |
| Magesh, Surani, Dahl, Suzgun, Manning & Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools", arXiv 2405.20362 (2024); Journal of Empirical Legal Studies 22(2):216-242 (2025) ([arXiv](https://arxiv.org/abs/2405.20362)) | 202 pre-registered legal queries against retrieval-based legal research tools and GPT-4, March to May 2024 | Hallucinated "between 17% and 33% of the time": Lexis+ AI 17%, Ask Practical Law AI 17% (with 63% incomplete answers), Westlaw AI-Assisted Research 33%; GPT-4 without documents 43%. The paper counts falsely claiming that a source supports a statement as a hallucination | Retrieval plus citation did not stop wrong answers. ClaimCheck adds a code check and grades against frozen gold answers |
| Anthropic, Citations for Claude (launched January 23, 2025; [docs](https://platform.claude.com/docs/en/build-with-claude/citations), [release notes](https://platform.claude.com/docs/en/release-notes/api)) | API feature: Claude returns `cited_text` spans with document index and character or page location | Docs: "citations are guaranteed to contain valid pointers to the provided documents". Anthropic reports up to 15% better recall accuracy than most custom implementations (internal evaluation, no method given); customer Endex reported source hallucinations and formatting issues falling from 10% to 0% (customer testimonial) | The guarantee is that a quote is real. The docs describe no check that the quote supports the answer, which is the case ClaimCheck grades |
| Gao, Yen, Yu & Chen, ALCE, "Enabling Large Language Models to Generate Text with Citations", EMNLP 2023 ([arXiv](https://arxiv.org/abs/2305.14627)) | Benchmark for model answers with citations, graded automatically with an NLI model | On ELI5, even the best models tested lacked complete citation support about half the time | Not in the film; same lesson as row 1 |
| LlamaIndex `CitationQueryEngine` ([docs](https://developers.llamaindex.ai/python/examples/query_engine/citation_query_engine/), source read 2026-11-23) | Prompts the model to answer from numbered sources and cite them | The engine returns the model's answer unchanged with the source chunks; nothing checks the cited text against the answer | ClaimCheck's checker is the missing step |
| What I tried myself (2026-10-07, from the pitch) | Uploading a policy PDF to a chat assistant; a LlamaIndex / LangChain RAG template | Fluent answers, citations not checked, no test set, no "not in the documents" rule | Same gap |

The gap, as the film puts it (B07A): both studies found cited answers that were wrong or unsupported,
and Claude's Citations feature guarantees that a quote is real, not that it is the right one. A cited
answer can still be wrong, so something has to catch it before a reader relies on it.

Why mine still matters: in the sources above, citing is common and checking is not. ClaimCheck puts a
deterministic check in the path of every answer, makes refusal a rule, and publishes a frozen
evaluation whose headline number is the wrong answers that still reached the reader.

Design note for later: Claude's Citations feature cannot be combined with structured JSON output
(`output_config.format`), which ClaimCheck's answerer uses today. Using Citations would mean parsing
the answer from text blocks instead; that trade-off is open.

---

## B. Methods (Part 3)

### B.1 What exists and ran

Built 2026-10-25; re-run 2026-11-23 in `evidence/claimcheck-rerun-2026-11-23/` (a copy, so the
submitted folder is untouched).

| Piece | File | Status |
|---|---|---|
| One synthetic homeowner policy (endorsement E-2 overrides exclusion 5(d)) | `data/policy_ho3_synthetic.md` | written by me |
| 10 questions with gold status, gold text and source; 4 traps (an override, 2 not-in-documents, an exception inside an exclusion) | `data/questions.jsonl` | frozen 2026-10-25 before any model run, sha256 `7f37bf6f52f08cb4…` in `data/FROZEN.md`; the eval refuses to run if it changes |
| Answer contract: `answer`, `quote`, `doc_id`, `status` (`answered` / `not_in_documents`), parse or reject | `claimcheck/contract.py` | runs |
| Citation checker, standard library only, version 0.1.0 | `claimcheck/checker.py` | runs |
| Grading against gold | `claimcheck/grading.py` | runs |
| Answerers: `baseline` (no model), `claude` (live, stops cleanly without a key), `recorded` (replay) | `claimcheck/answerers.py` | baseline runs; `claude` never called the API |
| Eval runner, writes a dated report, failures first | `claimcheck/eval.py` | runs |
| 17 offline tests | `tests/test_claimcheck.py` | `Ran 17 tests ... OK` on 2026-11-23 (`evidence/claimcheck-tests-2026-11-23.txt`) |

Commands: `python3 -m claimcheck.eval` and `python3 -m unittest discover -s tests -v`.

### B.2 The checker's rules

An `answered` reply is shown only if all hold: (1) `doc_id` names a document the answerer was given;
(2) the quote is at least 15 characters; (3) the quote appears in that document word for word
(whitespace and quote marks normalised); (4) every number in the answer appears in the quote;
(5) at least half of the answer's content words appear in the quote. A `not_in_documents` reply always
passes. Rules 4 and 5 are proxies for "the quote contains the answer" and can be fooled, which is why
grading against gold exists (C.2).

### B.3 The agent loop (planned)

- **Observe:** the question and the claim file's table of contents.
- **Decide:** Claude either calls a read-only tool or replies in the contract format.
- **Act:** run the tool and return its result, or pass the reply to the checker.
- **Record:** every model call, tool call and result, checker verdict, token counts and cost, in a
  per-run log that can be replayed with the `recorded` answerer.
- **Retry:** at most one, after a failed check, with the checker's reason appended.
- **Stop (decided in code, never by the model saying it is done):** a reply that passes the checker
  goes to the human gate; a `not_in_documents` reply goes to the gate as a refusal; a third model call
  without a passing reply ends as a refusal marked "budget exhausted".
- **Budget:** three model calls per question, counting tool turns and the retry.

### B.4 Tools and the permission policy (planned)

Two tools, both read-only: `search_file(query)` returns matching lines with document id and section;
`open_section(doc_id, section_id)` returns one section's text. An allowlist in code names exactly those
two; any other tool name, or any request to write, send or change anything, is refused and logged.
ClaimCheck never decides coverage, approves or denies a claim.

### B.5 The human gate (planned)

The examiner sees the question, the answer, the quote highlighted inside its section, and the checker's
verdict, and chooses approve, reject or send back. The decision is stored with a hash of exactly what
was on screen, so a later reviewer can see what the examiner saw.

### B.6 Data plan

- Synthetic only: no real claims, no customer data, no personal data (data boundary).
- Grow from one policy to a full claim file: policy, endorsement, claim form, adjuster notes.
- 30 to 50 questions, at least a third traps (override, not in the documents, exception inside an
  exclusion, number buried in a table); some written by someone other than me.
- Split into a tuning set and a held-out set; the held-out set is frozen with a sha256 before any
  prompt tuning and scored once.
- At least five deliberate failure cases, as the final project requires.

### B.7 Step by step

1. Get an API key; run `python3 -m claimcheck.eval --answerer claude` on the 10 frozen questions; save
   the raw replies so the run can be replayed offline. Done when a dated Claude report exists.
2. Grow the data and freeze the held-out set. Done when its hash is in `FROZEN.md`.
3. Build the loop, tools and gate, tests first. Done when tests for the budget, the allowlist and the
   gate pass before the model is wired in.
4. Tune prompts on the tuning set only; log every prompt change with its score change.
5. One scored run on the held-out set; a stranger runs the project from the README.

### B.8 Do I have what I need?

**Have (2026-11-23):**

| Resource | Status |
|---|---|
| Python 3, `anthropic` SDK | have (`.venv-claimcheck`) |
| Claude Code, GitHub | have |
| Compute | have: the model is hosted, so a laptop (Apple M3, 8 GB) is enough |
| The first piece: policy, 10 frozen questions, contract, checker, grading, eval runner, 17 tests | have; ran again 2026-11-23 (B.1) |

**Still unresolved:**

| Dependency | Status | Needed by |
|---|---|---|
| Claude API key and token credits | **unresolved**: no key yet | step 1 (the first live run) |
| A second person to write some of the held-out questions | **unresolved**: nobody found yet (2026-11-23) | step 2 (before the held-out set is frozen) |

Cost estimate (not measured; to be replaced by the usage the `claude` answerer records):
Claude Opus 5.5 lists at $4 per million input tokens and $20 per million output tokens, and thinking
is billed as output. Assumptions: about 1.5k input tokens per call (the policy is 3,156 characters,
about 0.8k tokens, plus the system prompt and the question) and up to 2k output tokens per call at
medium effort.

- One pass over 10 questions: 15k x $4/M + 20k x $20/M = $0.06 + $0.40 = about **$0.46**.
- Worst case with the three-call budget: 30 calls at up to 3k input and 2k output:
  90k x $4/M + 60k x $20/M = $0.36 + $1.20 = about **$1.56**.

So the film says "under two dollars". (The October README said "a few cents"; that left out thinking
tokens.)

---

## C. Evaluation (Part 4)

### C.1 Grades (from `claimcheck/grading.py`)

| Grade | Meaning |
|---|---|
| CORRECT | answered with the gold text in the quote, or correctly refused |
| CAUGHT | the file has no answer; the answerer answered anyway and the checker blocked it |
| MISSED | the gold answer exists but the reader got nothing (refused, blocked, or a broken reply) |
| WRONG | the reader saw an answer that is not the gold answer: the worst outcome |

### C.2 The bar to beat: the no-model baseline (2026-11-23, same as 2026-10-25)

CORRECT 5, CAUGHT 0, MISSED 1, WRONG 4. The baseline copies the document line that shares the most
words with the question, so every quote it gives is real. All four WRONG answers (Q03, Q06, Q08, Q09)
passed the checker: Q06 quoted exclusion 5(d) when endorsement E-2 overrides it, and Q08 and Q09
answered questions the file cannot answer. The checker makes an answer traceable; grading against
frozen gold is what catches a real quote from the wrong clause.

### C.3 What result means it worked: the pass bar

On the held-out set, all three must hold:

| # | Measure | Pass threshold |
|---|---|---|
| 1 | Wrong answers shown to the reader | **WRONG = 0**. A WRONG is judged on the quote (its gold text is missing), so this also means no wrong citation reaches the reader |
| 2 | Not-in-the-documents traps refused by the answerer | **100%**: each one graded CORRECT. A CAUGHT is reported but not counted as a pass, because the answerer should refuse without the checker's help |
| 3 | Answerable questions (gold status `answered`, including the override and exception traps) graded CORRECT | **100%** |

Together the three mean a perfect score: every held-out question graded CORRECT. Why 100%: every
question has a frozen gold answer in a file I control, so anything less is a failure I can name.
The cost is that one cautious refusal on an answerable question (a MISSED) fails the run. That is
deliberate: the report then shows which question was missed and why, instead of hiding it inside an
average. The no-model baseline gets 62.5% of the answerable questions.

How the bar reads on known cases:

| Case | WRONG | Traps refused | Answerable correct | Result |
|---|---|---|---|---|
| No-model baseline, 2026-11-23 (10 frozen questions) | 4 | 0 of 2 | 5 of 8 (62.5%) | fails all three |
| Refuse everything (derived from `grading.py`) | 0 | 2 of 2 | 0 of 8 | passes 1 and 2, fails 3 |
| What a pass needs on, say, 36 questions (12 traps: 4 not-in-the-documents, 8 answerable) | 0 | 4 of 4 | 32 of 32 | pass |

### C.4 What result means it didn't

Missing any one of the three thresholds: one WRONG, one not-in-the-documents trap answered, or one
answerable question not graded CORRECT.

### C.5 The controlled failure

Predicted failure, written before building the loop: an answer that quotes the base exclusion 5(d)
when endorsement E-2 overrides it. Trigger it on purpose by replaying such a reply with the `recorded`
answerer; the checker passes it (the quote is real), and the gold grade marks it WRONG. The same case
is already pinned by `test_real_quote_from_the_wrong_clause_passes_the_checker_but_grades_wrong`. The
recovery (for example, a checker rule that flags a quoted exclusion when an endorsement in the file
names it) gets reviewed and re-run before it is accepted.

### C.6 Also reported each run

Contract parse failures, retries used, model calls per question, tokens and cost, and the human gate's
decisions.

### C.7 What the sample can and cannot show

Synthetic documents, 30 to 50 questions, mostly written by me. A pass shows the method works on this
file. It does not show that ClaimCheck works on real claims, and the film doesn't claim it.

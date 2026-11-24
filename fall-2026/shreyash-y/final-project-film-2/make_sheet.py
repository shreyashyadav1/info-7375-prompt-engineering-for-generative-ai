#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for the ClaimCheck final project film (four-part cut).

Course brief (INFO 7375 "What your project film needs to show"): four parts, in this order:
  1. Executive summary: what and why, no "how".
  2. Introduction: what other people have done, and why mine still matters.
  3. Methods: the plan, the data, step by step, and whether I have what I need.
  4. Evaluation: what I will measure, and what result means it worked or didn't.

Built with the Brutalist show-tell skill (one drawing per beat, short labels, the voice explains),
adapted for a student film: the narration is the local Kokoro am_onyx voice reading Shreyash
Yadav's first-person script (disclosed on the first and last frames), no Liam / in-for-Bear persona,
no @NikBearBrown handle, and the outro is a drawn title card instead of ClaudeTitleOutro, whose
handle is fixed in the component. Detail lives in APPENDIX.md; every claim is in FACTCHECK.md.

HONESTY: past tense only for what ran (the offline baseline and tests, re-run 2026-11-23, saved in
evidence/). Everything about the agent loop, tools, gate, larger data set and live Claude run is
future tense. No Claude response is shown: no live Claude run has happened yet.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "yadav-shreyash-final-project-film"
TITLE = "Quote It or Refuse."
VOICE = "am_onyx"

SPARSE = ("show-tell style: one drawn object or scene on a cream stage per beat, short labels, the voice "
          "carries the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and "
          "contrast still apply.")


def est(n):
    return round(len(n.split()) / 3.3, 1)


def beat(bid, part, narration, cls, image, show, sparse=True):
    b = {"beat_id": bid, "act": part, "lane": "manim", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": est(narration),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                  "manim": {"class": cls}, "motion_claim": image}}
    if sparse:
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE}
    return b


def remotion(bid, part, narration, pattern, props, show, lane="bookend", gate="SHOW", **extra):
    b = {"beat_id": bid, "act": part, "lane": lane, "proof_gate": gate,
         "narration_text": narration, "estimated_duration_s": est(narration),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


# B16 matches claimcheck/grading.py exactly: CAUGHT only when the file has no answer and the checker
# blocks the one given; MISSED whenever the answer existed but the reader got nothing.
B16_NARR = ("Part four: how I'll know it worked. Each question gets one of four grades against its frozen gold "
            "answer: correct; caught, when the file has no answer and the checker blocks the one given; missed, "
            "when the answer was there but the reader got nothing; and wrong, when a wrong answer reaches the "
            "reader. Today's no-model baseline: five correct, none caught, one missed, four wrong.")


def _cue(text, phrase):
    """Fraction of the beat at which `phrase` is spoken, kept out of GATE T's 45-55% sample window."""
    f = text.index(phrase) / len(text)
    if 0.395 < f < 0.556:          # a lens move lasts 0.05 of the beat; keep all of it outside 0.45-0.55
        f = 0.39 if f < 0.475 else 0.556
    return round(f, 3)


B16_CUES = [_cue(B16_NARR, p) for p in ("caught, when", "missed, when", "and wrong, when")]

P1, P2, P3, P4 = ("1 executive summary", "2 introduction: what others have done",
                  "3 methods", "4 evaluation")

BEATS = [
 # ───────────────────────────── PART 1 · EXECUTIVE SUMMARY ─────────────────────────────
 remotion("BIDEA", P1,
    "Hi, I'm Shreyash Yadav, and this film is about my final project for INFO seventy-three seventy-five. "
    "It's called ClaimCheck. It isn't a smarter chatbot for insurance claims. It's a citation checker.",
    "BrutalistHesitantWriter",
    {"text": "ClaimCheck is a smarter chatbot\nfor insurance claim files.", "triggerWords": "smarter chatbot",
     "replacementWords": "citation checker", "fontSize": 96, "face": "serif", "align": "center",
     "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
     "seed": SLUG, "banner": "AI voice reading my script"},
    [{"at": 0.0, "event": "types 'ClaimCheck is a smarter chatbot for insurance claim files.'"},
     {"at": 0.6, "event": "backspaces 'smarter chatbot' and types 'citation checker'"}],
    lead_silence_s=0.8,
    motion_claim="The writer types the naive description and corrects it to the real one: a citation checker.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),

 beat("B00", P1,
    "An insurance claims examiner asks one question all day. Is this covered, and which clause says so?",
    "B00_ClaimFile",
    "The claim file (a binder) drops onto the stage; a question slip slides out beside it.",
    [{"at": 0.1, "event": "binder lands with a shadow"}, {"at": 0.55, "event": "question slip slides out"}]),

 beat("B01", P1,
    "ClaimCheck answers only with a word-for-word quote from the claim file, checked against the file "
    "before anyone sees it. If no clause answers the question, it should say: not in the documents.",
    "B01_QuoteOrRefuse",
    "The binder's cover lifts; one line lifts out as a quote slip and gets a check; a second slip "
    "returns blank with a refusal mark.",
    [{"at": 0.15, "event": "cover lifts"}, {"at": 0.35, "event": "quote slip rises, check lands"},
     {"at": 0.75, "event": "empty slip: refuse"}]),

 beat("B02", P1,
    "Why does that matter? A fluent answer that cites the wrong clause looks exactly like a right one.",
    "B02_LookAlike",
    "Two identical answer slips side by side, each with a citation tab; only one tab connects to the "
    "clause that answers the question.",
    [{"at": 0.2, "event": "two identical slips"}, {"at": 0.6, "event": "one tab's line reaches the wrong clause"}]),

 # Feedback 2026-11-23: the summary should say what citing the wrong clause costs.
 beat("B02B", P1,
    "Trust it, and an examiner could pay a claim the policy excludes, or deny a covered claim and leave "
    "the policyholder unpaid. Either way, the quote makes the mistake look checked.",
    "B02B_Consequence",
    "Two claim pages, each with the same cited slip clipped on; the stamp comes down on each: 'paid' on "
    "the excluded claim, 'denied' on the covered one, each with a cross; then each clipped slip gets a "
    "check: 'looks checked'.",
    [{"at": 0.15, "event": "stamp: excluded claim paid"}, {"at": 0.45, "event": "stamp: covered claim denied"},
     {"at": 0.8, "event": "the slips look checked"}]),

 beat("B03", P1,
    "Part of ClaimCheck already runs. The rest of this film covers what others have done, "
    "how I'll build it, and how I'll know it worked.",
    "B03_Roadmap",
    "A solid crate (built) and three dashed outlines (planned) line up along a rail; each dashed "
    "outline lights as its part is named.",
    [{"at": 0.1, "event": "solid crate: runs today"}, {"at": 0.45, "event": "three planned outlines"}]),

 # ───────────────────────────── PART 2 · WHAT OTHERS HAVE DONE ─────────────────────────────
 beat("B04", P2,
    "Part two: what others have done. AI search engines already cite sources. In early 2023, Stanford "
    "researchers checked four of them, including Bing Chat and Perplexity: only about half of their "
    "sentences were fully supported by their citations.",
    "B04_SearchEngines",
    "Four answer cards, each with citation tabs; a counter climbs to 51.5% beside them.",
    [{"at": 0.25, "event": "four answer cards"}, {"at": 0.7, "event": "51.5% lands"}]),

 beat("B05", P2,
    "Legal research tools fetch real cases first. Even so, a 2024 study by Stanford and Yale researchers "
    "found Lexis Plus AI and Westlaw's AI tool hallucinated seventeen to thirty-three percent of the time.",
    "B05_LegalTools",
    "A row of case books; answer slips come off them and some get struck; '17-33%' lands.",
    [{"at": 0.2, "event": "case books"}, {"at": 0.6, "event": "17-33% lands"}]),

 beat("B06", P2,
    "Anthropic added a citations feature to Claude in 2025. Its documentation guarantees each quote "
    "points to real text in your documents. That makes a quote real. It doesn't make it the right one.",
    "B06_RealNotRight",
    "A quote slip draws a pointer into a page and gets a check ('real'); a second mark beside it stays "
    "open ('right?').",
    [{"at": 0.3, "event": "pointer lands in the page: real"}, {"at": 0.8, "event": "right? stays open"}]),

 # Feedback 2026-11-23: show the two studies, what they found, and the gap, on one screen.
 beat("B07A", P2,
    "Side by side, both studies found cited answers that were wrong or unsupported, and Anthropic's citations "
    "feature makes a quote real, not right. That's the gap ClaimCheck addresses: a cited answer can still be wrong, "
    "so something has to catch it before a reader relies on it.",
    "B07A_TheGap",
    "Two study cards side by side: Liu et al., 2023, four AI search engines, 51.5% fully supported; "
    "Magesh et al., 2024, Lexis+ AI and Westlaw AI, 17-33% hallucinated. A line under both: the gap, "
    "catch it before the reader, with an open ring.",
    [{"at": 0.1, "event": "two study cards"}, {"at": 0.3, "event": "the two findings"},
     {"at": 0.6, "event": "the gap line"}, {"at": 0.85, "event": "open ring"}]),

 beat("B07", P2,
    "Citing is common; checking isn't. ClaimCheck adds the check: each quote is tested before an examiner "
    "sees it, the tool should refuse when the file is silent, and it counts how often a wrong answer still gets "
    "through.",
    "B07_AddsTheCheck",
    "The quote slip passes under the inspection lamp; a tally board beside it counts one mark.",
    [{"at": 0.25, "event": "lamp swings onto the slip"}, {"at": 0.8, "event": "tally mark"}]),

 # ───────────────────────────── PART 3 · METHODS ─────────────────────────────
 beat("B08", P3,
    "Part three: how I'm building it. The first piece already runs, offline: a synthetic homeowner policy "
    "I wrote, and ten questions, four of them traps, frozen with a checksum before any model saw them. "
    "Its seventeen tests passed again today.",
    "B08_FirstPiece",
    "One policy page; ten question cards in a row, four with a terracotta dot; a lock bar slides over "
    "the row; a check for the tests.",
    [{"at": 0.25, "event": "policy page"}, {"at": 0.45, "event": "ten cards, four marked"},
     {"at": 0.7, "event": "lock bar"}, {"at": 0.9, "event": "tests check"}]),

 beat("B09", P3,
    "Every answer comes back in a fixed format: an answer, a word-for-word quote, its document, and a "
    "status. Then plain code checks the quote: it must appear in that document exactly, with the "
    "answer's numbers and at least half its key words. If not, the answer never reaches the reader.",
    "B09_ContractChecker",
    "An answer slip with four field bars slides under the inspection lamp; the lamp lights it; a "
    "barrier drops in front of the reader for a slip that fails.",
    [{"at": 0.15, "event": "four field bars"}, {"at": 0.5, "event": "lamp check"},
     {"at": 0.85, "event": "barrier stops a failed slip"}]),

 beat("B10", P3,
    "Next, it becomes an agent. Claude answers; the checker checks. On a failed check, Claude gets one "
    "retry with the checker's reason. If that fails too, ClaimCheck refuses. It stops on a checked "
    "quote, a refusal, or three model calls, never because the model says it's done.",
    "B10_AgentLoop",
    "A loop track: answer, check, retry; three budget tokens drain one by one; the loop exits at a stop "
    "sign.",
    [{"at": 0.2, "event": "loop draws"}, {"at": 0.45, "event": "retry arc"},
     {"at": 0.75, "event": "three tokens"}]),

 beat("B11", P3,
    "Its tools can only read: search the claim file, and open one section. A permission list, written in "
    "code, allows those two and refuses everything else. It can't write, send, or decide coverage.",
    "B11_ReadOnlyTools",
    "Two tools undock from a tool block and pass a gate; a third parcel (send) is stopped by the gate's "
    "barrier.",
    [{"at": 0.2, "event": "two tools pass"}, {"at": 0.6, "event": "barrier stops the parcel"}]),

 beat("B12", P3,
    "Then the human gate. The examiner sees the answer beside its highlighted quote, and approves, "
    "rejects, or sends it back, and that decision is saved with exactly what they saw. A person decides "
    "coverage; ClaimCheck only finds and quotes.",
    "B12_HumanGate",
    "A document with a highlighted quote; the approval stamp comes down; the stamped record drops into "
    "a drawer.",
    [{"at": 0.2, "event": "highlighted quote"}, {"at": 0.45, "event": "stamp"},
     {"at": 0.7, "event": "record filed"}]),

 beat("B13", P3,
    "All the data is synthetic, written for this project, with no real claims or customer data. I'll "
    "grow it into a full claim file, with thirty to fifty questions, a third of them traps, some written "
    "by someone other than me.",
    "B13_Data",
    "A crate fills with four kinds of pages; question cards stack beside it, a third marked as traps.",
    [{"at": 0.25, "event": "pages drop into the crate"}, {"at": 0.65, "event": "question cards stack"}]),

 beat("B14", P3,
    "Step by step. One: get an API key and run Claude on the ten frozen questions. Two: grow the data and "
    "freeze a held-out set. Three: build the loop, tools and gate, tests first. Four: tune prompts on "
    "the rest, logging each change with its score. Five: one scored run on the held-out set.",
    "B14_Steps",
    "Five crates on a rail; each moves forward and gets a step marker as it is named; the last goes "
    "into a vault.",
    [{"at": 0.1, "event": "step 1"}, {"at": 0.3, "event": "step 2"}, {"at": 0.5, "event": "step 3"},
     {"at": 0.7, "event": "step 4"}, {"at": 0.9, "event": "step 5"}]),

 # Feedback 2026-11-23: say plainly what I have and which dependencies are still unresolved.
 beat("B15", P3,
    "Do I have what I need? Already in hand: Python, the Anthropic SDK, Claude Code and GitHub, and a "
    "laptop, which is enough because the model runs on Anthropic's servers. Still unresolved: an API key "
    "with token credits, which is step one. I estimate a ten-question run at under two dollars. And I "
    "need a second person to write some of the questions.",
    "B15_Resources",
    "Two columns. 'have': the four tool logos with a check, and the workstation ('compute') with a check. "
    "'unresolved': an empty budget tray ('API key', 'under $2, est.') and a stack of blank question "
    "cards ('second writer').",
    [{"at": 0.15, "event": "have: logos, check"}, {"at": 0.4, "event": "compute check"},
     {"at": 0.5, "event": "unresolved column"}, {"at": 0.6, "event": "API key tray"},
     {"at": 0.9, "event": "second writer"}]),

 # ───────────────────────────── PART 4 · EVALUATION ─────────────────────────────
 remotion("B16", P4,
    B16_NARR,
    "ShowTellCard",
    {"kind": "focus", "heading": "Baseline run, Nov 23, 2026",
     "items": [{"label": "Correct", "value": "5", "sub": ""}, {"label": "Caught", "value": "0", "sub": ""},
               {"label": "Missed", "value": "1", "sub": ""}, {"label": "Wrong", "value": "4", "sub": ""}],
     "focus": 3, "cues": B16_CUES},
    [{"at": 0.1, "event": "report rows land"}, {"at": 0.62, "event": "lens settles on Wrong"}],
    lane="card", gate="CARD",
    motion_claim="The lens walks the four grades of the real baseline report and settles on Wrong: the number that matters.",
    qc={"sparse_by_design": True, "sparse_reason": "ShowTellCard focus: one real report, four rows."}),

 beat("B17", P4,
    "All four wrong answers quoted the policy word for word, so all four passed the checker. Only grading "
    "against gold caught them. The checker makes an answer traceable. It doesn't make it right.",
    "B17_TraceableNotRight",
    "A slip passes the lamp with a check, then meets the gold slip in a comparison tray: they don't "
    "match, and a cross lands.",
    [{"at": 0.2, "event": "lamp check"}, {"at": 0.55, "event": "gold comparison"}, {"at": 0.7, "event": "cross"}]),

 # Feedback 2026-11-23: a measurable pass threshold. "Most" became a number, set by Shreyash at 100%:
 # every answerable question graded CORRECT (today's baseline: 5 of 8, 62.5%).
 beat("B18", P4,
    "So here's the pass bar, on the held-out set. Zero wrong answers reach the reader. Every "
    "not-in-the-documents trap is refused: one hundred percent. And every answerable question is "
    "answered correctly, also one hundred percent. Refusing everything would pass the first two and "
    "fail the third.",
    "B18_TheBar",
    "Three lamps on a gate light one by one: 0 wrong answers, 100% of traps refused, 100% answered "
    "correctly; a 'refuse all' panel lights only the first two.",
    [{"at": 0.25, "event": "lamp 1"}, {"at": 0.45, "event": "lamp 2"}, {"at": 0.65, "event": "lamp 3"},
     {"at": 0.85, "event": "refuse all fails the third"}]),

 beat("B19", P4,
    "It didn't work if it misses any one of those three numbers. And I'll break it on purpose: replay an "
    "answer that quotes the base clause that an endorsement overrides, and show the gold grade catches it.",
    "B19_BreakItOnPurpose",
    "A recorded slip (the overridden clause) is fed back in; the gold tray catches it with a cross.",
    [{"at": 0.3, "event": "one slip gets through: fail"}, {"at": 0.7, "event": "replayed slip caught"}]),

 beat("B20", P4,
    "One limit stays: the data is synthetic and mostly mine, so a pass shows the method works on this "
    "file, not on real claims.",
    "B20_Limit",
    "The crate of synthetic pages sits inside a dashed boundary; real claims stay outside it.",
    [{"at": 0.3, "event": "dashed boundary"}, {"at": 0.7, "event": "real claims outside"}]),
]

BEATS.append({"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW",
              "narration_text": "Quote it, or refuse. ClaimCheck, by Shreyash Yadav.",
              "estimated_duration_s": 4.0, "voice": VOICE, "engine": "kokoro", "tail_silence_s": 1.0,
              "shot": {"type": "GRAPHIC", "source": "own",
                       "visual_intent": "Title restate with name, course, and the AI-narration disclosure. "
                                        "Replaces ClaudeTitleOutro, whose @NikBearBrown handle is fixed in the component.",
                       "show": [{"at": 0.0, "event": "title types in"}, {"at": 0.4, "event": "name, course, disclosure"}],
                       "manim": {"class": "BOUT_Title"}, "motion_claim": "Title restate."},
              "qc": {"sparse_by_design": True, "sparse_reason": "Outro title card."}})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 - FINAL PROJECT FILM",
    "working_title": "ClaimCheck", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "student-info7375", "persona": "Shreyash Yadav (AI voice reading the student's own script)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "clock": "narration", "palette": "claude",
    "register": "Teardown", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none",
    "pronounce": {"Shreyash": "ʃɹˈeɪəʃ", "Yadav": "jˈɑːdəv"},
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Course brief: four parts in this order (summary, prior work, methods, evaluation). "
                              "The hesitant writer opens the summary; no terms card, verdict card or Your Turn, "
                              "which would add parts the brief doesn't ask for. Student outro is a drawn title card "
                              "(no @NikBearBrown handle)."),
    "audience": "INFO 7375 instructor and TAs; reviewers for applied-AI / LLM engineer roles",
    "source_doc": ("ClaimCheck first piece (submission folder, 2026-10-25), re-run 2026-11-23 into evidence/; "
                   "PROJECT-BRIEF.md (2026-10-14); prior-work sources in SOURCES.md and FACTCHECK.md"),
    "honesty": ("Past tense only for what ran: the offline no-model baseline and the 17 unit tests (re-run "
                "2026-11-23). No Claude API key yet, so no live Claude run and no Claude response is shown. "
                "Agent loop, tools, gate, larger data set and held-out run are plans."),
    "tags": ["ClaimCheck", "INFO 7375", "citation checking", "LLM evaluation", "agentic AI", "Brutalist"]},
    "beats": BEATS}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(len(BEATS), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")

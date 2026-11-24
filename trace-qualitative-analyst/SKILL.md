---
name: trace-qualitative-analyst
description: Annotate agent trajectories with verbatim Act-onomy evidence, resolve ambiguous labels using adjudicated cases, and render interactive trajectory reports.
---

# SWE-agent Trajectory Analyzer

Produce an interactive HTML report that connects each Act-onomy annotation to its original thought or action. The overview shows the run timeline and action frequencies. The turn log links source passages to their codebook labels.

## When to use this skill

Use this skill when the user gives you any of the following:

- A raw SWE-agent trajectory (`.traj` JSON file, pasted text from the paper, or a copy-paste from logs)
- A description of agent turns asking for codebook analysis
- A request to "annotate", "tag", "ground", "break down", or "visualize" agent reasoning
- A request to build a qualitative-analysis artifact for one or more agent runs

The deliverable is always an interactive HTML file with an action-frequency profile, written in English.

## High-level workflow

There are four stages plus a required summarization step. **Stages 1 and 4 are now fully deterministic scripts**; stage 2 is a quick judgment per turn; **stage 3 and the summary are the cognitive work** — that's where you, Claude, do the reasoning.

```
1. Parse trajectory     → run scripts/parse_trajectory.py on a raw trajectory JSON;
                          it emits a partial annotated skeleton with TODOs
2. Phase-label turns    → assign reproduce/localize/edit/recover/verify/submit
                          (fill in `phase`, `phase_label`, `headline` per turn)
3. ANNOTATE             → select verbatim thought and action spans and
                          map each to a codebook (group, subgroup, leaf) triple
3b. SUMMARIZE           → write a 4–8 sentence narrative summary of the run
                          (REQUIRED — the renderer rejects JSON without it)
4. Render               → run scripts/render_artifact.py on the annotated JSON
```

**Read `references/codebook.md` before stage 3.** It defines the 10 codebook groups (a three-level hierarchy: action → sub-action → leaf, aligned with arXiv:2605.13625v1), their subgroups and leaf actions, plus annotation guidelines. Stage 3 is impossible to do well without it.

For new annotations, read [the ambiguity case library](references/ambiguity_cases.md) before stage 3. Apply contract rules C1–C6 first, then consult matching adjudicated examples. Record the evidence field for each quote. Where a historical case uses `Evaluating`, use the current codebook action `Evaluate`. The [case-library editor](case-library.html) supports browsing the precedents and recording project-specific decisions.

If the user provides a JSON library exported by `case-library.html` (schema `actonomy.case-library.v1`), read its `cases` before stage 3. Match each precedent by its evidence field, quoted passage and rationale. A `label` decision supplies the user's label, `omit` leaves the matching passage untagged, and `unresolved` records an open question. Identify project-specific labels and unresolved or conflicting precedents in the findings. Apply the codebook to remaining passages and preserve the run's required evidence fields and validation format.

---

## Stage 1: Parse trajectory

**For the message-list trajectory format (a JSON array of `{role, text, ...}` dicts), use the preprocessor — don't extract by hand.** Manual extraction is slow and a single off-by-one character break the substring matching downstream.

```bash
python scripts/parse_trajectory.py <trajectory.json> \
    --instance-id <owner/repo-N> \
    --outcome <resolved|unresolved> \
    --output <stem>.annotated.json
```

What the preprocessor does:
- Strips the leading system message
- Pulls the issue body out of the first user message (between `ISSUE:` and `INSTRUCTIONS:`)
- Walks each subsequent ai/user pair and emits one turn per ai message:
  - `thought`: ai message text with the `DISCUSSION` header and the trailing fenced code block stripped
  - `action`: the contents of that fenced code block (multi-line edits preserved verbatim)
  - `obs`: the previous user message with the trailing `(Open file: …) bash-$` prompt stripped
- Wraps the result in the full annotated-JSON schema with `TODO` placeholders for everything cognitive (`phase`, `phase_label`, `headline`, `quotes`, `summary`, `findings`)

Both role conventions are accepted: the native trajectory format uses `role: "ai"`; SWE-agent's `.traj` files use `role: "assistant"`. The preprocessor handles either.

**After running the preprocessor**, open the resulting `*.annotated.json` and walk the turns to fill in stages 2 and 3. The verbatim thought text is already exact — quote substrings will match at render time as long as you copy from the file.

### When the preprocessor doesn't apply

- **Paper-formatted trajectories** (e.g., arXiv Figure 33–36 transcripts pasted as text). The marker shape is:
  ```
  SWE-agent <instance>     ← assistant turn (thought + action follow)
  Observation <instance>   ← environment response (the observation for the NEXT turn)
  ```
  Convert these to the JSON message-list format first (see `assets/example_*.json` for the layout), then run the preprocessor. Or extract turns manually if the trajectory is short.
- **Raw paste / mixed format**: ask the user one clarifying question before proceeding (e.g., "Is this from the SWE-agent paper appendix, or from a `.traj` file you ran?").

### What you produce in stage 1

The preprocessor's output JSON has the full schema. Each turn entry looks like:
```json
{
  "n": 1,
  "phase": "TODO",
  "phase_label": "TODO",
  "headline": "TODO",
  "obs": "...verbatim observation...",
  "thought": "...verbatim thought, no DISCUSSION prefix, no code block...",
  "action": "...the command...",
  "quotes": []
}
```

Verbatim text is preserved — do not paraphrase the thought when filling in quotes. The renderer matches quoted substrings by `String.indexOf`.

---

## Stage 2: Phase-label turns

Assign one of these phases to each turn (used for the colored pill in the UI):

| Phase | When to use |
|---|---|
| `reproduce` | Creating reproduction script, running it to confirm bug |
| `localize` | Searching for files, navigating to relevant code, scrolling/goto |
| `recover` | Recovering from a failed command or lint error |
| `edit` | Applying the actual fix patch |
| `verify` | Re-running tests/repro after the fix |
| `submit` | Cleanup, `submit` command, exit |
| `other` | Anything that doesn't fit |

Also write a short `phase_label` (display string, e.g., "Reproduction", "File-level localize", "Pinpoint") and a one-line `headline` (~6-10 words capturing what this turn accomplishes).

---

## Stage 3: Quote-grounded annotation (the cognitive step)

**This is the part you must do manually for each turn.** The script cannot do it.

For each turn, quote the shortest verbatim spans that support distinct behaviors. Set `quote_target` to `both` for new contract-v3 annotations and set each quote’s `target` to `thought` or `action`. Map each quote to a `(grp, sub, leaf)` codebook triple from `references/codebook.md`.

### Hard rules

1. **Quotes must be exact substrings.** The renderer matches by `String.indexOf`. If the thought says "the bug" but you write "this bug", the highlight will silently fail. Copy-paste, don't paraphrase.
2. **Quotes must not overlap.** Split distinct evidence where possible. For inseparable spans, follow C4–C6 in the case library and surface any unresolved collision.
3. **Use a leaf from the codebook when possible.** If genuinely none fits, write a new leaf in the same naming style ("verb-phrase capturing the cognitive move") and the user can accept or revise it.
4. **The `grp` field uses these exact values (10-category v4.2 codebook):** `Retrieval`, `Memory`, `Planning`, `Reasoning`, `Evaluate`, `Deciding`, `Grounding`, `Executing`, `Learning`, `Reflection`. The keys are also their display names — no rewriting is performed by the template. The triple has no super-class layer; the paper's 3 clusters (External Interaction / Cognition & Execution / Learning & Adaptation) are presentation only.

### Heuristics

- **Short procedural turns** ("Now let's add the comments") may have only **1 annotation**. Don't pad.
- **Phase-transition turns** (turns that wrap up one phase and pivot to the next) often have **4-5 annotations**. Don't compress.
- **Tag the cognitive move, not the surface verb.** "Let's open the file" is *Grounding › Invoke structured API*, not just "Executing".
- **Reflection requires a failure signal.** Words like "did not work", "issue persists", "errored" are the trigger. Without one, prefer Reasoning or Deciding.
- **Reflection vs. Learning.** Reflection steers within the current episode; Learning persistently changes the agent's prompt, code, weights, or stored knowledge. If the move evaporates at episode end, it's Reflection.
- **Reasoning › Generating vs. Reasoning › Analysing.** Generating produces *new* artifacts (code, requirements, candidate moves) *de novo*. Analysing transforms information that is already present. Drafting a fresh patch is Generating; tracing dataflow through an existing patch is Analysing.
- **Diagnose vs. Infer**: Diagnose names a *cause* ("the regex doesn't match punctuation"). Infer chains *consequences* ("if X then Y"). Same thought can have both.

### Output of stage 3

For each turn, attach a `quotes` list:
```json
"quotes": [
  {"quote": "first try to replicate the bug as described",
   "target": "thought",
   "grp": "Planning",
   "sub": "Decompose task",
   "leaf": "Decompose into subgoals with success conditions"},
  ...
]
```

---

## Stage 4: Render

Once you have a fully annotated JSON, run the renderer:

```bash
python scripts/render_artifact.py <annotated.json> --output <output.html>
```

The script:
- Checks each quote against its designated thought or action field (warnings, not errors)
- Builds the run overview, action-frequency bars and linked turn log
- Fills the HTML template
- Writes a self-contained HTML file

If there are warnings, **read them and fix the JSON** — usually the quote has a typo or smart-quote difference. Don't ship a render with warnings.

### Input JSON schema (full reference)

```json
{
  "instance_id": "pylint-dev/pylint-5859",
  "model": "SWE-agent w/ GPT-4 Turbo",
  "outcome": "resolved",
  "issue_text": "...full issue body, plain text...",
  "summary": "REQUIRED. A 4–8 sentence narrative summary of the entire trajectory...",
  "quote_target": "both",      // New contract-v3 annotations mark the host field of each quote.
                               // See "Quote target modes" below.
  "findings": [
    {"title": "Reasoning is layered", "body": "Turn 9 alone has 5 distinct phrases..."},
    ...
  ],
  "segments": [                // OPTIONAL. See "Segments (optional)" below.
    {"start": 1, "end": 5, "title": "First investigation cycle",
     "summary": "Localize → reproduce → draft a first patch; T5 fails to dispatch."},
    ...
  ],
  "turns": [
    {
      "n": 1,
      "phase": "reproduce",
      "phase_label": "Reproduction",
      "headline": "Create the empty test file.",
      "obs": "...",
      "thought": "...verbatim...",
      "action": "create test.py",
      "quotes": [
        {"target": "thought", "quote": "...", "grp": "Planning", "sub": "...", "leaf": "..."},
        ...
      ],
      "insight": "Optional note shown with the turn."
    },
    ...
  ]
}
```

### Quote target modes

The renderer supports three top-level modes for where quotes are anchored:

| `quote_target` | When to use | Quote substrings come from | Highlighted block |
|---|---|---|---|
| `"both"` | New contract-v3 annotations | Each quote names its `target` | Thought and Action in the turn log |
| `"thought"` | Previously annotated thought-only trajectories, or a requested thought-only analysis | `t.thought` | Thought |
| `"action"` | Previously annotated action-only trajectories, or a requested action-only analysis | `t.action` | Action |

**In `"action"` mode**, the schema interpretation flips:

- `t.action` should hold the **verbatim action surface** the agent emitted — multi-line code blocks, stdout strings, the full delegation/peer message — not a one-line summary like `edit foo.py`.
- `t.thought` becomes **context only** (rendered without highlights). Use it for a brief framing note such as `"(executor reports stdout)"` or `"(assistant emits Python; prose explanation around code blocks not annotated)"`.
- Quotes must be substrings of `t.action`, not `t.thought`. The validator will warn if they aren't.
- Pure-thought turns (e.g., an agent emitting only a plan outline with no code, no peer directive) are valid with `quotes: []`. The renderer handles 0-quote turns gracefully.

**Annotation rule for action mode**: do *not* pull quotes from explanatory prose around the code. If an agent emits `# This computes the daily usage\nx = 5 * 0.2`, quote `x = 5 * 0.2`, not the comment-style preamble. The whole point of action mode is that the cognitive interest lies in the executable surface — that is exactly where bugs hide and where the multi-agent loop's failures are most diagnostic.

### Summary section (required)

The `summary` field is **required** for every render. It appears in the Overview tab above the stage narratives.

Aim for **4–8 sentences** of narrative prose. A good summary covers:

1. **What the agent was trying to do** — one-line restatement of the bug/task in the agent's words, not the issue's.
2. **The shape of the run** — how many phases the trajectory falls into and what each phase accomplished. Use turn ranges (`T1–T9`, `T10–T11`) so the reader can jump in.
3. **The key turn(s)** — which one or two turns carry the most weight (densest reasoning, phase pivot, the patch itself).
4. **A judgment about quality** — did the agent solve the *bug* or just the *symptom*? Was the verification real or circular? Were there wasted turns and what pattern caused them?

Inline HTML is allowed (`<strong>`, `<em>`, `<code>`) so you can highlight turn numbers and key terms. Keep the tone descriptive, not boosterish — say what happened, including what went sideways.

The summary is the lens through which the rest of the artifact is read — write it last, after annotation, when you actually understand the run.

### Findings section

The `findings` array (0–4 entries) populates the Findings tab. Each finding is a `{title, body}` pair. Good findings are observations that would only become visible **because** of the quote-level granularity — for example:
- Turns where one paragraph fires 4+ different codebook leaves
- A single short phrase that carries a phase transition
- The contrast between annotation-dense reasoning turns and bare procedural turns

If you have nothing meaningful to say, omit `findings` entirely. Note: the Findings tab is currently hidden in rendered HTML reports (`scripts/report_layout.py` sets `{{FINDINGS_VISIBILITY}}` to `hidden`), while preserving any `findings` entries in the annotated JSON.

**Summary vs. Findings:** the **summary** is a holistic narrative of the whole run (what happened, in what order, with what quality). The **findings** are punchy 1–2 sentence observations about *patterns the quote-level granularity reveals*. Don't duplicate; they read as complementary layers.

### Trajectory signature (auto-generated)

The Turn log shows the original trajectory beside its signature. Each signature chip displays the group, subgroup and leaf of one quote. Select a chip to locate its source passage, or select a highlighted passage to locate the matching chip. On narrow screens the two views share a switch. Repeated thought text marks session restarts in the signature.

### Human-interaction events (optional — human-in-the-loop trajectories)

For trajectories with real human turns (Claude Code sessions, chat-style agent logs), do **not** fold human prompts into the next turn's `obs` — the human is an actor, not part of the environment. Instead, normalize the trajectory as a mixed event sequence: agent turns keep the `(observation, thought, action)` triple (where `obs` now holds *environment feedback only*, e.g. tool results), and each human prompt becomes a first-class **interaction event** interleaved at its true position in the `turns` array:

```json
{"kind": "interaction",
 "id": "H3",                     // optional; auto-numbered H1..Hk if omitted
 "actor": "human",               // default "human"
 "label": "escalation",          // optional interaction-type tag, see below
 "text": "FIX THE RED TEXT ..."} // REQUIRED, the VERBATIM prompt — never truncate
```

Rules and rendering behavior:

- Interaction events carry **no codebook quotes** — the codebook describes *agent* behavior. The agent's uptake of a prompt is annotated on the *agent* turn that responds (e.g., Reasoning › Analysing › Understanding intent; Reflection › Reflect on external feedback › Receive and integrate external feedback).
- `label` is a lightweight *human-move* tag, deliberately separate from the agent codebook. Suggested vocabulary (extend as needed): `initial request`, `defect report`, `diagnostic hint`, `scope extension`, `escalation`, `preference reversal`, `commit request`, `constraint`, `new task`.
- Agent turns keep their own contiguous numbering (`n` = 1..N, interactions excluded), so `segments`, findings, and summary turn references are unaffected by how many human turns interleave.
- Each interaction appears in the turn log and signature at its original position. The report header gives the interaction count. Write an actor and a concrete verb in each headline so readers can distinguish a human request from the agent’s response.

### Segments and layout

Optional `segments` entries have `start`, `end`, `title` and `summary`. Use agent turn numbers for the bounds in chronological order. Authored segments supply the stage timeline and narrative. Where turns have no authored segment, the renderer groups consecutive turns by phase. Use `<code>`, `<strong>` or `<em>` for inline formatting in narrative fields.

The Overview tab includes a resizable behavior-profile column. The Turn log opens with expanded turns and supports expanding or collapsing them together.

---

## Working with the user

By default, **run Stages 1 → 2 → 3 → 3b → 4 end-to-end in one pass** and generate both the annotated JSON and the rendered HTML report without pausing for intermediate confirmations.

Only pause to ask the user before proceeding if:
- the input file/paste is ambiguous or does not contain a parseable trajectory, or
- the user explicitly asks to review parsed turns or an annotation sample before rendering.

After rendering, share direct links to the generated HTML report and annotated JSON (and run `present_files` if available) along with a brief summary of any borderline phase or codebook calls so the user can request targeted edits if needed.

If the user asks for multiple trajectories (e.g., a successful one and a failed one for comparison), produce one HTML per trajectory. The codebook is shared across runs but each render is self-contained.

---

## Worked example

The skill ships with `assets/example_pylint_5859.json` — a complete annotation of the `pylint-dev/pylint-5859` trajectory from arXiv:2405.15793 Figure 34. Read it as a reference for granularity, quote-selection style, finding-writing style, and overall calibration.

To see the rendered output:

```bash
python scripts/render_artifact.py assets/example_pylint_5859.json --output /tmp/example.html
```

This is your gold-standard reference for what "good" looks like.

---

## File layout

```
trace-qualitative-analyst/
├── SKILL.md                              ← this file
├── case-library.html                     ← browse precedents and import/export project cases
├── references/
│   ├── ambiguity_cases.md                ← adjudicated cases and contract v3
│   └── codebook.md                       ← the 10-group v4.2 action codebook (read in stage 3)
├── scripts/
│   ├── report_layout.py                  ← standalone report layout
│   ├── parse_trajectory.py               ← stage 1 preprocessor (raw JSON → skeleton)
│   └── render_artifact.py                ← stage 4 renderer (annotated JSON → HTML)
└── assets/
    ├── template.html                     ← HTML template with placeholders
    └── example_pylint_5859.json          ← worked example / reference
```

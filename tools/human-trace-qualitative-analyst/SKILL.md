---
name: human-trace-qualitative-analyst
description: Analyze human-in-the-loop agent trajectories (Claude Code sessions, chat-style logs where a real user prompts an agent across multiple turns) with quote-level Act*ONOMY codebook annotations and first-class human interaction events, producing an interactive HTML report with human/agent icons, collapsed-by-default turn cards, and plain-English actor-verb summaries. Use whenever a trajectory contains real human turns — persona-tagged sessions (Mind Changer, Expert Nitpicker, Vague Requester), swe-chat transcripts, Claude Code .jsonl session logs, or any (human prompt → agent work)* loop. Trigger for requests like "annotate this human-agent session", "analyze the human-in-the-loop trajectory", "带human的trajectory标注", "分析人机交互轨迹", "label the human prompts", "persona analysis of this session". For agent-only trajectories (SWE-agent .traj, no real user turns) use trace-qualitative-analyst instead.
---

# Human-in-the-loop Trajectory Analyzer

Specialization of `trace-qualitative-analyst` for trajectories where a **real human** interleaves with the agent. The deliverable is the same interactive HTML report, with three additions:

1. **Human prompts are first-class interaction events**, not observations. Each gets its own amber card (Google Material `person` icon), a verbatim prompt body, a one-line `headline`, and a `label` from a human-move taxonomy.
2. **Both actors get summaries.** Agent turn headlines read "Agent <verb> …", interaction headlines read "Human <verb> …", segment titles read "Human <does X> · Agent <does Y>".
3. **Human-in-the-loop analysis lenses** (who supplies the error signal, pushback/concession arcs, preference reversals, persona fingerprints) drive the summary and findings.

## Dependency

This skill **requires the sibling skill** `trace-qualitative-analyst` (same parent directory):

- `../trace-qualitative-analyst/references/codebook.md` — the 10-group Act\*ONOMY v4.2 codebook (read before annotating)
- `../trace-qualitative-analyst/scripts/render_artifact.py` — the renderer (supports `kind: "interaction"` entries, actor icons, collapsed-by-default cards)

If the renderer rejects `kind: "interaction"`, the sibling skill is outdated — update it first.

## When to use this skill vs. the base skill

| Situation | Skill |
|---|---|
| SWE-agent / SWE-bench `.traj`, paper transcripts, agent-only runs | `trace-qualitative-analyst` |
| Claude Code session `.jsonl` with real user prompts | **this skill** |
| Persona-tagged sessions (swe-chat `user_persona` ≠ Other) | **this skill** |
| Multi-agent dialog with no human | `trace-qualitative-analyst` (action mode) |

Rule of thumb: **≥2 real human inputs after the initial task → this skill.**

## High-level workflow

```
1. Parse            → scripts/parse_chat_trajectory.py on the raw .jsonl;
                      emits a skeleton: agent (obs, thought, action) turns +
                      interleaved {kind:"interaction"} events, all TODO-marked
2. Label human moves → fill each interaction's `label` (references/human_moves.md)
                      and `headline` ("Human <verb> …")
3. Phase + headline  → phase-label agent turns (same 7 phases as the base skill);
                      headlines read "Agent <verb> …" in plain English
4. ANNOTATE          → quote-grounded (grp, sub, leaf) triples per agent turn,
                      per the base skill's codebook.md; interactions get NO
                      codebook quotes (the codebook describes agent behavior)
5. Segment           → one segment per prompt cycle (or merged cycles);
                      titles "Human <does X> · Agent <does Y>"
6. SUMMARIZE         → intro sentence + bullet list (required); findings through
                      the human-in-the-loop lenses below
7. Render            → python ../trace-qualitative-analyst/scripts/render_artifact.py
```

## Stage 1: Parse

```bash
python scripts/parse_chat_trajectory.py <session.jsonl> \
    --instance-id "<repo> · session <id> (<persona>)" \
    --model "Claude Code (human-in-the-loop, persona: <persona>)" \
    --outcome <resolved|unresolved> \
    --output <stem>.skeleton.json
```

What it does with a Claude Code native log:

- **Real human text messages** (string `message.content`, excluding `<local-command-caveat>` and slash-command wrappers) → `{kind:"interaction", id:"H<k>", actor:"human", label:"TODO", headline:"TODO", text:<verbatim>}` at their true position.
- **Assistant `text`/`thinking` blocks** → start a new agent turn (`thought`); subsequent `tool_use` blocks become the turn's `action` surface (`$ cmd` for Bash, `grep '<pattern>' (in <path>)`, `read <path>:<range>`, `edit <path>` with `- old` / `+ new` lines, `write <path>`, generic fallback for other tools). Paths are made relative to the session `cwd`.
- **`tool_result` contents** → the *next* turn's `obs` (truncated; human prompts are never truncated).
- **Agent turn numbering excludes interactions** (T1..TN contiguous), so segments and turn references are stable.

Verify the printout: agent-turn count, interaction count, and that each human prompt opens where you expect. Tool-use-only turns (empty `thought`) are normal — annotate their action surface.

## Stage 2: Label human moves

Read `references/human_moves.md`. For each interaction fill:

- `label` — one (or two joined by ` + `) human-move tags, e.g. `defect report`, `escalation`, `commit request + constraint`.
- `headline` — one plain-English sentence starting with "Human": *"Human says the badge text on line 442 is unreadable."*

The label sequence across the session is the **persona fingerprint** — compare it against the profiles in the reference file.

## Stages 3–4: Phases, headlines, quote annotation

Same as the base skill (read its SKILL.md stages 2–3 and `references/codebook.md`), plus these human-in-loop conventions:

- **`quote_target: "both"`** is the default here: chat-agent turns split cognition between short thought texts and rich action surfaces (edit diffs, scripts, commands).
- The agent turn that responds to a prompt usually anchors *Reasoning › Analysing › Understanding intent* (first turn of a cycle) or *Reflection › Reflect on external feedback › Receive and integrate external feedback* (after a correction). The human's words themselves are never quoted for codebook tags.
- **Reflection guideline:** in human-in-loop runs the failure signal is usually the *human*, not a test. "you're right", "wait —" after a complaint, re-investigating a 'done' item — all Reflection triggers.
- **Plain-English headline rules** (undergraduate-readable, applies to headlines, segment titles/summaries, summary, findings, insights):
  - No tool names as verbs: *searches* not "greps", *reviews and saves (commits)* not "diffs/stages/commits", *changes* not "swaps".
  - Unpack mechanism jargon into cause-and-effect: *"the component's built-in white text wins over the orange"* not "CSS specificity".
  - Git terms allowed with a gloss on first use: *"saves (commits)"*.
  - Verbatim thought/action/quote text and codebook triples stay untouched — they are data.

## Stage 5: Segments

One segment per prompt cycle; merge cycles that form one arc (e.g., six prompts of one styling argument). Each title is a **Human-verb · Agent-verb pair**: `"Human reports a broken layout · Agent recovers from failed edits"`. Summaries are 1–4 sentences, every sentence starting with `<strong>Human</strong>` or `<strong>Agent</strong>`, with (H#/T#) anchors after each move. A segment whose start turn follows an interaction renders its card above that interaction automatically.

## Stage 6: Summary and findings — human-in-the-loop lenses

`summary` is required: an intro sentence (who, what app, which persona) + `<ul>` bullets — one per arc (with T/H ranges) — + a "Worth noticing:" bullet list. Probe these lenses for bullets and findings:

1. **Who supplies the error signal?** Count Reflection triggers: human complaint vs. tool error vs. agent self-check. Visual/UX work typically shows *zero* agent-detected errors.
2. **Pushback → concession arcs.** Turns where the agent argues with the human, and the exact quote where it flips ("you're right…").
3. **Information asymmetry.** Prompts that carry *diagnostic content* (the human names the failing class/line) vs. pure emotion (all-caps escalation) — and how differently the agent responds.
4. **Preference reversals.** Technically-correct fixes rejected on taste; the agent's compliance behavior (silent vs. argued).
5. **Self-sufficiency gradient.** Compare cycles by human prompts consumed per task — chat sessions often contain one near-autonomous arc that contrasts with the contested ones.
6. **Persona fingerprint.** The human-move label sequence, stated as a finding when it matches a known persona profile.

## Stage 7: Render

```bash
python ../trace-qualitative-analyst/scripts/render_artifact.py <annotated.json> --output <report.html>
```

Fix every warning before shipping. Then sanity-check: masthead shows "Human prompts <k>"; amber cards collapsed by default with "Human <verb>…" headlines; signature panel interleaves `H▸` rows.

## Worked example

`assets/example_c4d3dbfa.json` — the wodsmith "Mind Changer" session (42 agent turns, 10 human prompts, 93 quotes): the reference for granularity, human-move labels, actor-verb phrasing, segments, and lens-driven findings. Render it to see the target output.

## File layout

```
human-trace-qualitative-analyst/
├── SKILL.md                          ← this file
├── references/
│   └── human_moves.md                ← human-move label taxonomy + persona profiles
├── scripts/
│   └── parse_chat_trajectory.py      ← stage-1 parser (Claude Code .jsonl → skeleton)
└── assets/
    └── example_c4d3dbfa.json         ← worked example (Mind Changer session)

(depends on ../trace-qualitative-analyst/ for codebook.md and render_artifact.py)
```

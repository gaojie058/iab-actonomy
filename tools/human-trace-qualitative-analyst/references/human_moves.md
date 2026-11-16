# Human-move label taxonomy

Labels for `{kind: "interaction"}` events. This vocabulary is **deliberately separate from the Act\*ONOMY agent codebook**: the codebook describes what the *agent* does; these labels describe what the *human's* message does to the task state. Label the move's *function*, not its wording — an all-caps profanity prompt that adds no new information is an `escalation`, even though it superficially restates a `defect report`.

One label per interaction; join two with ` + ` when one message genuinely does two things (`commit request + constraint`). Extend the vocabulary in the same style when nothing fits, and note new labels in the report findings.

## Task-creating moves

| Label | The message… | Example |
|---|---|---|
| `initial request` | opens the session's first task | "the red and orange together are pretty hideous … make it all orange" |
| `new task` | opens an unrelated task after a previous one closed (qualify: `new task · bug report`, `new task · feature removal`) | "lets remove streamable as an option" |

## Steering moves (the task stays, the target moves)

| Label | The message… | Example |
|---|---|---|
| `defect report` | says the result is wrong/broken, without saying why | "line 442 you can't even see the red text. fix it" |
| `diagnostic hint` | supplies *technical content* that narrows the cause (a class name, a line, a stack trace) | "then its text-orange-700 which does not work on the orange background" |
| `scope extension` | adds more places/cases to the same fix | "and fix line 1401 1521 please" |
| `preference reversal` | rejects a *correct* result on taste and states a new preference | "that looks shitty though. change it to orange background and white text" |
| `escalation` | repeats a prior complaint with raised emotional intensity, adding no new information | "FIX THE RED TEXT FUCKING REMOVE ALL RED ON THE PAGE" |
| `clarification answer` | answers a question the agent asked | "yes, the second one" |

**`defect report` vs `diagnostic hint`:** the hint names a mechanism-level fact the agent can act on directly; the report only names a symptom. This distinction matters — in observed sessions, hints trigger the agent's best reasoning while escalations trigger only re-checking.

**`preference reversal` vs `defect report`:** reversal rejects something that *works*; report rejects something that *doesn't*. Reversals are the signature move of the Mind Changer persona.

## Process moves

| Label | The message… | Example |
|---|---|---|
| `commit request` | asks to save/commit/push the work | "commit that work" |
| `constraint` | restricts how the agent may act (usually attached: `commit request + constraint`) | "…ignore db/indext.ts" |
| `approval` | accepts the result, possibly implicitly by moving on | "looks good, next…" |
| `technical challenge` | questions the agent's approach and demands justification or a change of plan | "why a new table instead of a column?" |

## Persona fingerprints

The label *sequence* across a session is a behavioral fingerprint. Profiles observed in swe-chat:

- **Mind Changer** — steering-heavy: `defect report` → `escalation` → `diagnostic hint` → `preference reversal` chains on a single task; acceptance criteria move repeatedly. (Worked example: `assets/example_c4d3dbfa.json` — sequence: initial request, defect report, scope extension, escalation, diagnostic hint, preference reversal, commit request + constraint, new task · bug report, commit request, new task · feature removal.)
- **Expert Nitpicker** — `technical challenge` dominant: the agent does most of the work; the human interrogates design decisions and demands corrections with precise technical content (high `diagnostic hint` ratio, low emotion).
- **Vague Requester** — under-specified `initial request` / `new task` moves followed by `clarification answer`s; the requirement is co-constructed across the session ("is X not enough…", "lets switch to phase 27").

When a session's fingerprint matches a profile, state it as a finding; when it doesn't, describe the actual sequence — that mismatch is itself a result.

## Headline conventions

Every interaction also carries a `headline`: one plain-English sentence starting with "Human", undergraduate-readable, no tool jargon:

- ✅ "Human points out the exact color class that is not working."
- ✅ "Human asks to save the work, skipping db/index.ts."
- ❌ "Human pinpoints text-orange-700 as the failing class." (jargon-dense)
- ❌ "Requests commit excluding db/index.ts." (no actor)

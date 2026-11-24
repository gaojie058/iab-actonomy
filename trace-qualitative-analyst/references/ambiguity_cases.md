# Adjudicated ambiguity cases

The study used the action name `Evaluating`. In new annotations for this repository, use `Evaluate` from the bundled [codebook](codebook.md). Historical labels and proposed additions are reproduced below.

<!-- BEGIN ANNOTATION CONTRACT (hand-maintained — outside the generated blocks) -->

## Annotation contract v3 — read before anything below

From the human-IRR study (`AC-Q2 .../irr/`, blind pass by a codebook-fluent
human against all three stacks). Two of these change **what gets quoted**, so
they override the general heuristics and any precedent below that predates
them.

### C1 · Quote the action surface, not only the thought

Set `quote_target: "both"` and give every quote a `"target": "thought"` or
`"target": "action"` field.

Batch-3 quoted thoughts only — all 922 spans across the three stacks sit in
`thought`, none in `action`. But every `Executing` leaf is *defined* by a
command being run (`Apply patch via edit` — "running an `edit` command";
`Run verification command` — "running `python`, `pytest`"). So `Executing` could
never be evidenced by the field it was defined on, and the stacks resolved that
by projecting the turn's command back onto the thought that announced it. The
human annotator, reading the glosses literally, used `Executing` **zero times in
41 quotes**. That is not a miss; it is the only self-consistent reading of a
thought-only contract.

### C2 · A thought that announces an action is Planning; the action span carries Executing

> 就句论句 — the sentence is judged on what it says. In `thought`, expect
> `Planning`, at most `Evaluating`. `Executing` belongs to the `action` span.

C1 is what makes C2 payable: the execution still gets labelled, on the span that
actually executes. Under a thought-only contract C2 alone would simply delete
`Executing` from the data.

**Worked pair** (astropy T15, sympy T3, scikit-learn T3 and five more):

| span | field | label |
|---|---|---|
| "run the script to see if we can reproduce the issue" | `thought` | `Planning > Formulate a workflow or plan > Plan function or tool use` |
| `python reproduce_issue.py` | `action` | `Executing > Executing plan > Run verification command` |

In all eight blind-pass collisions of this shape the turn's `action` literally
performed what the thought announced, and the stacks labelled the thought
`Executing` while the human labelled it `Planning`. Both were right about the
turn; the contract had not said which span owns the execution. Now it has.

### C3 · Precedents superseded by C1 and C2

25 adjudicated patterns covering 65 spans put a **thought** span into
`Executing`. They were adjudicated correctly under the thought-only contract and
are kept below as history, but **for thought spans they no longer apply**:

- `R1` (P002, P003, P144, P153, P158 — 36 spans, "run it / test our changes by
  running …") → the thought span is now `Planning`; `Run verification command`
  moves to the action span.
- `Apply patch via edit` on thought spans (P009, P015, P019, P027, P038, P049,
  P085, P093, P094, P110 — 17 spans) → thought span is now `Planning`;
  `Apply patch via edit` moves to the `edit …` action span.
- `Initiate planned action` / `Normal executing` / `Adopt debugging
  instructions` on thought spans (P011, P020, P033, P034, P037, P047, P057,
  P060, P062, P063 — 12 spans) → same move.

An `Executing` label on an `action`-targeted span is unaffected — there were
none before, because there were no action spans.

**This supersession has not been re-adjudicated span by span.** It is a stated
rule, not 65 fresh human calls. Any batch built under this contract is a new
annotation contract, not a re-run of batch-3, and is **not span-comparable with
batch-3**. Say so wherever its numbers are reported.

### C4 · When two leaves genuinely will not separate

Pick the leaf whose **gloss** fits the span most tightly, record the collision,
and move on. Do not break the tie by model majority, and do not leave the label
blank — a blank loses the span, while a recorded collision is evidence for the
next codebook version.

### C5 · Leaf collisions recorded so far

| span | leaves that would not separate | take | note |
|---|---|---|---|
| "it's likely to be in a file related to coordinates" | `Reasoning > Inferring > Infer causal relationship` ↔ `Infer structure from indirect evidence` | **`Infer structure from indirect evidence`** | proposed for **merge** — the two are not separable in general, and this one is the higher-level of the pair |
| "we can try to run the tests using pytest directly without installing the package" | `Planning > Formulate a workflow or plan > Plan function or tool use` ↔ `Formulate a high-level plan` | **`Plan function or tool use`** | separable in principle; on spans that name a specific tool, take `Plan function or tool use` |
| "we need to implement the proposed changes in the appropriate file" | `Planning > Formulate a workflow or plan > Plan code or artifact structure` ↔ `Formulate a high-level plan` | *unresolved* | recorded as a collision; no precedent yet |
| "we should test these new transformations to ensure they work as expected" | `Planning > … > Plan function or tool use` ↔ `Evaluating > Evaluating with gold > Plan verification step` | **`Plan verification step`** | structural defect: `Plan verification step` is the only `Plan*` leaf living outside `Planning`, and its four siblings under `Evaluating with gold` are all post-hoc comparisons. Flagged for the next codebook version |

### C6 · Retrieval vs Grounding on a phrase that will not split

From the human-IRR pass on `pydata__xarray-3305` (Q9 · T18). When a phrase cannot
be split into an operation part and an object part, decide on what the phrase
actually states:

| the phrase states | label | example |
|---|---|---|
| only the operation | `Grounding` | "Let's open the file" |
| the object it acts on, or the information it is after | `Retrieval` | "inspect the implementation of `resolve_expression`" |

**Scope: thought spans.** Command surfaces are unresolved. The span that prompted
this rule is an action span, `search_file "def quantile" xarray/core/dataset.py`,
where the human took `Grounding > Augment with external computation > Execute
code` and all three stacks took `Retrieval > Retrieve from local corpus`. Read
literally the rule above sends that span to `Retrieval`, since it names both the
pattern searched for and the file, so the rule does not reproduce the label that
prompted it. Do not extend C6 to action spans until that call is made.

The same annotator proposed a leaf that would dissolve the conflict rather than
arbitrate it: **`Grounding > Augment with external computation > Search relevant
files`**. `search_file` would land there, and the boundary rule would not have to
cover command surfaces at all. Recorded in `irr/codebook_notes.md`, not yet in
the canonical codebook.

Standing evidence: `Grounding ↔ Retrieval` is the largest cross-model confusion
pair in batch-4, 112 of 545 action-level disagreements (20.6%), up from 28 (8.0%)
in batch-3. See `analysis/IRR_batch-4.md`.

<!-- END ANNOTATION CONTRACT -->

<!-- BEGIN CROSS-MODEL ADJUDICATED CASES -->

## Cross-model tie-break precedents

Adjudicated disagreements between independent analyst stacks. Each entry records a span that different models labelled differently, the label a human adjudicator selected, and why. **When a span resembles one of these, follow the adjudicated label.**

_Auto-generated from `case_library/` — 75 adjudicated patterns covering 176 disputed spans. Do not edit by hand._

### R1

**P002** · 17 span(s) · disagreement at *action* level

> test our changes by running the `test_fits_card.py` script again

- claude: `Grounding > Augment with external computation > Execute code`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Executing > Executing plan > Run verification command`
- **adjudicated: `Executing > Executing plan > Run verification command`**
- rationale: need to identify the main action, the main action is the "run". And this is the agent's thought

**P003** · 16 span(s) · disagreement at *action* level

> run it to see if we can reproduce the issue

- claude: `Grounding > Augment with external computation > Execute code`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Grounding > Augment with external computation > Execute code`
- **adjudicated: `Executing > Executing plan > Run verification command`**
- rationale: need to identify the main action, the main action is the "run". And this is the agent's thought

**P144** · 1 span(s) · disagreement at *action* level

> run the script to see if we can reproduce the issue

- claude: `Grounding > Augment with external computation > Execute code`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Evaluating > Evaluating with gold > Confirm actual ≠ expected`
- **adjudicated: `Executing > Executing plan > Run verification command`**
- rationale: need to identify the main action, the main action is the "run". And this is the agent's thought

**P153** · 1 span(s) · disagreement at *action* level

> run the script to see if our fix for the `PythonCodePrinter` has resolved the issue

- claude: `Grounding > Augment with external computation > Execute code`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Evaluating > Evaluating with gold > Plan verification step`
- **adjudicated: `Executing > Executing plan > Run verification command`**
- rationale: need to identify the main action, the main action is the "run". And this is the agent's thought

**P158** · 1 span(s) · disagreement at *action* level

> run our `reproduce.py` script again to see if the issue has been resolved

- claude: `Grounding > Augment with external computation > Execute code`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Evaluating > Evaluating with gold > Confirm actual == expected`
- **adjudicated: `Executing > Executing plan > Run verification command`**
- rationale: need to identify the main action, the main action is the "run". And this is the agent's thought

### R2

**P001** · 20 span(s) · disagreement at *action* level

> The changes look good

- claude: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- gpt: `Reasoning > Analysing > Interpret meaning of artifacts`
- deepseek: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- **adjudicated: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`**
- rationale: qualitative judgement for current status -> evaluating

**P054** · 1 span(s) · disagreement at *action* level

> The script looks good as it is

- claude: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- gpt: `Reasoning > Analysing > Interpret meaning of artifacts`
- deepseek: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`
- **adjudicated: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`**
- rationale: qualitative judgement for current status -> evaluating

### R3

**P007** · 5 span(s) · disagreement at *leaf* level

> the migrations are not being applied correctly

- claude: `Reflection > Reflect on errors and failures > Detect prior fix did not work`
- gpt: `Reflection > Reflect on errors and failures > Detect failed action`
- deepseek: `Reflection > Reflect on errors and failures > Detect failed action`
- **adjudicated: `Reflection > Reflect on errors and failures > Detect failed action`**
- rationale: the leaf should not be too much specific

**P010** · 4 span(s) · disagreement at *leaf* level

> The `exclude()` case is still not working as expected

- claude: `Reflection > Reflect on errors and failures > Detect prior fix did not work`
- gpt: `Reflection > Reflect on errors and failures > Detect failed action`
- deepseek: `Reflection > Reflect on errors and failures > Detect prior fix did not work`
- **adjudicated: `Reflection > Reflect on errors and failures > Detect failed action`**
- rationale: the leaf should not be too much specific

**P016** · 2 span(s) · disagreement at *action* level

> our custom `newer_group` function is being called with an unexpected third argument

- claude: `Reflection > Reflect on errors and failures > Detect prior fix did not work`
- gpt: `Reflection > Reflect on errors and failures > Detect failed action`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reflection > Reflect on errors and failures > Detect failed action`**
- rationale: the leaf should not be too much specific

### Individual precedents

**P004** · 6 span(s) · disagreement at *leaf* level

> successfully reproduced the issue described in the bug report

- claude: `Evaluating > Evaluating with gold > Confirm actual ≠ expected`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Evaluating > Evaluating with gold > Confirm actual ≠ expected`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P005** · 5 span(s) · disagreement at *action* level

> modify the method to handle these cases more explicitly

- claude: `Reasoning > Generating > Generate initial fix candidate`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Reasoning > Generating > Generate initial fix candidate`
- **adjudicated: `Planning > Formulate a workflow or plan > Formulate a high-level plan`**

**P006** · 5 span(s) · disagreement at *sub-action* level

> The indentation issue has been resolved

- claude: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P008** · 4 span(s) · disagreement at *action* level

> Let's try a different approach

- claude: `Planning > Select Strategy > Switch to fallback strategy`
- gpt: `Deciding > Make a decision > Pick alternative strategy`
- deepseek: `Deciding > Make a decision > Pick alternative strategy`
- **adjudicated: `Planning > Select Strategy > Select among candidate strategies`**

**P009** · 4 span(s) · disagreement at *action* level

> update the `test_exists_exclude` method to test our changes

- claude: `Reasoning > Generating > Generate structured artifacts`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Executing > Executing plan > Apply patch via edit`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P011** · 3 span(s) · disagreement at *action* level

> try to install the package again

- claude: `Executing > Executing plan > Initiate planned action`
- gpt: `Planning > Formulate a workflow or plan > Formulate a high-level plan`
- deepseek: `Executing > Executing plan > Initiate planned action`
- **adjudicated: `Executing > Executing plan > Initiate planned action`**

**P012** · 3 span(s) · disagreement at *action* level

> because Django's settings are not configured

- claude: `Reasoning > Inferring > Diagnose Error Cause`
- gpt: `Reflection > Reflect on errors and failures > Inspect Error Pattern`
- deepseek: `Reflection > Reflect on errors and failures > Inspect Error Pattern`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P013** · 3 span(s) · disagreement at *action* level

> The error is occurring because we're trying to define the model before configuring Django settings

- claude: `Reasoning > Inferring > Diagnose Error Cause`
- gpt: `Reflection > Reflect on errors and failures > Inspect Error Pattern`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P014** · 3 span(s) · disagreement at *action* level

> open it and look for the `ReadOnlyPasswordHashField` class

- claude: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- gpt: `Grounding > Interact with digital environments > Navigate digital interfaces`
- deepseek: `Grounding > Interact with digital environments > Navigate digital interfaces`
- **adjudicated: `Grounding > Interact with digital environments > Navigate digital interfaces`**

**P015** · 2 span(s) · disagreement at *action* level

> add the code to reproduce the issue

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Reasoning > Generating > Generate initial codes`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P017** · 2 span(s) · disagreement at *action* level

> The changes we made have successfully resolved the issue

- claude: `Reasoning > Inferring > Conclude success from evidence`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Evaluating > Evaluating with gold > Confirm actual == expected`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P018** · 2 span(s) · disagreement at *sub-action* level

> The change has been applied successfully

- claude: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P019** · 2 span(s) · disagreement at *action* level

> add the test case mentioned in the issue description

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Executing > Executing plan > Apply patch via edit`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P020** · 2 span(s) · disagreement at *action* level

> remove the duplicate and keep only the updated version

- claude: `Executing > Executing plan > Apply patch via edit`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Deciding > Pick scores > Select action by score`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P021** · 2 span(s) · disagreement at *sub-action* level

> the actual implementation of how it's handled in subqueries might be in a different file

- claude: `Reasoning > Inferring > Infer structure from indirect evidence`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Reasoning > Inferring > Infer structure from indirect evidence`
- **adjudicated: `Reasoning > Inferring > Infer structure from indirect evidence`**

**P022** · 2 span(s) · disagreement at *action* level

> let's test if this change resolves the issue

- claude: `Evaluating > Evaluating with gold > Plan verification step`
- gpt: `Evaluating > Evaluating with gold > Plan verification step`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Evaluating > Evaluating with gold > Plan verification step`**

**P023** · 2 span(s) · disagreement at *action* level

> run the tests to see if the issue has been resolved

- claude: `Evaluating > Evaluating with gold > Plan verification step`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Executing > Executing plan > Run verification command`
- **adjudicated: `Evaluating > Evaluating with gold > Compare against gold reference`**

**P024** · 2 span(s) · disagreement at *action* level

> The test looks correct, but it's failing

- claude: `Evaluating > Evaluating with gold > Confirm actual ≠ expected`
- gpt: `Reasoning > Inferring > Diagnose Error Cause`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P025** · 2 span(s) · disagreement at *action* level

> open this file and examine its contents

- claude: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- gpt: `Grounding > Interact with digital environments > Navigate digital interfaces`
- deepseek: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- **adjudicated: `Grounding > Interact with digital environments > Navigate digital interfaces`**

**P026** · 2 span(s) · disagreement at *sub-action* level

> create a script to reproduce the problem

- claude: `Planning > Decompose task > Decompose into subgoals with success conditions`
- gpt: `Planning > Formulate a workflow or plan > Plan function or tool use`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Planning > Formulate a workflow or plan > Plan function or tool use`**

**P027** · 2 span(s) · disagreement at *action* level

> create a migration for our model and apply it in the test setup

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Planning > Formulate a workflow or plan > Plan function or tool use`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P028** · 2 span(s) · disagreement at *action* level

> check if there's a specific file for forms in the documentation

- claude: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- gpt: `Planning > Decompose task > Plan deeper inspection before edit`
- deepseek: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- **adjudicated: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`**

**P029** · 2 span(s) · disagreement at *action* level

> find the correct file without specifying a directory

- claude: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- gpt: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- deepseek: `Planning > Select Strategy > Switch to fallback strategy`
- **adjudicated: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`**

**P030** · 2 span(s) · disagreement at *action* level

> we've found the file containing the `PythonCodePrinter` class

- claude: `Evaluating > Evaluating without ground truth > Evaluate intermediate results`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`
- **adjudicated: `Reasoning > Analysing > Analyse source code`**

**P031** · 2 span(s) · disagreement at *action* level

> add our new `_print_Indexed` method to the `PythonCodePrinter` class

- claude: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- gpt: `Reasoning > Inferring > Predict patch effect`
- deepseek: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- **adjudicated: `Planning > Formulate a workflow or plan > Plan code or artifact structure`**

**P032** · 1 span(s) · disagreement at *sub-action* level

> we're working within the source code of astropy, and the extension modules haven't been built yet

- claude: `Reasoning > Inferring > Diagnose Error Cause`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reasoning > Analysing > Analyse source code`**

**P033** · 1 span(s) · disagreement at *action* level

> build the extension modules as suggested in the error message

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Grounding > Augment with external computation > Execute code`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Executing > Executing debug > Adopt debugging instructions`**

**P034** · 1 span(s) · disagreement at *action* level

> let's try building the extension modules again

- claude: `Executing > Executing plan > Initiate planned action`
- gpt: `Grounding > Augment with external computation > Execute code`
- deepseek: `Executing > Executing plan > Initiate planned action`
- **adjudicated: `Executing > Executing plan > Initiate planned action`**

**P035** · 1 span(s) · disagreement at *action* level

> the build process encountered an error

- claude: `Reflection > Reflect on errors and failures > Detect failed action`
- gpt: `Reflection > Reflect on errors and failures > Inspect Error Pattern`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reasoning > Analysing > analyse current situation`**

**P036** · 1 span(s) · disagreement at *action* level

> there's a `_convolve.pyx` file instead of a `_convolve.c` file

- claude: `Reasoning > Analysing > Analyse source code`
- gpt: `Deciding > Make a decision > Pick alternative strategy`
- deepseek: `Reasoning > Analysing > Analyse source code`
- **adjudicated: `Reasoning > Analysing > Analyse source code`**

**P037** · 1 span(s) · disagreement at *action* level

> modify the `astropy/wcs/setup_package.py` file to remove the dependency

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Reasoning > Inferring > Predict patch effect`
- deepseek: `Reasoning > Generating > Generate initial fix candidate`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P038** · 1 span(s) · disagreement at *action* level

> modify the function to handle this case

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Reasoning > Generating > Generate initial fix candidate`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P039** · 1 span(s) · disagreement at *sub-action* level

> install the package with verbose output to see where it might be hanging

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Planning > Formulate a workflow or plan > Formulate a high-level plan`
- deepseek: `Planning > Select Strategy > Switch to fallback strategy`
- **adjudicated: `Planning > Formulate a workflow or plan > Formulate a high-level plan`**

**P040** · 1 span(s) · disagreement at *action* level

> focus on building just the extension modules

- claude: `Planning > Formulate a workflow or plan > Plan function or tool use`
- gpt: `Grounding > Augment with external computation > Execute code`
- deepseek: `Planning > Modify Plan > Replan dynamically based on feedback`
- **adjudicated: `Planning > Formulate a workflow or plan > Plan function or tool use`**

**P041** · 1 span(s) · disagreement at *action* level

> the build process has completed successfully

- claude: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Reasoning > Inferring > Conclude success from evidence`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P042** · 1 span(s) · disagreement at *sub-action* level

> the issue might actually be related to `astropy`'s implementation of `TimeDelta`

- claude: `Reasoning > Inferring > Form precursor hypothesis about cause`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Reasoning > Inferring > Initial diagnostic framing`
- **adjudicated: `Reasoning > Inferring > Initial diagnostic framing`**

**P043** · 1 span(s) · disagreement at *action* level

> the issue is in the `_format_float()` function in the `card.py` file

- claude: `Reasoning > Inferring > Initial diagnostic framing`
- gpt: `Reasoning > Inferring > Pinpoint root cause mechanism`
- deepseek: `Memory > Read memory > Read from working memory`
- **adjudicated: `Reasoning > Inferring > Pinpoint root cause mechanism`**

**P044** · 1 span(s) · disagreement at *leaf* level

> using 16 digits of precision for all float values, which can lead to unnecessary expansion

- claude: `Reasoning > Inferring > Diagnose Error Cause`
- gpt: `Reasoning > Inferring > Form precursor hypothesis about cause`
- deepseek: `Reasoning > Inferring > Pinpoint root cause mechanism`
- **adjudicated: `Reasoning > Inferring > Pinpoint root cause mechanism`**

**P045** · 1 span(s) · disagreement at *sub-action* level

> It covers all the aspects of the issue we've fixed

- claude: `Evaluating > Evaluating with goals/requirements/constraints > Requirement-satisfaction check`
- gpt: `Evaluating > Evaluating with gold > Confirm actual == expected`
- deepseek: `Evaluating > Evaluating without ground truth > Provide qualitative judgement`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Requirement-satisfaction check`**

**P046** · 1 span(s) · disagreement at *action* level

> the pytest command is not able to find the astropy module

- claude: `Reflection > Reflect on errors and failures > Detect failed action`
- gpt: `Retrieval > Retrieve from local corpus > Read code semantics from open file`
- deepseek: `Reasoning > Inferring > Diagnose Error Cause`
- **adjudicated: `Reflection > Reflect on errors and failures > Detect failed action`**

**P047** · 1 span(s) · disagreement at *action* level

> run the test using Python directly

- claude: `Planning > Select Strategy > Switch to fallback strategy`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Deciding > Make a decision > Pick alternative strategy`
- **adjudicated: `Executing > Executing plan > Run verification command`**

**P048** · 1 span(s) · disagreement at *action* level

> we've verified that our changes work as expected and the test passes

- claude: `Evaluating > Evaluating with gold > Confirm actual == expected`
- gpt: `Executing > Terminating > Terminate rollout with submission`
- deepseek: `Evaluating > Evaluating with gold > Confirm actual == expected`
- **adjudicated: `Evaluating > Evaluating with goals/requirements/constraints > Goal-completion check`**

**P049** · 1 span(s) · disagreement at *action* level

> add the code to reproduce the issue

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Executing > Executing plan > Initiate planned action`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P051** · 1 span(s) · disagreement at *action* level

> look at the file where the problem is occurring

- claude: `Planning > Decompose task > Phase transition: reproduce → localize`
- gpt: `Reasoning > Inferring > Pinpoint root cause mechanism`
- deepseek: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P057** · 1 span(s) · disagreement at *action* level

> add the test case mentioned in the issue description

- claude: `Planning > Decompose task > Decompose into subgoals with success conditions`
- gpt: `Grounding > Interact with digital environments > Navigate digital interfaces`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P060** · 1 span(s) · disagreement at *action* level

> clean up the imports and add the missing Item model

- claude: `Executing > Executing plan > Apply patch via edit`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P062** · 1 span(s) · disagreement at *sub-action* level

> move the `test_exists_exclude` method to the end

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Planning > Formulate a workflow or plan > Formulate a high-level plan`
- deepseek: `Planning > Modify Plan > Replan dynamically based on feedback`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P063** · 1 span(s) · disagreement at *action* level

> adding the method after the last method in the class

- claude: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Reasoning > Analysing > Analyse source code`
- **adjudicated: `Executing > Executing plan > Normal executing`**

**P064** · 1 span(s) · disagreement at *action* level

> we need to fix the actual issue in the Django codebase

- claude: `Planning > Decompose task > Phase transition: reproduce → localize`
- gpt: `Evaluating > Evaluating with gold > Plan verification step`
- deepseek: `Planning > Decompose task > Phase transition: reproduce → localize`
- **adjudicated: `Planning > Formulate a workflow or plan > Formulate a high-level plan`**

**P065** · 1 span(s) · disagreement at *leaf* level

> The problem is likely in the `Exists` field implementation

- claude: `Reasoning > Inferring > Initial diagnostic framing`
- gpt: `Reasoning > Inferring > Pinpoint root cause mechanism`
- deepseek: `Reasoning > Inferring > Initial diagnostic framing`
- **adjudicated: `Reasoning > Inferring > Initial diagnostic framing`**

**P066** · 1 span(s) · disagreement at *action* level

> find it in the `query.py` file, which is likely to contain query-related classes

- claude: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- gpt: `Retrieval > Retrieve from local corpus > Retrieve from local corpus`
- deepseek: `Planning > Select Strategy > Select among candidate strategies`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P068** · 1 span(s) · disagreement at *action* level

> the `add_filter` method of the `Query` class, as it's likely to be involved in handling filters and exclusions

- claude: `Reasoning > Inferring > Initial diagnostic framing`
- gpt: `Retrieval > Retrieve from local corpus > Read code semantics from open file`
- deepseek: `Reasoning > Inferring > Initial diagnostic framing`
- **adjudicated: `Reasoning > Inferring > Initial diagnostic framing`**

**P069** · 1 span(s) · disagreement at *sub-action* level

> The problem could be in the `build_filter` method, which is called from `_add_q`

- claude: `Reasoning > Inferring > Infer dataflow / control flow`
- gpt: `Reasoning > Analysing > Analyse source code`
- deepseek: `Reasoning > Inferring > Infer dataflow / control flow`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P071** · 1 span(s) · disagreement at *action* level

> The method doesn't seem to have specific handling for `OuterRef` objects

- claude: `Reasoning > Inferring > Pinpoint root cause mechanism`
- gpt: `Reflection > Reflect on errors and failures > Detect failed action`
- deepseek: `Reasoning > Inferring > Pinpoint root cause mechanism`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P072** · 1 span(s) · disagreement at *action* level

> there are now two `test_exists_exclude` methods in the file

- claude: `Reflection > Reflect on errors and failures > Detect failed action`
- gpt: `Reasoning > Inferring > Form precursor hypothesis about cause`
- deepseek: `Reflection > Reflect on errors and failures > Detect failed action`
- **adjudicated: `Reasoning > Analysing > Analyse source code`**

**P075** · 1 span(s) · disagreement at *action* level

> use Django's test runner directly

- claude: `Planning > Select Strategy > Switch to fallback strategy`
- gpt: `Deciding > Make a decision > Pick alternative strategy`
- deepseek: `Planning > Select Strategy > Switch to fallback strategy`
- **adjudicated: `Planning > Select Strategy > Select among candidate strategies`**

**P083** · 1 span(s) · disagreement at *action* level

> The error is occurring during the SQL compilation process, specifically when handling the `OuterRef`

- claude: `Reasoning > Inferring > Diagnose Error Cause`
- gpt: `Reflection > Reflect on errors and failures > Inspect Error Pattern`
- deepseek: `Reasoning > Inferring > Pinpoint root cause mechanism`
- **adjudicated: `Reasoning > Inferring > Diagnose Error Cause`**

**P085** · 1 span(s) · disagreement at *action* level

> print out the count of `Number` objects and `Item` objects

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Planning > Formulate a workflow or plan > Formulate an analysis workflow`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P093** · 1 span(s) · disagreement at *action* level

> add the code to reproduce the issue

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P094** · 1 span(s) · disagreement at *action* level

> include a `setUpClass` method that creates the necessary tables

- claude: `Planning > Modify Plan > Replan dynamically based on feedback`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P100** · 1 span(s) · disagreement at *action* level

> we should run the Django test suite to ensure that our changes haven't broken anything

- claude: `Evaluating > Evaluating with gold > Plan verification step`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Planning > Decompose task > Decompose into subgoals with success conditions`
- **adjudicated: `Evaluating > Evaluating with gold > Compare against gold reference`**

**P110** · 1 span(s) · disagreement at *action* level

> add a comment explaining the change we made

- claude: `Reasoning > Generating > Generate initial codes`
- gpt: `Executing > Executing plan > Apply patch via edit`
- deepseek: `Reasoning > Generating > Generate structured artifacts`
- **adjudicated: `Executing > Executing plan > Apply patch via edit`**

**P111** · 1 span(s) · disagreement at *action* level

> run the tests again to ensure everything is still working correctly

- claude: `Evaluating > Evaluating with gold > Plan verification step`
- gpt: `Executing > Executing plan > Run verification command`
- deepseek: `Evaluating > Evaluating with gold > Plan verification step`
- **adjudicated: `Evaluating > Evaluating with gold > Compare against gold reference`**

**P140** · 1 span(s) · disagreement at *action* level

> include a comment explaining why we added the check

- claude: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- gpt: `Reasoning > Inferring > Predict patch effect`
- deepseek: `Planning > Formulate a workflow or plan > Plan function or tool use`
- **adjudicated: `Planning > Formulate a workflow or plan > Plan code or artifact structure`**

**P147** · 1 span(s) · disagreement at *action* level

> add the new method `_print_Indexed` to this class

- claude: `Planning > Formulate a workflow or plan > Plan code or artifact structure`
- gpt: `Reasoning > Inferring > Predict patch effect`
- deepseek: `Reasoning > Generating > Generate initial fix candidate`
- **adjudicated: `Planning > Formulate a workflow or plan > Plan code or artifact structure`**

<!-- END CROSS-MODEL ADJUDICATED CASES -->

<!-- BEGIN PROPOSED TAXONOMY ADDITIONS -->

## Proposed taxonomy additions (not yet canonical)

Leaves and sub-actions an adjudicator needed but could not find in the tree. They are recorded here **as proposals with their evidence**, not merged into the canonical taxonomy. Promoting one is a version bump: update `act-onomy_taxonomy.csv` and propagate with the `extension-tool` skill.

**During annotation these are usable**: if a span matches a proposal, use it and flag the span, rather than forcing a poor fit onto an existing leaf.

_2 proposal(s), backing 8 disputed span(s)._

### `Executing > Executing plan > Normal executing`

- kind: **new leaf** *(proposed)*
- attaches under: `Executing` › `Executing plan`
- evidence: 7 span(s) across 6 pattern(s) (P037, P020, P057, P060, P062, P063)
  - > modify the `astropy/wcs/setup_package.py` file to remove the dependency
  - > remove the duplicate and keep only the updated version
  - > add the test case mentioned in the issue description

### `Reasoning > Analysing > analyse current situation`

- kind: **new leaf** *(proposed)*
- attaches under: `Reasoning` › `Analysing`
- evidence: 1 span(s) across 1 pattern(s) (P035)
  - > the build process encountered an error

<!-- END PROPOSED TAXONOMY ADDITIONS -->

<!-- BEGIN NON-BEHAVIOUR SPAN EXAMPLES -->

## Spans that should not be quoted

Every stack quoted these, and a human adjudicator ruled that they encode **no agent behaviour** — they are narration, restatement, or filler. Do not open a quote span on text like this; a missing quote is better than a quote with no behaviour in it.

_1 pattern(s), 1 span(s)._

- > the test case provided in the issue description
  - (P050, 1 span(s); the stacks disagreed over how to label it, which is itself a signal it carries no behaviour)

<!-- END NON-BEHAVIOUR SPAN EXAMPLES -->

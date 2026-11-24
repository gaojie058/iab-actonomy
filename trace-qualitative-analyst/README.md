# Skill — `trace-qualitative-analyst`

A Claude Code Skill from Act\*ONOMY that takes a raw agent trajectory, grounds each turn to the codebook with verbatim quote evidence, and renders an interactive HTML report.

## Layout

```
skill/
├── case-library.html                 # Browse precedents and edit project cases
├── SKILL.md                          # The Skill prompt (Claude Code skill format)
├── assets/
│   ├── template.html                 # Interactive HTML report template
│   └── example_pylint_5859.json      # Worked example trajectory
├── references/
│   ├── ambiguity_cases.md            # Annotation contract and adjudicated examples
│   └── codebook.md                   # Codebook the Skill loads at runtime
└── scripts/
    ├── report_layout.py              # Build report overview and behavior profile
    ├── parse_trajectory.py           # Stage 1: raw trajectory → annotated skeleton
    └── render_artifact.py            # Stage 4: annotated JSON → HTML artifact
```

## How to invoke

Load this skill in a compatible agent environment (see [installation instructions](../README.md)). To use it:

1. Place a raw trajectory (`.traj` JSON file or pasted text) in your working directory.
2. Ask Claude: *"Analyze this trajectory with the trace-qualitative-analyst skill."*
3. The skill walks through four stages — parse, phase-label, annotate, render — emitting a self-contained HTML artifact.

The `(observation, thought, action)` triple schema accepts trajectories from heterogeneous frameworks via a thin adapter (see `scripts/parse_trajectory.py`).

## Add your own cases

The analyst reads [the adjudicated cases and annotation contract](references/ambiguity_cases.md) during annotation. Download [case-library.html](case-library.html) and open it in a browser. The reference section contains the study's 75 adjudicated patterns and its six v3 annotation rules. Search by passage, case ID, or label to see the historical decisions and their alternatives.

Choose **Add a case**, enter the passage, select its evidence field, and explain your decision. You can type your own label, leave a passage untagged, or record an unresolved decision. **Export JSON** saves your cases to a portable file. A collaborator can open the same page and use **Import JSON** to add them to their own library.

To use a library in an annotation run, give the analyst the exported file along with the raw trajectory. For example, “Annotate this trajectory using the cases in `actonomy-custom-cases.json`.” The analyst reads the decisions directly from that file.

## Reference codebook vs. canonical taxonomy

[`references/codebook.md`](references/codebook.md) is the version the Skill loads at runtime. It mirrors the canonical taxonomy at [`../data/taxonomy/act-onomy_taxonomy.csv`](../data/taxonomy/act-onomy_taxonomy.csv) (v4.2: 10 Actions → 46 Subactions → 120 Instances, with Actions: Retrieval, Memory, Planning, Reasoning, Evaluate, Deciding, Grounding, Executing, Learning, Reflection) and additionally carries:

- a **palette table** that maps each group to a hex color (consumed by the renderer and the HTML template);
- empirically-extra leaves accumulated during real annotation runs that the canonical taxonomy does not yet enumerate (e.g., `Pinpoint root cause mechanism` under Reasoning › Inferring).

The two files are kept in sync: any change to the canonical taxonomy should be reflected here, and any new leaf added during annotation should be promoted into the canonical taxonomy before the next versioned release.

## License

The Skill source (SKILL.md, scripts, template) is MIT-licensed; see [`../LICENSE`](../LICENSE). The reference codebook is CC BY 4.0; see [`../LICENSE-codebook`](../LICENSE-codebook).

---
name: extension-tool
description: Maintain consistency between the Act*ONOMY codebook and its dependent artifacts after accepted taxonomy changes. Run repository-local checks, generate a full codebook view, identify affected references, and synchronize explicitly selected trace-skill directories when requested.
---

# Codebook extension tool

Use this workflow after an accepted action, subaction, instance, or version change, or to investigate inconsistent codebook artifacts. Read [the dependency manifest](references/CODEBOOK_DEPENDENCIES.md) for the affected files.

## Workflow

1. Run `scripts/check_consistency.py` to inspect the current sources and dependents. It is read-only and discovers the repository from the script location; `--repo-root` selects another checkout.
2. Separate mechanical changes from semantic decisions. Update counts and paths as needed; support any annotation reassignment with the original evidence.
3. Update canonical representations and affected operational references together. Keep historical evidence and previous version snapshots intact.
4. Run `scripts/regenerate_docs.py` to generate the full leaf-level Markdown view, then render affected trace examples and repeat checks.
5. Check external paper artifacts or personal skill sources only when relevant paths are explicitly available. Use the shared personal library source for personal skill maintenance, not assistant-specific discovery copies.

## Commands

Run these from this skill directory, or use `python3 scripts/actonomy.py` from the repository root:

```bash
python3 scripts/check_consistency.py
python3 scripts/check_consistency.py --json
python3 scripts/regenerate_docs.py
```

The checker compares CSV/JSON codes, hierarchy labels, definitions, summaries, documented subaction counts, renderer groups, and worked-example action/subaction pairs. It does not adjudicate quote meaning or automatically audit every dependency tier. Exit **0** means clean, **1** errors, **2** warnings only. JSON output contains `counts`, `errors`, `warnings`, `info`, and a `summary` of message counts.

The generator writes `<repo>/outputs/codebook_v4.2.md` by default; use `--output` to select a destination. The curated `data/taxonomy/taxonomy.md` and paper frequencies are maintained manually. The generator does not rewrite canonical JSON or external directories.

## Optional external checks

```bash
python3 scripts/check_consistency.py \
  --runtime-skill /path/to/trace-qualitative-analyst \
  --paper-dir /path/to/paper/codebook
```

The mirror check compares the declared trace-skill files. The paper check looks for subaction-count phrases in `taxonomy.md`, `codebook_v4.2.md`, and `table.tex`; figure values still need human review.

Copying files is a separate explicit operation:

```bash
python3 scripts/sync_skill_mirrors.py \
  --source /path/to/source/trace-qualitative-analyst \
  --destination /path/to/destination/trace-qualitative-analyst --dry-run
```

The utility requires complete source files, never deletes destination extras, and verifies copied bytes. Remove `--dry-run` only for a copy within the user's authorized task and filesystem permissions. Do not automatically mirror on every codebook check.

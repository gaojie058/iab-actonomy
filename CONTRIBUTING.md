# Contributing to Act\*ONOMY

Act\*ONOMY is a living research artifact. Contributions should keep behavior labels grounded in evidence and analyses reproducible.

> Contributions are paused during pre-release. The protocol below describes how the open release will accept contributions.

## Development setup

Use Python 3.10+ from a source checkout. The Python tools and tests need no third-party packages. For the optional discovery document builders, run `npm ci --prefix tools/discovery-qualitative-analyst/scripts`.

```bash
make check
make demo
```

`make check` runs repository-local codebook consistency, documentation-link checks, and regression tests. GitHub Actions runs these checks on Python 3.10, 3.12, and 3.13. A separate Node.js job checks the discovery scripts and their installed dependency. See [the architecture guide](docs/architecture.md) for where changes belong.

Keep outputs under `outputs/` and retain raw research inputs and saved reference results. Update both root READMEs when user-facing commands or capabilities change. Include the commands you ran and their results in a pull request. Tests should cover affected behavior rather than just repeat implementation details.

## Proposing a taxonomy extension

Use the [extension template](.github/ISSUE_TEMPLATE/codebook_extension.md) and include:

1. **Behavior sentence:** a verbatim quote from a paper or trajectory.
2. **Source:** citation, agent name, and page/turn reference.
3. **Target placement:** an existing code, new instance/subaction, or new top-level action.
4. **Boundary argument:** why the closest existing code does not cover the behavior; reference the boundary tests in §3.1 of the paper.
5. **Example labeling:** a short labeled passage and explanation, if available.

Add a subaction when a behavior fits an existing top-level action but is not covered by its current subactions. Add a top-level action only when it fails the boundary tests against all existing actions. A new subaction needs evidence from at least two independent sources; domain-specific instances may specialize existing subactions.

## Review criteria

- **Faithfulness:** the quoted sentence occurs verbatim in the source.
- **Boundary clarity:** the proposed code preserves meaningful distinctions.
- **Generality:** the code captures a recurring pattern rather than a single domain detail.
- **Consistency:** structured codebook representations, operational references, affected examples, and documented counts agree.

Use the [dependency manifest](tools/extension-tool/references/CODEBOOK_DEPENDENCIES.md) and [maintenance guide](docs/codebook.md) to propagate an accepted change. Semantic relabeling requires evidence-based review; a passing checker cannot establish it.

## Versioning and provenance

The current analytical codebook is V4.2. The taxonomy JSON also retains its historical export-format version (`v1.0`); these are different labels.

- Increment the major codebook version for changes to the top-level action layer.
- Increment the minor version for changes at the subaction or instance layer.
- Preserve earlier development snapshots and record the source/version of an analysis. Current sources live in `data/taxonomy/`; development history is in `data/taxonomy/taxonomy_development/`.
- Document release changes and migration needs with the accepted proposal. A directory reorganization does not change codebook semantics or justify replacing historical corpus labels.

Personal skills are maintained in the shared skill-library source, with assistant discovery directories linking to it. The repository's distributable bundles are separate project artifacts. Review synchronization explicitly; repository commands do not automatically overwrite personal installations.

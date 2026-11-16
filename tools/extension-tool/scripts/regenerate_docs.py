#!/usr/bin/env python3
"""Generate a leaf-level codebook from the canonical CSVs.

The curated taxonomy.md, canonical JSON, and external paper files are not written.
"""

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ACTION_CLUSTER = {
    'Grounding':  ('External Interaction',   '🟦'),
    'Retrieval':  ('External Interaction',   '🟦'),
    'Reasoning':  ('Cognition & Execution',  '🟧'),
    'Planning':   ('Cognition & Execution',  '🟧'),
    'Evaluate':   ('Cognition & Execution',  '🟧'),
    'Deciding':   ('Cognition & Execution',  '🟧'),
    'Executing':  ('Cognition & Execution',  '🟧'),
    'Reflecting': ('Learning & Adaptation',  '🟪'),
    'Reflection': ('Learning & Adaptation',  '🟪'),  # legacy alias
    'Learning':   ('Learning & Adaptation',  '🟪'),
    'Memory':     ('Learning & Adaptation',  '🟪'),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, help='Output Markdown (default: <repo>/outputs/codebook_v4.2.md)')
    args = parser.parse_args()
    CB_CSV = args.repo_root / 'data/taxonomy/act-onomy_codebook.csv'
    TX_CSV = args.repo_root / 'data/taxonomy/act-onomy_taxonomy.csv'
    output = args.output or args.repo_root / 'outputs/codebook_v4.2.md'
    # ============ Load CSVs ============
    with CB_CSV.open(encoding="utf-8-sig", newline="") as stream:
        codebook = list(csv.DictReader(stream))
    with TX_CSV.open(encoding="utf-8-sig", newline="") as stream:
        taxonomy = {r['code'].strip(): r for r in csv.DictReader(stream)}

    hier = OrderedDict()
    for r in codebook:
        act, sub = r['Action'].strip(), r['Subaction'].strip()
        code = r['taxonomy_code'].strip()
        leaf = dict(
            code=code,
            instance=r['Instance'].strip(),
            definition=taxonomy[code]['definition'].strip(),
            examples=r['examples_raw'].strip(),
            papers=r['papers_cited'].strip(),
            reviewers=r['human reviewers'].strip(),
        )
        hier.setdefault(act, OrderedDict()).setdefault(sub, []).append(leaf)

    n_actions = len(hier)
    n_subs    = sum(len(subs) for subs in hier.values())
    n_leaves  = sum(len(l) for subs in hier.values() for l in subs.values())
    print(f'CSV: {n_actions} actions / {n_subs} sub-actions / {n_leaves} leaves')

    # NOTE: legacy table.tex parser removed — taxonomy.md is now hand-curated with
    # paper-aligned frequencies (n=120 sentences from arXiv:2605.13625v1 Figure 2).

    # Group actions by paper cluster for presentation
    clustered = OrderedDict()  # cluster_name -> [(emoji, action_name, subs_dict)]
    for act, subs in hier.items():
        cluster, emoji = ACTION_CLUSTER.get(act, ('(Uncategorised)', '⬜'))
        clustered.setdefault(cluster, {'emoji': emoji, 'actions': []})['actions'].append((act, subs))

    # NOTE: taxonomy.md is now hand-curated for paper-aligned frequencies (n=120 sentences
    # from arXiv:2605.13625v1 Figure 2). This script no longer regenerates taxonomy.md.
    # Edit it manually when the paper's Figure 2 changes.

    # ============ Emit codebook_v4.2.md (paper-grouped leaf-level codebook) ============
    L = [
        r'# Act\*ONOMY Codebook · V4.2',
        '',
        'Full leaf-level codebook joining `act-onomy_codebook.csv` (raw examples + papers cited) and `act-onomy_taxonomy.csv` (definitions).  ',
        f'**{n_actions} actions · {n_subs} sub-actions · {n_leaves} leaf instances** · grouped by paper cluster (arXiv:2605.13625v1 Figure 3).',
        '',
        'Each leaf entry shows:',
        '- **Code** — `Tx.x.x.x` opaque taxonomy ID (stable across versions; the leading prefix is *not* semantic).',
        '- **Definition** — canonical short description (from `act-onomy_taxonomy.csv`)',
        '- **Examples** — raw example phrases recorded during annotation (from `act-onomy_codebook.csv`)',
        '- **Papers cited** — corpus papers in which this leaf was observed; `theory-driven` if no paper cited',
        '- **Reviewers** — annotators who endorsed the leaf',
        '',
        '---',
        '',
    ]
    for cluster, info in clustered.items():
        L += [f'## {info["emoji"]} {cluster}', '']
        for act, subs in info['actions']:
            L += [f'### {act}', '']
            for sub, instances in subs.items():
                L += [f'#### Sub-action: {sub}', '']
                for inst in instances:
                    L += [f'**`{inst["code"]}`  ·  {inst["instance"]}**', '']
                    if inst['definition']:
                        L.append(f'- *Definition:* {inst["definition"]}')
                    if inst['examples']:
                        ex_list = [e.strip().lstrip('"').rstrip('"') for e in inst['examples'].split('\n') if e.strip()]
                        if ex_list:
                            L.append('- *Examples:*')
                            for e in ex_list:
                                L.append(f'  - {e}')
                    L.append(f'- *Papers cited:* {inst["papers"] or "—"}')
                    if inst['reviewers']:
                        L.append(f'- *Reviewers:* {inst["reviewers"]}')
                    L.append('')
            L.append('')
        L += ['---', '']

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(L), encoding='utf-8')
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()

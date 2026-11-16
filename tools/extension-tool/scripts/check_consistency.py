#!/usr/bin/env python3
"""Check local taxonomy sources and dependents without changing files.

Exit 0: clean; 1: errors; 2: warnings only. Personal mirrors are opt-in.
"""

import argparse
import ast
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
COUNT_PATTERN = re.compile(r'\b(\d+)\s*(?:sub-?actions?\b|类子动作)', re.IGNORECASE)
MIRROR_FILES = (
    'SKILL.md', 'README.md', 'references/codebook.md', 'assets/example_pylint_5859.json',
    'assets/template.html', 'scripts/parse_trajectory.py', 'scripts/render_artifact.py',
)


def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return [{key: value.strip() for key, value in row.items()} for row in csv.DictReader(stream)]


def check_repository(root, runtime_skill=None, paper_dir=None):
    report = {'counts': {}, 'errors': [], 'warnings': [], 'info': []}
    errors, warnings = report['errors'], report['warnings']
    taxonomy = root / 'data/taxonomy'
    skill = root / 'tools/trace-qualitative-analyst'
    try:
        codebook = csv_rows(taxonomy / 'act-onomy_codebook.csv')
        rows = csv_rows(taxonomy / 'act-onomy_taxonomy.csv')
        tree = json.loads((taxonomy / 'act-onomy_taxonomy.json').read_text(encoding='utf-8'))
        snapshot = json.loads((taxonomy / 'taxonomy_development/codebook_v4.2.json').read_text(encoding='utf-8'))

        def index(records, code_key, label):
            result = {}
            for row in records:
                code = row[code_key]
                if not code or code in result:
                    errors.append(f'{label}: empty or duplicate code {code!r}')
                result[code] = tuple(row[key] for key in ('Action', 'Subaction', 'Instance'))
            return result

        canonical = index(codebook, 'taxonomy_code', 'codebook.csv')
        tabular = index(rows, 'code', 'taxonomy.csv')
        if not canonical:
            errors.append('The canonical codebook is empty')
        if canonical != tabular:
            errors.append('codebook.csv and taxonomy.csv disagree on codes or hierarchy labels')
        tree_rows = [
            {'code': leaf['code'], 'Action': action['name'], 'Subaction': sub['name'],
             'Instance': leaf['name'], 'definition': leaf['definition']}
            for action in tree['taxonomy'] for sub in action['subactions'] for leaf in sub['instances']
        ]
        if index(tree_rows, 'code', 'taxonomy.json') != canonical:
            errors.append('taxonomy.json and codebook.csv disagree on codes or hierarchy labels')
        if {r['code']: r['definition'] for r in tree_rows} != {r['code']: r['definition'] for r in rows}:
            errors.append('taxonomy.json and taxonomy.csv definitions disagree')
        rich_leaves = Counter(
            (action['name'], sub['name'], leaf['action'])
            for action in snapshot['actions'] for sub in action['sub_categories'] for leaf in sub['leaves']
        )
        if rich_leaves != Counter(canonical.values()):
            errors.append('codebook_v4.2.json and codebook.csv hierarchy labels disagree')
        pairs = {(value[0], value[1]) for value in canonical.values()}
        actions = {value[0] for value in canonical.values()}
        counts = {'actions': len(actions), 'subactions': len(pairs), 'instances': len(codebook)}
        report['counts'] = counts
        expected_tree = dict(zip(('tier_1', 'tier_2', 'tier_3'), counts.values()))
        expected_rich = dict(zip(('n_actions', 'n_sub_categories', 'n_leaves'), counts.values()))
        for label, source, expected in (('taxonomy.json', tree, expected_tree), ('codebook_v4.2.json', snapshot, expected_rich)):
            for key, count in expected.items():
                if source['summary'].get(key) != count:
                    errors.append(f"{label}: summary.{key} should be {count}, got {source['summary'].get(key)}")

        count_files = [root / 'README.md', root / 'README.zh.md', root / 'data/README.md', taxonomy / 'taxonomy.md',
                       skill / 'README.md', skill / 'references/codebook.md']
        if paper_dir is not None:
            count_files.extend(paper_dir / name for name in ('taxonomy.md', 'codebook_v4.2.md', 'table.tex'))
        for path in count_files:
            if not path.exists():
                warnings.append(f'Count check skipped: missing {path}')
                continue
            for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                for match in COUNT_PATTERN.finditer(line):
                    if int(match[1]) != counts['subactions']:
                        errors.append(f"{path}:{line_number}: stale subaction count {match[1]}; expected {counts['subactions']}")
        renderer = ast.parse((skill / 'scripts/render_artifact.py').read_text(encoding='utf-8'))
        palette = next(ast.literal_eval(node.value) for node in renderer.body
                       if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GROUP_COLOURS' for t in node.targets))
        if set(palette) != actions:
            errors.append('Renderer palette groups disagree with canonical actions')
        examples = [skill / 'assets/example_pylint_5859.json',
                    root / 'tools/human-trace-qualitative-analyst/assets/example_c4d3dbfa.json']
        for path in examples:
            example = json.loads(path.read_text(encoding='utf-8'))
            for turn in example['turns']:
                for quote in turn.get('quotes', []):
                    pair = (quote.get('grp'), quote.get('sub'))
                    if pair not in pairs:
                        errors.append(f"{path.name} turn {turn.get('n')}: unknown action/subaction {pair}")
        report['info'].append('Empirical extra leaves are allowed; action/subaction pairs must be canonical.')
        if runtime_skill is not None:
            for relative in MIRROR_FILES:
                source, mirror = skill / relative, runtime_skill / relative
                if not mirror.is_file():
                    errors.append(f'Skill mirror missing: {mirror}')
                elif source.read_bytes() != mirror.read_bytes():
                    errors.append(f'Skill mirror differs: {relative}')
        else:
            report['info'].append('Personal skill mirrors and external paper files are checked only when explicitly supplied.')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, StopIteration) as exc:
        errors.append(f'Could not validate repository: {exc}')
    report['summary'] = {key: len(report[key]) for key in ('errors', 'warnings', 'info')}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--runtime-skill', type=Path, help='Explicit optional trace-skill mirror directory')
    parser.add_argument('--paper-dir', type=Path, help='Explicit optional directory containing paper codebook views')
    parser.add_argument('--json', action='store_true', help='Print a machine-readable report')
    args = parser.parse_args()
    report = check_repository(args.repo_root.resolve(), args.runtime_skill, args.paper_dir)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print('Act*ONOMY consistency check')
        print('Counts:', report['counts'])
        for level in ('errors', 'warnings', 'info'):
            for message in report[level]:
                print(f'[{level}] {message}')
        print('Summary:', report['summary'])
    return 1 if report['errors'] else 2 if report['warnings'] else 0


if __name__ == '__main__':
    sys.exit(main())

"""Build the overview, timeline and behavior profile for standalone Act-onomy reports."""
from collections import Counter
from html import escape, unescape
from itertools import groupby
import json
import re


def inline_text(value):
    """Preserve the inline emphasis supported by annotated summaries and findings."""
    parts = re.split(r'(</?(?:strong|em|b|i|code)>)', str(value or ''))
    for i in range(0, len(parts), 2):
        parts[i] = escape(unescape(parts[i]), quote=False)
    return ''.join(parts)


def script_json(value):
    return json.dumps(value, ensure_ascii=True).replace('<', r'\u003c')


def report_sections(turns, segments):
    """Use authored segments where present and summarize uncovered turns by phase."""
    sections = []
    assigned = set()
    for seg in segments:
        group = [t for t in turns if seg['start'] <= t['n'] <= seg['end']]
        if not group:
            continue
        assigned.update(t['n'] for t in group)
        sections.append((group, seg))
    for key, members in groupby(turns, lambda t: (t['n'] in assigned, t['phase'])):
        if not key[0]:
            sections.append((list(members), {}))

    stages = []
    for group, seg in sorted(sections, key=lambda item: item[0][0]['n']):
        first, last = group[0], group[-1]
        title = seg.get('title') or first.get('phase_label') or first['phase'].capitalize()
        narrative = seg.get('summary') or ' '.join(dict.fromkeys(
            t['headline'] for t in (first, last) if t.get('headline')
        ))
        stages.append(dict(start=first['n'], end=last['n'], size=len(group),
                           title=inline_text(title), summary=inline_text(narrative)))
    return stages


def layout_values(data, agent_turns, segments, group_counts, source_json):
    stages = report_sections(agent_turns, segments)
    widths, bars, labels, rows = [], [], [], []
    for i, s in enumerate(stages):
        color = f'--stage:var(--stage-{i % 4 + 1})'
        widths.append(f'{s["size"]}fr')
        bars.append(f'<span style="{color}"></span>')
        start, end = s['start'], s['end']
        turn_range = f'T{start:02}' if start == end else f'T{start:02}–{end:02}'
        labels.append(f'<li class="stage" style="{color}"><span class="stage-identity">'
                      f'<i aria-hidden="true" class="stage-key"></i><span class="stage-name">{s["title"]}</span></span>'
                      f'<span class="range">{turn_range}</span></li>')
        rows.append(f'<li><div class="run-stage-title"><h3>{s["title"]}</h3>'
                    f'<a href="#turn-{start}" aria-label="Open turn {start}">{turn_range}</a></div>'
                    f'<p>{s["summary"]}</p></li>')
    n = len(agent_turns)
    turn_label = f'{n} turn' if n == 1 else f'{n} turns'
    timeline = (f'<div aria-hidden="true" class="stage-bar" style="--stage-widths:{" ".join(widths)}">'
                f'{"".join(bars)}</div><ol class="stage-list" aria-label="Stages across {turn_label}">'
                f'{"".join(labels)}</ol>')
    meta = [('Agent', data['model'])]
    if data.get('annotator'):
        meta.append(('Annotator', data['annotator']))
    prompts = len(data['turns']) - n
    if prompts:
        meta.append(('Interactions', prompts))
    facts = ''.join(f'<div><dt>{key}</dt><dd>{escape(str(value))}</dd></div>' for key,value in meta)
    total = sum(count for _,count in group_counts)
    profile = f'<p class="panel-sub">{total} quote-level annotations across {len(group_counts)} action groups.</p>'
    if group_counts:
        highest = max(count for _,count in group_counts)
        items = []
        for group, count in group_counts:
            token = re.sub(r'[^\w-]', '', group, flags=re.ASCII)
            items.append(f'<li class="behavior-row" style="--color:var(--grp-{token},var(--slate-11));'
                         f'--length:{100*count/highest:.4g}%"><span class="bar-name">{escape(group)}</span>'
                         f'<span class="bar-track" aria-hidden="true"><i></i></span><span class="bar-count">{count}</span></li>')
        profile += '<ul class="profile-bars" aria-labelledby="profile-title">' + ''.join(items) + '</ul>'
    findings = ''.join(
        '<li><div class="run-stage-title"><h3>' + inline_text(f.get('title')) + '</h3></div><p>'
        + inline_text(f.get('body') or f.get('detail')) + '</p></li>' for f in data.get('findings',[])
    )
    return {
        '{{TURN_COUNT_LABEL}}': turn_label, '{{RUN_FACTS}}': facts, '{{STAGE_BAR}}': timeline,
        '{{STAGE_ROWS}}': ''.join(rows), '{{SAFE_SUMMARY}}': inline_text(data['summary']),
        '{{PROFILE_BARS}}': profile, '{{FINDINGS_VISIBILITY}}': '' if findings or data.get('patterns') else 'hidden',
        '{{FINDING_ROWS}}': findings, '{{STATUS_TEXT}}': escape(data['outcome'].capitalize()),
        '{{STATUS_COLOR}}': 'teal' if data['outcome'] == 'resolved' else 'orange',
        '{{SAFE_SEGMENTS_JSON}}': script_json(stages), '{{SOURCE_JSON}}': source_json,
        '{{QUOTE_TARGET_JSON}}': script_json(data['quote_target']),
    }

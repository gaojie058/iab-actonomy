# Case Study 1 — Three-agent trajectories

This directory includes the 300 source trajectory JSON files used in the [three-agent analysis report](analysis_report.md), together with the existing aggregate report and [run summaries](run_summaries.md).

| Report label | Source directory | JSON files | Bytes |
| --- | --- | ---: | ---: |
| AG2 | [trajectories/AG2/](trajectories/AG2/) | 100 | 856,164 |
| HyperAgent | [trajectories/HyperAgent/](trajectories/HyperAgent/) | 100 | 22,343,556 |
| SWE-Agent | [trajectories/nebius_swe_agent/](trajectories/nebius_swe_agent/) | 100 | 8,347,571 |
| **Total** | | **300** | **31,547,291** |

## Provenance and integrity

Imported on 2026-10-30 from the maintainer-provided `trajectories/` collection. Original JSON bytes, filenames, and dataset directory names are preserved; macOS `.DS_Store` files are excluded. The SWE-Agent files retain their embedded source metadata identifying `nebius/SWE-agent-trajectories`.

All 300 file identifiers match the per-trace fingerprint table in `analysis_report.md` exactly, using `nebius_swe_agent` → `SWE-Agent` for the report label. Numbered suffixes such as `_2` are retained as distinct trace identifiers.

[trajectories_manifest.json](trajectories_manifest.json) records the relative path, report identifier, byte size, and SHA-256 checksum of every imported file. From the repository root, verify the copies with:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
import json

base = Path('examples/case1_three_agents')
manifest = json.loads((base / 'trajectories_manifest.json').read_text())
expected = {entry['path'] for entry in manifest['files']}
actual = {str(p.relative_to(base)) for p in (base / 'trajectories').rglob('*.json')}
assert actual == expected
assert len(expected) == manifest['file_count'] == 300
for entry in manifest['files']:
    data = (base / entry['path']).read_bytes()
    json.loads(data)
    assert len(data) == entry['bytes'], entry['path']
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['path']
print('Verified 300 trajectory JSON files.')
PY
```

## Formats and analysis scope

These files retain their source formats. AG2 and SWE-Agent store message dictionaries in `trajectory`; HyperAgent stores text log lines. The length of a HyperAgent `trajectory` list is a line count, not the report's agent-turn count. This import does not normalize messages or regenerate behavior annotations.

The source logs do not replace the quote-level Act\*ONOMY annotation outputs used to calculate the report's behavior counts. Those annotation outputs are not supplied by this import.

The current analysis report covers three agents and 300 traces. `run_summaries.md` retains the earlier four-dataset collection of 400 summaries, including 100 CodeAct summaries. CodeAct raw trajectories are not included here. The report also explicitly marks its historical top-leaf ranking as including CodeAct; that ranking and the saved statistics are unchanged by this import.

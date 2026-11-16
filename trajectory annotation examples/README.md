# Examples and case studies

Run these commands from the repository root. Generated files go into `outputs/`; the checked-in HTML and annotation files remain reference artifacts.

| Example | What is available | Scope |
| --- | --- | --- |
| [Three agents](case1_three_agents/) | 300 source JSON files, integrity manifest, aggregate report, and run summaries | AG2/AutoGen, HyperAgent, and SWE-Agent: 100 trajectories each; see the case README for historical CodeAct summaries |
| [Two SWE-agent tasks](case2_swe_agent_two_traces/) | Raw JSON, annotated JSON, and HTML | requests-2317 and django-14411 |
| [Crosswalks](crosswalk/) | Script, CSV tables, summary JSON, report, and appendix | MAST failure-mode relations and CoALA action-space mappings |

```bash
mkdir -p outputs
python3 scripts/actonomy.py render \
  examples/case2_swe_agent_two_traces/trace2_django__django-14411.annotated.json \
  --output outputs/django.html
python3 scripts/actonomy.py crosswalk
```

The current renderer may present a saved annotation differently from its historical HTML. Crosswalk outputs should reproduce the saved numeric mappings, but the mappings encode analytic decisions rather than a claim of equivalence between a failure taxonomy and a behavior taxonomy. The refactor preserves them without re-adjudication.

A small annotated pylint example is also bundled with the trace skill (`python3 scripts/actonomy.py demo`). The human-interaction skill includes a separate example:

```bash
python3 scripts/actonomy.py render \
  tools/human-trace-qualitative-analyst/assets/example_c4d3dbfa.json \
  --output outputs/human-session.html
```

<p align="center">
  <img src="assets/actonomy_logo.png" alt="Act*ONOMY" width="440">
</p>

<h3 align="center">A shared vocabulary for understanding, describing and analysing agent runtime behavior</h3>

<p align="center">
  English · <a href="README.zh.md">中文</a><br>
  <a href="Project Website">Project Website</a> ·
  <a href="https://arxiv.org/abs/2605.13625">Paper</a> ·
  <a href="data/taxonomy/taxonomy.md">Taxonomy</a>
</p>

**Act\*ONOMY** describes what AI agents do at runtime through **10 actions, 46 subactions, and 120 leaf instances**. It combines a grounded-theory codebook, tools for quote-level trajectory analysis, and a protocol for extending the vocabulary as new behaviors emerge.

<p align="center">
  <img src="assets/semantic_workflow.gif" alt="Original trajectory, two examples of sentence-level Action–Subaction–Leaf labels, turn summaries, and a shared purpose" width="1000"><br>
  <em>Raw trajectory → Turn excerpts → Behavior labels → Turn summaries → Shared purpose.</em>
</p>

The animation follows T1–T4 of the [original requests-2317 log](trajectory%20annotation%20examples/case2_swe_agent_two_traces/trace1_psf__requests-2317.json). Two example pages show highlighted sentences from T1–T2 with **Action → Subaction → Leaf** labels taken verbatim from the [case-study annotations](trajectory%20annotation%20examples/case2_swe_agent_two_traces/trace1_psf__requests-2317.annotated.json). The four turn summaries then reveal a shared purpose. [Three-level annotation example](assets/semantic_workflow_labels.png) · [Static summary](assets/semantic_workflow.png).

## When to use Act\*ONOMY

| Your goal                                          | Start here                                                             |
|----------------------------------------------------|------------------------------------------------------------------------|
| Understand an agent's reasoning and actions        | [Trajectory analysis](tools/trace-qualitative-analyst/README.md)       |
| Study how a human steers an agent                  | [Human–agent analysis](tools/human-trace-qualitative-analyst/SKILL.md) |
| Compare behavioral profiles across agents or tasks | [Case studies](trajectory%20annotation%20examples/README.md)                                     |
| Identify behaviors missing from the vocabulary     | [Discovery workflow](tools/discovery-qualitative-analyst/SKILL.md)     |

## Quickstart

**Download skills → Install skills → Input a trajectory → Generate a report**

Analysis runs in a compatible AI assistant with the skills loaded. The assistant reads the codebook, annotates evidence, and generates the report; `actonomy.py` provides parsing and rendering helpers, not automatic trajectory analysis.

### 1. Download skills

Download this repository; the skill bundles are in [`tools/`](tools/).

```bash
git clone https://github.com/gaojie058/Act-onomy.git
cd Act-onomy
```

### 2. Install skills

Open the repository in your assistant and ask:

```text
Install tools/trace-qualitative-analyst and tools/human-trace-qualitative-analyst
using this environment's skill installation workflow. Keep both complete
folders side by side, including their references, scripts, and assets.
```

The human-interaction skill depends on the trace skill. The assistant needs local file access and Python **3.10+** to run the bundled scripts.

### 3. Input a trajectory

Provide your trajectory file and ask:

```text
Use trace-qualitative-analyst to analyze my trajectory at <path/to/trajectory.json>.
Annotate behavior with verbatim evidence from the trajectory and generate
outputs/trajectory.annotated.json and outputs/trajectory.html.
```

For a Claude Code session with human interactions, use `human-trace-qualitative-analyst` and provide the session `.jsonl` file. See the [full quickstart](docs/quickstart.md) for input formats and a bundled example.

### 4. Generate a report

The assistant saves the annotated JSON and an interactive HTML report. Open **`outputs/trajectory.html`** in your browser to explore turn-by-turn behavior, evidence quotes, and action distributions.

## Repository layout

```text
.
├── data/
│   ├── corpus/
│   ├── large_corpus/
│   └── taxonomy/
├── tools/
│   ├── discovery-qualitative-analyst/
│   ├── extension-tool/
│   ├── human-trace-qualitative-analyst/
│   └── trace-qualitative-analyst/
├── trajectory annotation examples/
│   ├── case1_three_agents/
│   ├── case2_swe_agent_two_traces/
│   └── crosswalk/
├── assets/
├── CITATION.cff
├── LICENSE
└── LICENSE-codebook
```

| Directory | Contents |
| --- | --- |
| [data/](data/README.md) | Research corpora, canonical taxonomy, and development snapshots |
| [tools/](tools/) | Four skill bundles with instructions, scripts, and supporting assets |
| [trajectory annotation examples/](trajectory%20annotation%20examples/README.md) | Agent trajectories, annotated reports, and MAST/CoALA crosswalks |
| [assets/](assets/) | Act\*ONOMY branding, workflow animations, and static previews |

<!-- ## Data and examples

| Resource                                                     | Included in this repository                                                 |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|
| [Grounded-theory corpus](data/corpus/)                       | 35 papers; 664 construction and 116 held-out behavior sentences             |
| [Codebook](data/taxonomy/)                                   | CSV/JSON sources, a readable taxonomy, and development snapshots            |
| [Larger corpus](data/large_corpus/)                          | 3,455 behavior sentences; the current paper index has 211 records           |
| [Three-agent comparison](trajectory%20annotation%20examples/case1_three_agents/)       | 300 source trajectory JSON files (100 per agent) and aggregate reports      |
| [Two SWE-agent traces](trajectory%20annotation%20examples/case2_swe_agent_two_traces/) | Raw JSON, annotated JSON, and saved HTML for requests-2317 and django-14411 |
| [MAST / CoALA crosswalks](trajectory%20annotation%20examples/crosswalk/)               | Mapping script and saved tables; mappings are analytic judgments            |

The [data guide](data/README.md) explains corpus splits, the paper-index count discrepancy, and local-only materials. -->

<!-- ## Development and contributing

```bash
make check      # Codebook consistency, documentation links, and regression tests
make demo       # Render the bundled example
make crosswalk  # Write regenerated mappings to outputs/crosswalk/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and evidence requirements for taxonomy proposals. The existing pre-release pause on external contributions remains in effect. -->

## Citation

If you use Act\*ONOMY in research, cite [How to Interpret Agent Behavior](https://arxiv.org/abs/2605.13625):

```bibtex
@misc{gao2026interpret,
  title = {How to Interpret Agent Behavior},
  author = {Jie Gao and Kaiser Sun and Jen-tse Huang and Katherine Van Koevering and Sijie Ji and Heyuan Huang and Weiyan Shi and Zhuoran Lu and Ziang Xiao and Daniel Khashabi and Mark Dredze},
  year = {2026},
  eprint = {2605.13625},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  url = {https://arxiv.org/abs/2605.13625}
}
```

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

## License

- **Source code and skill templates:** [MIT](LICENSE).
- **Codebook content and labeled datasets:** [CC BY 4.0](LICENSE-codebook).
- **Third-party case-study materials:** retain their original licenses and attribution; see the paper's appendix.

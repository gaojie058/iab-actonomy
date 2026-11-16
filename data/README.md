# Research data

The codebook uses **10 actions → 46 subactions → 120 leaf instances**. The readable presentation adds three clusters; they are not an extra coding level.

| Directory | Contents |
| --- | --- |
| [taxonomy/](taxonomy/) | Canonical codebook CSV, taxonomy CSV/JSON, readable taxonomy, and development snapshots |
| [corpus/](corpus/) | 35-paper index and 780 extracted behavior-description sentences |
| [large_corpus/](large_corpus/) | Follow-up paper index and 3,455 behavior-description sentences |

## Corpus splits

- **Construction:** 28 papers / 664 sentences. The existing study documentation identifies 20 incorporated papers / 565 sentences and 8 reviewed off-topic papers / 99 sentences. The released codebook quotes 120 sentences as evidence.
- **Held out:** 7 papers / 116 sentences, with 50 sentences sampled for the reported human–human and human–LLM reliability checks.

Join the corpus paper index and sentence tables by `paper_id`. Original suggested labels and review decisions are historical records; preserve them when the taxonomy evolves.

## Larger corpus inventory

The prior README described 210 papers. The checked-in `large-corpus-paper-list.csv` currently contains **211 data rows with distinct paper IDs/URLs**, while the sentence table contains **3,455 rows**. The index's `title` field currently contains the placeholder `[paper`; use IDs and URLs for identification. These are documented inventory discrepancies, not corrections to the research sample. The refactor does not add, remove, or relabel evidence.

## Local-only materials

`data/reliability/`, `data/saturation/`, and `data/corpus/construction_set_pdfs/` remain ignored. They may exist in a maintainer's working copy but are not required by the quickstart, tests, or CI. Release staging remains in the ignored root `hf_release/` directory. Third-party paper PDFs are not redistributed here.

Codebook content and labeled datasets are covered by [CC BY 4.0](../LICENSE-codebook). For citation, see [the root README](../README.md#citation).

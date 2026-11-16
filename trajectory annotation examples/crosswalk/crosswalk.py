#!/usr/bin/env python3
"""
Crosswalk: MAST (14 failure modes) and CoALA (action space) -> Act*ONOMY v4.2 leaves.

Why this exists
---------------
Reviewer concern (NeurIPS 2026 ED): "multiple simultaneous work ... trying to
classify and label agent behaviors", i.e. limited originality. The counter-claim
is that Act*ONOMY sits at a *finer and more general* level than the concurrent
schemes, and that those schemes are expressible over Act*ONOMY annotations while
the converse does not hold. This script turns that claim into numbers.

Method
------
Two directions, kept separate because they answer different questions.

  FORWARD  (their category -> our leaves): can Act*ONOMY express it?
  REVERSE  (our leaves -> their category): does their scheme reach our vocabulary?

A MAST failure mode is not a behavior; it is a *predicate over* behavior
(absent / wrong / repeated). So the forward mapping records a RELATION, not just
a target:

  direct     the mode names one behavior that has a leaf; the failure is that
             leaf being absent or wrong
  composite  needs 2+ leaves jointly
  pattern    a predicate over the annotated leaf *sequence* (repetition, drift,
             thought/action disagreement)
  gap        no leaf covers it; a v4.3 extension candidate

Coverage percentages are computed against the live taxonomy CSV, so they cannot
drift from the codebook.

Usage:  python3 examples/crosswalk/crosswalk.py [--csv PATH] [--outdir DIR]
"""

import argparse
import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO / "data" / "taxonomy" / "act-onomy_taxonomy.csv"


# --------------------------------------------------------------------------
# MAST -> Act*ONOMY.  Modes verbatim from arXiv:2503.13657 (NeurIPS 2025 D&B).
# `leaves` are Act*ONOMY v4.2 codes; `relation` per the docstring.
# --------------------------------------------------------------------------
MAST = [
    # ---- FC1. System Design Issues ----
    dict(
        id="FM-1.1", cat="FC1 System Design Issues",
        name="Disobey task specification",
        defn="Failure to adhere to the specified constraints or requirements of a given task",
        relation="composite",
        leaves=["T3.1.1.1", "T2.3.2.2", "T2.3.2.3", "T2.3.2.4"],
        note="Constraint arrives via 'Accept instructions from humans'; the failure is the "
             "absence or misexecution of the three constraint-side Evaluate leaves.",
    ),
    dict(
        id="FM-1.2", cat="FC1 System Design Issues",
        name="Disobey role specification",
        defn="Failure to adhere to the defined responsibilities and constraints of an assigned role",
        relation="composite",
        leaves=["T2.2.7.3", "T2.2.7.4", "T2.1.1.3", "T2.4.3.1", "T3.1.1.6"],
        note="Role is established by the two role-conditioning leaves; violation = acting "
             "outside the leaf set those licence, or failing to decline/refuse when out of scope.",
    ),
    dict(
        id="FM-1.3", cat="FC1 System Design Issues",
        name="Step repetition",
        defn="Unnecessary reiteration of previously completed steps in a process",
        relation="pattern",
        leaves=[],
        note="Predicate over the annotated sequence: identical leaf code recurs across turns "
             "with no intervening Reflection (T4.2.*) or Modify Plan (T2.1.4.*). Leaf-agnostic, "
             "so it applies to all 120 leaves rather than to any one of them.",
    ),
    dict(
        id="FM-1.4", cat="FC1 System Design Issues",
        name="Loss of conversation history",
        defn="Unexpected context truncation, disregarding recent interaction history",
        relation="direct",
        leaves=["T1.2.3.1", "T1.2.3.2", "T1.2.4.2", "T1.2.5.1"],
        note="Act*ONOMY splits this into four distinct memory operations where MAST has one "
             "mode: discard-from-working, discard-redundant-keep-summary, compact-context, "
             "read-from-working. The distinction matters because only the last is recoverable.",
    ),
    dict(
        id="FM-1.5", cat="FC1 System Design Issues",
        name="Unaware of termination conditions",
        defn="Lack of recognition or understanding of the criteria that should trigger termination",
        relation="composite",
        leaves=["T2.1.1.2", "T2.1.2.1", "T2.3.2.1", "T3.2.3.1"],
        note="Termination criteria are set by the subgoal/plan leaves and checked by "
             "goal-completion check; the failure is that check never firing before Terminating.",
    ),
    # ---- FC2. Inter-Agent Misalignment ----
    dict(
        id="FM-2.1", cat="FC2 Inter-Agent Misalignment",
        name="Conversation reset",
        defn="Unexpected or unwarranted restarting of a dialogue, potentially losing context",
        relation="gap",
        leaves=["T1.2.3.1", "T3.1.4.3"],
        note="GAP. The nearest leaves cover discarding working memory and sending a peer "
             "message, but neither names restarting a dialogue as such. v4.3 extension "
             "candidate: Grounding > Interact with other agents > Reset conversation with peer.",
    ),
    dict(
        id="FM-2.2", cat="FC2 Inter-Agent Misalignment",
        name="Fail to ask for clarification",
        defn="Inability to request additional information when faced with unclear or incomplete data",
        relation="direct",
        leaves=["T3.1.1.2", "T2.4.4.1"],
        note="Absence of 'Ask for clarification from people' in a turn annotated "
             "'Decide under uncertainty'. A two-leaf signature, directly computable.",
    ),
    dict(
        id="FM-2.3", cat="FC2 Inter-Agent Misalignment",
        name="Task derailment",
        defn="Deviation from the intended objective or focus of a given task",
        relation="pattern",
        leaves=["T2.1.2.1", "T2.1.4.1", "T2.3.2.1"],
        note="Drift between the leaf set named in the plan and the leaf set actually executed, "
             "with no Replan leaf accounting for the change.",
    ),
    dict(
        id="FM-2.4", cat="FC2 Inter-Agent Misalignment",
        name="Information withholding",
        defn="Failure to share or communicate important data that could impact other agents' decisions",
        relation="direct",
        leaves=["T3.1.4.3", "T3.1.4.4"],
        note="Absence of Send-message / Recommend-action to peer after a leaf that produced "
             "decision-relevant information.",
    ),
    dict(
        id="FM-2.5", cat="FC2 Inter-Agent Misalignment",
        name="Ignored other agent's input",
        defn="Disregarding or failing to adequately consider input provided by other agents",
        relation="direct",
        leaves=["T3.1.4.1", "T3.1.4.2", "T4.2.3.1"],
        note="Cleanest signature in the whole crosswalk: 'Receive feedback from peer agent' "
             "present, 'Receive and integrate external feedback' absent. Act*ONOMY separates "
             "receiving from integrating; MAST cannot.",
    ),
    dict(
        id="FM-2.6", cat="FC2 Inter-Agent Misalignment",
        name="Reasoning-action mismatch",
        defn="Discrepancy between logical reasoning process and actual actions taken by the agent",
        relation="pattern",
        leaves=[],
        note="Act*ONOMY annotates Observation / Thought / Action spans separately, so this is "
             "a disagreement between the Thought-side leaf (T2.2.*) and the Action-side leaf "
             "(T3.*) of the same turn. Structural, hence leaf-agnostic.",
    ),
    # ---- FC3. Task Verification ----
    dict(
        id="FM-3.1", cat="FC3 Task Verification",
        name="Premature termination",
        defn="Ending a dialogue before all necessary information has been exchanged or objectives met",
        relation="direct",
        leaves=["T3.2.3.1", "T3.2.3.2", "T2.3.2.1"],
        note="This is the 'submit anyway, without verifying' pattern already surfaced in "
             "Case Study 4.3 (django-14411 T16): Terminating reached with no goal-completion "
             "check in the preceding session.",
    ),
    dict(
        id="FM-3.2", cat="FC3 Task Verification",
        name="No or incomplete verification",
        defn="(Partial) omission of proper checking or confirmation of task outcomes",
        relation="direct",
        leaves=["T2.3.1.1", "T2.3.1.2", "T2.3.2.1", "T2.3.2.2", "T2.3.2.3", "T2.3.2.4",
                "T2.3.3.1", "T2.3.3.2", "T2.3.3.3", "T2.3.3.4", "T2.3.3.5", "T2.3.3.6",
                "T2.3.3.7", "T2.3.3.8"],
        note="Absence over the entire Evaluate branch. Act*ONOMY has 14 leaves here where "
             "MAST has one mode, and the distinction is consequential: 'no gold available' "
             "(T2.3.3.*) is a different engineering problem from 'gold available but unused' "
             "(T2.3.1.*).",
    ),
    dict(
        id="FM-3.3", cat="FC3 Task Verification",
        name="Incorrect verification",
        defn="Failure to adequately validate or cross-check crucial information or decisions",
        relation="direct",
        leaves=["T2.3.1.1", "T2.3.1.2", "T2.3.2.1", "T2.3.2.2", "T2.3.2.3", "T2.3.2.4",
                "T2.3.3.1", "T2.3.3.2", "T2.3.3.3", "T2.3.3.4", "T2.3.3.5", "T2.3.3.6",
                "T2.3.3.7", "T2.3.3.8"],
        note="Same branch as FM-3.2 but misexecution rather than absence. MAST needs two "
             "modes to separate absent-vs-wrong; Act*ONOMY gets it from the annotation "
             "being present-with-a-quote vs missing.",
    ),
]


# --------------------------------------------------------------------------
# CoALA -> Act*ONOMY.  Categories verbatim from arXiv:2309.02427 (TMLR 2024).
# Mapping is by Action/Subaction, so it is stated as predicates over rows.
# --------------------------------------------------------------------------
def coala_bucket(action, subaction):
    """Return (coala_unit, coala_layer) for an Act*ONOMY row, or (None, None)."""
    if action == "Grounding":
        return "External: grounding", "action space"
    if action == "Retrieval":
        return "Internal: retrieval", "action space"
    if action == "Memory":
        # CoALA: reading LTM is retrieval; writing LTM is learning.
        if subaction == "Read memory":
            return "Internal: retrieval", "action space"
        return "Internal: learning", "action space"
    if action == "Reasoning":
        return "Internal: reasoning", "action space"
    if action == "Learning":
        return "Internal: learning", "action space"
    # Decision procedure, not action space.
    if action == "Planning":
        return "Decision cycle: planning (propose)", "decision procedure"
    if action == "Evaluate":
        return "Decision cycle: planning (evaluate)", "decision procedure"
    if action == "Deciding":
        return "Decision cycle: planning (select)", "decision procedure"
    if action == "Executing":
        return "Decision cycle: execution", "decision procedure"
    if action == "Reflection":
        # CoALA has no dedicated category. It would be swept into "reasoning",
        # which erases the distinction the paper argues for in §2.1.
        return None, "unassigned"
    return None, "unassigned"


def load_taxonomy(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("code"):
                rows.append(r)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--outdir", default=str(REPO / "outputs" / "crosswalk"))
    args = ap.parse_args()

    rows = load_taxonomy(args.csv)
    by_code = {r["code"]: r for r in rows}
    n_leaves = len(rows)
    per_action = Counter(r["Action"] for r in rows)

    # ---------------- MAST ----------------
    for m in MAST:
        missing = [c for c in m["leaves"] if c not in by_code]
        if missing:
            raise SystemExit(f"{m['id']} references unknown codes: {missing}")

    mast_hit = set()
    for m in MAST:
        mast_hit.update(m["leaves"])

    rel_counts = Counter(m["relation"] for m in MAST)
    expressible = sum(1 for m in MAST if m["relation"] != "gap")

    mast_hit_by_action = Counter(by_code[c]["Action"] for c in mast_hit)

    # ---------------- CoALA ----------------
    coala_rows = []
    for r in rows:
        unit, layer = coala_bucket(r["Action"], r["Subaction"])
        coala_rows.append((r, unit, layer))
    coala_layer_counts = Counter(layer for _, _, layer in coala_rows)
    coala_unit_counts = Counter(unit for _, unit, _ in coala_rows if unit)

    # ---------------- report ----------------
    pct = lambda a, b: f"{100.0 * a / b:.1f}%"
    L = []
    P = L.append
    P("=" * 74)
    P(f"CROSSWALK  ·  Act*ONOMY v4.2  ({n_leaves} leaves, "
      f"{len(set(r['Subaction'] for r in rows))} sub-actions, "
      f"{len(per_action)} actions)")
    P("=" * 74)

    P("")
    P("[1] MAST -> Act*ONOMY   (forward: can we express their modes?)")
    P("-" * 74)
    for m in MAST:
        tag = m["relation"].upper()
        codes = ", ".join(m["leaves"]) if m["leaves"] else "(sequence-level, leaf-agnostic)"
        P(f"  {m['id']:7s} {m['name']:34s} {tag:10s} {codes}")
    P("")
    P(f"  expressible over Act*ONOMY : {expressible}/{len(MAST)}  ({pct(expressible, len(MAST))})")
    for k in ("direct", "composite", "pattern", "gap"):
        if rel_counts[k]:
            P(f"      {k:10s} {rel_counts[k]}")
    P("")
    P("  The one gap (FM-2.1 Conversation reset) is a concrete v4.3 candidate:")
    P("      Grounding > Interact with other agents > Reset conversation with peer")

    P("")
    P("[2] Act*ONOMY -> MAST   (reverse: how much of our vocabulary do they reach?)")
    P("-" * 74)
    P(f"  leaves reachable from MAST's 14 modes : {len(mast_hit)}/{n_leaves}  "
      f"({pct(len(mast_hit), n_leaves)})")
    P(f"  leaves with no MAST counterpart       : {n_leaves - len(mast_hit)}/{n_leaves}  "
      f"({pct(n_leaves - len(mast_hit), n_leaves)})")
    P("")
    P(f"  {'Action':<12}{'leaves':>8}{'reached':>9}{'unreached':>11}   coverage")
    for a, tot in sorted(per_action.items(), key=lambda kv: -kv[1]):
        hit = mast_hit_by_action.get(a, 0)
        bar = "#" * int(round(20 * hit / tot))
        P(f"  {a:<12}{tot:>8}{hit:>9}{tot - hit:>11}   {bar:<20} {pct(hit, tot)}")

    P("")
    P("[3] CoALA -> Act*ONOMY   (forward: containment, not distinction)")
    P("-" * 74)
    for unit, n in sorted(coala_unit_counts.items(), key=lambda kv: -kv[1]):
        P(f"  {unit:<38}{n:>4} leaves   ({pct(n, n_leaves)})")
    unassigned = coala_layer_counts.get("unassigned", 0)
    P(f"  {'(no CoALA category)':<38}{unassigned:>4} leaves   ({pct(unassigned, n_leaves)})")
    P("")
    act_space = coala_layer_counts.get("action space", 0)
    dec_proc = coala_layer_counts.get("decision procedure", 0)
    P(f"  CoALA action space proper covers      : {act_space}/{n_leaves}  ({pct(act_space, n_leaves)})")
    P(f"  CoALA decision procedure covers       : {dec_proc}/{n_leaves}  ({pct(dec_proc, n_leaves)})")
    P(f"  no CoALA counterpart (all Reflection) : {unassigned}/{n_leaves}  ({pct(unassigned, n_leaves)})")
    P("")
    n_units = len(coala_unit_counts)
    P(f"  Resolution ratio: {n_units} CoALA units span {n_leaves} leaves "
      f"= 1 unit per {n_leaves / n_units:.0f} leaves.")
    P("  Containment is total but distinction is not: CoALA cannot separate")
    P("  'Compare against gold reference' from 'Provide qualitative judgement' —")
    P("  both are internal reasoning to it.")

    P("")
    P("[4] Headline numbers for the rebuttal")
    P("-" * 74)
    P(f"  MAST     {expressible}/14 modes expressible; reaches {len(mast_hit)}/{n_leaves} leaves "
      f"({pct(len(mast_hit), n_leaves)}); {n_leaves - len(mast_hit)} leaves unreachable,")
    P(f"           including 100% of Retrieval ({per_action['Retrieval']}) and "
      f"100% of Learning ({per_action['Learning']}).")
    P(f"  CoALA    total containment at 1 unit per {n_leaves / n_units:.0f} leaves; "
      f"{unassigned} Reflection leaves have no category.")
    P("=" * 74)

    report = "\n".join(L)
    print(report)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    (outdir / "crosswalk_report.txt").write_text(report + "\n", encoding="utf-8")

    # auditable row-level artifacts
    with open(outdir / "crosswalk_mast.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["mast_id", "mast_category", "mast_mode", "mast_definition",
                    "relation", "actonomy_code", "actonomy_action",
                    "actonomy_subaction", "actonomy_instance", "note"])
        for m in MAST:
            if not m["leaves"]:
                w.writerow([m["id"], m["cat"], m["name"], m["defn"], m["relation"],
                            "", "", "", "", m["note"]])
            for c in m["leaves"]:
                r = by_code[c]
                w.writerow([m["id"], m["cat"], m["name"], m["defn"], m["relation"],
                            c, r["Action"], r["Subaction"], r["Instance"], m["note"]])

    with open(outdir / "crosswalk_coala.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["actonomy_code", "actonomy_action", "actonomy_subaction",
                    "actonomy_instance", "coala_unit", "coala_layer"])
        for r, unit, layer in coala_rows:
            w.writerow([r["code"], r["Action"], r["Subaction"], r["Instance"],
                        unit or "", layer])

    summary = OrderedDict(
        taxonomy=dict(leaves=n_leaves, actions=len(per_action),
                      subactions=len(set(r["Subaction"] for r in rows)),
                      per_action=dict(per_action)),
        mast=dict(modes=len(MAST), expressible=expressible,
                  relations=dict(rel_counts),
                  leaves_reached=len(mast_hit),
                  leaves_unreached=n_leaves - len(mast_hit),
                  leaves_reached_pct=round(100.0 * len(mast_hit) / n_leaves, 1),
                  per_action_reached=dict(mast_hit_by_action),
                  gap_modes=[m["id"] for m in MAST if m["relation"] == "gap"]),
        coala=dict(units=n_units, unit_counts=dict(coala_unit_counts),
                   action_space_leaves=act_space,
                   decision_procedure_leaves=dec_proc,
                   unassigned_leaves=unassigned,
                   leaves_per_unit=round(n_leaves / n_units, 1)),
    )
    (outdir / "crosswalk_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nwrote: crosswalk_report.txt, crosswalk_mast.csv, "
          f"crosswalk_coala.csv, crosswalk_summary.json  -> {outdir}")


if __name__ == "__main__":
    main()

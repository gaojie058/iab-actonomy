#!/usr/bin/env python3
"""
parse_chat_trajectory.py
========================

Stage-1 parser for human-in-the-loop trajectories: converts a Claude Code
native session log (.jsonl, one event per line) into the annotated-JSON
skeleton consumed by trace-qualitative-analyst's render_artifact.py.

Human prompts become first-class interaction events; agent work becomes
(obs, thought, action) turns. Everything cognitive is left as TODO for the
annotation stages.

USAGE
-----

    python parse_chat_trajectory.py <session.jsonl> \
        --instance-id "<repo> · session <id> (<persona>)" \
        --model "Claude Code (human-in-the-loop, persona: <persona>)" \
        --outcome resolved \
        --output <stem>.skeleton.json

TURN CONSTRUCTION
-----------------

- A real human text message closes the current agent turn and is emitted as
  {kind: "interaction", id: "H<k>", actor: "human", label: "TODO",
   headline: "TODO", text: <verbatim>}. Local-command caveats and slash-command
  wrappers are skipped.
- Each assistant `text`/`thinking` block starts a new agent turn (its content
  is the verbatim `thought`); following `tool_use` blocks extend that turn's
  `action` surface. A tool_use with no preceding text starts a thought-less
  turn (normal in chat agents — annotate its action surface).
- `tool_result` contents accumulate into the NEXT turn's `obs` (environment
  feedback only; truncated to --obs-limit chars). Human prompts are never
  truncated.
- Agent turns are numbered 1..N excluding interactions, so segments and
  turn references stay stable regardless of how many human turns interleave.
"""
import argparse
import json
import re


def make_tool_surface(strip):
    def tool_surface(tu):
        name, inp = tu.get("name"), tu.get("input", {}) or {}
        if name == "Bash":
            return "$ " + str(inp.get("command", "")).strip()
        if name in ("Grep", "Glob"):
            pat = inp.get("pattern", "")
            path = strip(inp.get("path", "") or "")
            return "%s '%s'%s" % (name.lower(), pat, " (in %s)" % path if path else "")
        if name == "Read":
            fp = strip(inp.get("file_path", ""))
            rng = ""
            if inp.get("offset"):
                rng = ":%s-%s" % (inp["offset"], inp["offset"] + inp.get("limit", 0))
            return "read " + fp + rng
        if name == "Edit":
            fp = strip(inp.get("file_path", ""))
            return "edit %s\n- %s\n+ %s" % (
                fp, str(inp.get("old_string", "")).strip(), str(inp.get("new_string", "")).strip())
        if name == "Write":
            fp = strip(inp.get("file_path", ""))
            content = str(inp.get("content", ""))
            head = content[:400] + (" …" if len(content) > 400 else "")
            return "write %s\n%s" % (fp, head)
        if name == "TodoWrite":
            todos = inp.get("todos", []) or []
            items = "; ".join(str(t.get("content", ""))[:60] for t in todos if isinstance(t, dict))
            return "todo: [%s]" % items
        return "%s %s" % (name, json.dumps(inp, ensure_ascii=False)[:160])
    return tool_surface


def result_summary(content):
    if isinstance(content, list):
        content = " ".join(x.get("text", "") for x in content if isinstance(x, dict))
    if not isinstance(content, str):
        content = str(content)
    return content.strip()


def is_noise_user_string(s):
    return s.startswith("<") or "command-name" in s


def parse(lines, obs_limit):
    turns = []
    cur = None
    pending_obs = []
    agent_n = 0
    human_k = 0

    cwd = next((l.get("cwd") for l in lines if l.get("cwd")), None)
    strip = (lambda s: s.replace(cwd.rstrip("/") + "/", "")) if cwd else (lambda s: s)
    tool_surface = make_tool_surface(strip)

    def close():
        nonlocal cur
        if cur is not None:
            cur["action"] = "\n".join(cur["action"]).strip()
            cur["thought"] = cur["thought"].strip()
            turns.append(cur)
            cur = None

    def new_turn(thought):
        nonlocal agent_n
        agent_n += 1
        return {
            "n": agent_n,
            "phase": "TODO", "phase_label": "TODO", "headline": "TODO",
            "obs": "\n".join(pending_obs).strip(),
            "thought": thought,
            "action": [],
            "quotes": [],
        }

    for l in lines:
        t = l.get("type")
        if t == "user":
            c = l.get("message", {}).get("content")
            if isinstance(c, str):
                if is_noise_user_string(c):
                    continue
                close()
                pending_obs.clear()
                human_k += 1
                turns.append({
                    "kind": "interaction",
                    "id": "H%d" % human_k,
                    "actor": "human",
                    "label": "TODO",
                    "headline": "TODO",
                    "text": c.strip(),
                })
            elif isinstance(c, list):
                for x in c:
                    if x.get("type") == "tool_result":
                        s = result_summary(x.get("content"))
                        if s:
                            pending_obs.append(s)
        elif t == "assistant":
            for x in l.get("message", {}).get("content", []):
                k = x.get("type")
                if k in ("text", "thinking"):
                    close()
                    txt = (x.get("text") if k == "text" else x.get("thinking", "")) or ""
                    cur = new_turn(txt.strip())
                    pending_obs.clear()
                elif k == "tool_use":
                    if cur is None:
                        cur = new_turn("")
                        pending_obs.clear()
                    cur["action"].append(tool_surface(x))
    close()

    # truncate long environment obs; human text lives in interaction events and is never cut
    for t in turns:
        if t.get("kind") != "interaction" and len(t["obs"]) > obs_limit:
            t["obs"] = t["obs"][:obs_limit] + " …[truncated]"

    return turns, agent_n, human_k


def main():
    ap = argparse.ArgumentParser(description="Parse a Claude Code session .jsonl into a human-in-the-loop annotation skeleton.")
    ap.add_argument("transcript")
    ap.add_argument("--instance-id", default="TODO")
    ap.add_argument("--model", default="Claude Code (human-in-the-loop)")
    ap.add_argument("--outcome", default="resolved", choices=["resolved", "unresolved"])
    ap.add_argument("--output", default=None)
    ap.add_argument("--obs-limit", type=int, default=700)
    args = ap.parse_args()

    lines = [json.loads(l) for l in open(args.transcript) if l.strip()]
    turns, agent_n, human_k = parse(lines, args.obs_limit)

    doc = {
        "instance_id": args.instance_id,
        "model": args.model,
        "outcome": args.outcome,
        "issue_text": "TODO",
        "summary": "TODO",
        "quote_target": "both",
        "turns": turns,
    }
    out = args.output or re.sub(r"\.jsonl?$", "", args.transcript) + ".skeleton.json"
    json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)

    print("✓ Wrote skeleton: %s" % out)
    print("  · %d agent turns · %d human interactions" % (agent_n, human_k))
    for t in turns:
        if t.get("kind") == "interaction":
            print("  %s  HUMAN: %s" % (t["id"], t["text"][:90].replace("\n", " ")))
        else:
            head = (t["thought"] or t["action"]).replace("\n", " ")[:90]
            print("  T%02d  %s" % (t["n"], head))


if __name__ == "__main__":
    main()

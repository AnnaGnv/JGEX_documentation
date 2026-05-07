import json
from pathlib import Path

OLD_RESULTS = [
    "pipeline_results_eval.json"
]

OUT_PATH = "rerun_trunc_only.json"

def load_all(paths):
    all_rows = []
    for p in paths:
        all_rows.extend(json.loads(Path(p).read_text(encoding="utf-8")))
    return all_rows

rows = load_all(OLD_RESULTS)

def is_truncated(row):
    hist = row.get("history") or []
    if not hist:
        return False
    err = hist[0].get("error") or ""
    return ("finish_reason=length" in err) and (hist[0].get("jgex_candidate") is None)

targets = [r for r in rows if is_truncated(r)]
print(f"Found {len(targets)} truncated targets")

# Rerun function: you already have formalize(), just modify it to accept kwargs.
def formalize_once(nl_problem, examples, *, max_tokens=3000):
    messages = build_prompt(nl_problem, examples)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0,
        extra_body={
            "reasoning": {"effort": "low"}
        }
    )
    content = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason
    usage = getattr(response, "usage", None)

    if content is None:
        return None, False, {
            "finish_reason": finish_reason,
            "usage": usage.model_dump() if usage else None,
            "error": f"API returned None, finish_reason={finish_reason}",
        }

    jgex = content.strip().replace("```", "").strip()
    ok, err = run_newclid(jgex)

    meta = {
        "finish_reason": finish_reason,
        "usage": usage.model_dump() if usage else None,
        "newclid_error": err,
    }
    return jgex, ok, meta

rerun_rows = []
recovered_any = 0
recovered_exec = 0

for r in targets:
    jgex, ok, meta = formalize_once(r["nl_problem"], EXAMPLES, max_tokens=8000)
    recovered_any += int(jgex is not None)
    recovered_exec += int(ok)

    rerun_rows.append({
        "id": r["id"],
        "nl_problem": r["nl_problem"],
        "old_history": r.get("history"),
        "new_jgex_result": jgex,
        "new_success": ok,
        "new_meta": meta,
    })

Path(OUT_PATH).write_text(json.dumps(rerun_rows, indent=2), encoding="utf-8")
print(f"Recovered JGEX (non-empty): {recovered_any}/{len(targets)}")
print(f"Recovered executable: {recovered_exec}/{len(targets)}")
print(f"Wrote {OUT_PATH}")
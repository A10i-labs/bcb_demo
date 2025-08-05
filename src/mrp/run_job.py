# run_job.py
import sys
import json
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any

# -----------------------------
# Registry: map agents, reducers, producers
# -----------------------------

def agent_process_bio(chunk: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map-stage agent:
      - Uppercase every token
      - Filter tokens with length >= min_len
    Returns summary for this shard.
    """
    min_len = int(params.get("min_len", 0))
    upper = [s.upper() for s in chunk]
    processed = [s for s in upper if len(s) >= min_len]
    return {
        "input_size": len(chunk),
        "kept_size": len(processed),
        "kept": processed,
    }

AGENT_REGISTRY = {
    "process_bio": agent_process_bio,
}

def reduce_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Reduce-stage aggregator:
      - Sums sizes, flattens 'kept'
    """
    total_input = sum(r["input_size"] for r in results)
    total_kept = sum(r["kept_size"] for r in results)
    kept_flat = []
    for r in results:
        kept_flat.extend(r["kept"])
    return {
        "total_input": total_input,
        "total_kept": total_kept,
        "kept": kept_flat,
        "shards": results,
    }

REDUCE_REGISTRY = {
    "stats": reduce_stats,
}

def produce_print(payload: Dict[str, Any], spec: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))

def produce_save_json(payload: Dict[str, Any], spec: Dict[str, Any]) -> None:
    """
    Optionally save to a file:
      produce:
        op: save_json
        path: outputs/result.json
    """
    path = spec.get("produce", {}).get("path")
    if not path:
        raise ValueError("produce.save_json requires 'path'")
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[OK] Wrote JSON to {out}")

def produce_save_markdown(payload: Dict[str, Any], spec: Dict[str, Any]) -> None:
    """
    Save results to a markdown file:
      produce:
        op: save_markdown
        path: outputs/result.md
    """
    path = spec.get("produce", {}).get("path")
    if not path:
        raise ValueError("produce.save_markdown requires 'path'")
    
    # Format payload as markdown
    job_name = spec.get("job", "(unnamed)")
    description = spec.get("description", "")
    
    md_content = f"""# {job_name}

{description}

## Results Summary

- **Total Input Items**: {payload.get('total_input', 0)}
- **Total Kept Items**: {payload.get('total_kept', 0)}
- **Filter Efficiency**: {payload.get('total_kept', 0) / max(payload.get('total_input', 1), 1) * 100:.1f}%

## Filtered Items (Length ≥ 5)

"""
    
    kept_items = payload.get('kept', [])
    for i, item in enumerate(kept_items, 1):
        md_content += f"{i}. `{item}`\n"
    
    md_content += f"""
## Shard Details

| Shard | Input Size | Kept Size | Items |
|-------|------------|-----------|-------|
"""
    
    shards = payload.get('shards', [])
    for i, shard in enumerate(shards):
        items_str = ", ".join([f"`{item}`" for item in shard.get('kept', [])])
        if not items_str:
            items_str = "*none*"
        md_content += f"| {i} | {shard.get('input_size', 0)} | {shard.get('kept_size', 0)} | {items_str} |\n"
    
    md_content += f"""
## Raw JSON Data

```json
{json.dumps(payload, indent=2)}
```
"""
    
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md_content, encoding="utf-8")
    print(f"[OK] Wrote Markdown to {out}")

PRODUCE_REGISTRY = {
    "print": produce_print,
    "save_json": produce_save_json,
    "save_markdown": produce_save_markdown,
}

# -----------------------------
# Validation helpers
# -----------------------------

REQUIRED_TOP_KEYS = ["map", "reduce", "produce"]

def validate_spec(spec: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_KEYS if k not in spec]
    if missing:
        raise ValueError(f"Spec missing top-level keys: {missing}")

    if "agent" not in spec["map"] or "data" not in spec["map"]:
        raise ValueError("map section must include 'agent' and 'data'")

    if not isinstance(spec["map"]["data"], list) or not spec["map"]["data"]:
        raise ValueError("map.data must be a non-empty list of shards")

    # Ensure list of lists (shards)
    if not all(isinstance(shard, list) for shard in spec["map"]["data"]):
        raise ValueError("map.data must be a list of lists (each shard is a list)")

    reduce_op = spec["reduce"].get("op")
    if reduce_op not in REDUCE_REGISTRY:
        raise ValueError(f"Unknown reduce.op: {reduce_op!r}")

    produce_op = spec["produce"].get("op")
    if produce_op not in PRODUCE_REGISTRY:
        raise ValueError(f"Unknown produce.op: {produce_op!r}")

    agent = spec["map"]["agent"]
    if agent not in AGENT_REGISTRY:
        raise ValueError(f"Unknown map.agent: {agent!r}")

# -----------------------------
# Runner
# -----------------------------

def run(spec_path: Path) -> None:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    validate_spec(spec)

    map_cfg = spec["map"]
    agent_name = map_cfg["agent"]
    params = map_cfg.get("params", {}) or {}
    shards = map_cfg["data"]
    agent_fn = AGENT_REGISTRY[agent_name]

    print(f"▶ Job: {spec.get('job','(unnamed)')}")
    print(f"  - agent: {agent_name}")
    print(f"  - shards: {len(shards)}")
    print(f"  - reduce: {spec['reduce']['op']}")
    print(f"  - produce: {spec['produce']['op']}")

    # Parallel map using threads (simple "agentic" mock)
    results = [None] * len(shards)
    with ThreadPoolExecutor(max_workers=min(32, len(shards))) as ex:
        futures = {ex.submit(agent_fn, shard, params): i for i, shard in enumerate(shards)}
        for fut in as_completed(futures):
            idx = futures[fut]
            results[idx] = fut.result()
            print(f"    ✓ shard {idx} done")

    # Reduce
    reducer = REDUCE_REGISTRY[spec["reduce"]["op"]]
    reduced = reducer(results)

    # Produce
    producer = PRODUCE_REGISTRY[spec["produce"]["op"]]
    producer(reduced, spec)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_job.py path/to/job.yml")
        sys.exit(1)
    run(Path(sys.argv[1]))

if __name__ == "__main__":
    main()
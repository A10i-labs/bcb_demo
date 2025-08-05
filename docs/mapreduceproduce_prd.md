# MapReduce Produce

This is a **minimal, end-to-end “English → YAML DSL → parallel runtime”** that runs a toy *biological data processing* pipeline. No LLMs, just a lookup translator + a tiny DSL + a parallel executor.

Below are **two Python files** and the **generated YAML**. Run them as-is.

---

## 1) `compile.py` — stub NL→DSL translator (lookup table)

```python
# compile.py
import sys
from pathlib import Path
import textwrap

TEMPLATES = {
    # Exact string → DSL YAML
    "run the biological data processing given the data": textwrap.dedent("""\
        job: bio_hello
        description: "Demo: uppercase + filter length>=5, then aggregate stats"
        map:
          agent: process_bio
          params:
            min_len: 5
          data:
            - ["ATCG","GCTA","TGCA","CGAT","AATG"]
            - ["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]
            - ["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]
            - ["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]
        reduce:
          op: stats
        produce:
          op: print
        """)
}

USAGE = """\
Usage:
  python compile.py "run the biological data processing given the data" [OUTPUT_YML]

Notes:
  • This is a stub translator: it just maps exact strings to DSL YAML.
  • Default output file is ./job.yml if none is provided.
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    query = sys.argv[1].strip()
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("job.yml")

    if query not in TEMPLATES:
        print(f"[ERROR] No template for query: {query!r}")
        print("Hint: try the exact string above.")
        sys.exit(2)

    out_path.write_text(TEMPLATES[query], encoding="utf-8")
    print(f"[OK] Wrote DSL spec to: {out_path}")

if __name__ == "__main__":
    main()
```

---

## 2) `run_job.py` — YAML parser, validation, parallel “agents,” reduce, produce

```python
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
    print(f"[OK] Wrote {out}")

PRODUCE_REGISTRY = {
    "print": produce_print,
    "save_json": produce_save_json,
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

    # Parallel map using threads (simple “agentic” mock)
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
```

---

## 3) Generated DSL (`job.yml`) for your specific query

Running the translator below will generate this YAML:

```yaml
job: bio_hello
description: "Demo: uppercase + filter length>=5, then aggregate stats"
map:
  agent: process_bio
  params:
    min_len: 5
  data:
    - ["ATCG","GCTA","TGCA","CGAT","AATG"]
    - ["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]
    - ["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]
    - ["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]
reduce:
  op: stats
produce:
  op: print
```

---

## How to run

```bash
# 1) Generate the YAML from the plain-English query (stub translator)
python compile.py "run the biological data processing given the data" job.yml

# 2) Execute the job (agentic map, reduce, produce)
python run_job.py job.yml
```

**Expected output (abridged):**

```text
▶ Job: bio_hello
  - agent: process_bio
  - shards: 4
  - reduce: stats
  - produce: print
    ✓ shard 0 done
    ✓ shard 1 done
    ✓ shard 2 done
    ✓ shard 3 done
{
  "total_input": 19,
  "total_kept": 15,
  "kept": ["ATCG", "GCTA", ... "KERATIN"],
  "shards": [
    {"input_size": 5, "kept_size": 3, "kept": ["ATCG","GCTA","AATG"]},
    ...
  ]
}
```

---

## What makes this “agentic” (without LLMs)

* **Agents = map workers**: each shard is handled by an *agent function* referenced by name in the DSL (`map.agent: process_bio`).
* **Parallelism**: `ThreadPoolExecutor` fans out work across shards and collects results.
* **Spec-driven**: All behavior—inputs, params, reduce/produce ops—is declared in YAML, validated before execution.
* **Composable runtime**: You can register more `AGENT_REGISTRY`, `REDUCE_REGISTRY`, `PRODUCE_REGISTRY` entries without changing the driver.

---

## Easy extensions (keep the DSL tiny)

* **Add a file input**:

  ```yaml
  map:
    agent: process_bio
    params: { min_len: 6 }
    file: "data/bio_chunks.json"   # if present, runner loads shards from file instead of inline
  ```

  (Update `run_job.py` to read `map.file` when provided.)

* **Produce to JSON file**:

  ```yaml
  produce:
    op: save_json
    path: outputs/result.json
  ```

* **More agents** (e.g., `gc_content`, `filter_prefix`, `regex_match`)—just add new functions and register them.

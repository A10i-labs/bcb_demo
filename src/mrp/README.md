# MapReduce Produce (MRP)

A **minimal, end-to-end "English → YAML DSL → parallel runtime"** for biological data processing pipelines. This system demonstrates agentic computing patterns without LLMs, using a simple lookup translator + DSL + parallel executor.

## 🏗️ Architecture

```
English Query → compile.py → YAML DSL → run_job.py → Parallel Execution
```

- **Translation Layer**: `compile.py` - Maps natural language to YAML specifications
- **Runtime Engine**: `run_job.py` - Executes parallel map-reduce-produce workflows  
- **DSL Format**: YAML specifications with map agents, reducers, and producers

## 📁 Files

| File | Purpose |
|------|---------|
| `compile.py` | NL→DSL translator with query templates |
| `run_job.py` | Parallel runtime with agent registry |
| `job.yml` | Example YAML specification |
| `outputs/` | Generated results (JSON/Markdown) |

## 🚀 Quick Start

### 1. Generate YAML from Natural Language

```bash
# Console output
python compile.py "run the biological data processing given the data"

# Save to JSON file
python compile.py "save biological data processing to json"

# Save to Markdown report
python compile.py "save biological data processing to markdown"
```

### 2. Execute the Job

```bash
python run_job.py job.yml
```

### Expected Output

```
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
  "total_input": 18,
  "total_kept": 11,
  "kept": ["PROTEIN_A", "ENZYME_B", "RECEPTOR_C", ...],
  "shards": [...]
}
```

## 🎯 Available Queries

The system currently supports these exact queries:

1. **`"run the biological data processing given the data"`**
   - Processes biological sequences with length filtering
   - Outputs results to console

2. **`"save biological data processing to json"`**
   - Same processing as above
   - Saves results to `outputs/bio_results.json`

3. **`"save biological data processing to markdown"`**
   - Same processing as above  
   - Saves formatted report to `outputs/bio_results.md`

## 📊 Sample Data Processing

The demo processes 4 shards of biological data:

- **Shard 0**: `["ATCG","GCTA","TGCA","CGAT","AATG"]` → Filters items with length ≥ 5
- **Shard 1**: `["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]` → All kept
- **Shard 2**: `["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]` → Keeps longer names
- **Shard 3**: `["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]` → All kept

**Results**: 18 input items → 11 kept items (61.1% efficiency)

## 🔧 How It Works

### Map Phase

- **Agent**: `process_bio` runs in parallel across shards
- **Processing**: Uppercase transformation + length filtering
- **Parallelism**: ThreadPoolExecutor with up to 32 workers

### Reduce Phase  

- **Aggregation**: Combines shard results into summary statistics
- **Output**: Total counts, filtered items, per-shard details

### Produce Phase

- **print**: Console JSON output
- **save_json**: Clean JSON file output
- **save_markdown**: Formatted report with tables and summaries

## 🎨 Output Formats

### JSON Output (`outputs/bio_results.json`)

```json
{
  "total_input": 18,
  "total_kept": 11,
  "kept": ["PROTEIN_A", "ENZYME_B", ...],
  "shards": [...]
}
```

### Markdown Report (`outputs/bio_results.md`)

- Executive summary with efficiency metrics
- Numbered list of filtered items  
- Shard breakdown table
- Raw JSON data section

## 🔌 Extension Points

### Add New Agents

```python
def agent_gc_content(chunk: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
    # Custom processing logic
    return {"processed": results}

AGENT_REGISTRY["gc_content"] = agent_gc_content
```

### Add New Reducers

```python
def reduce_advanced_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Custom aggregation logic
    return {"advanced_metrics": metrics}

REDUCE_REGISTRY["advanced_stats"] = reduce_advanced_stats
```

### Add New Producers

```python
def produce_csv(payload: Dict[str, Any], spec: Dict[str, Any]) -> None:
    # Custom output format
    pass

PRODUCE_REGISTRY["csv"] = produce_csv
```

### Add New Queries

```python
TEMPLATES["your new query"] = textwrap.dedent("""\
    job: your_job
    map:
      agent: your_agent
      data: [["your", "data"]]
    reduce:
      op: your_reducer
    produce:
      op: your_producer
    """)
```

## 🧬 What Makes This "Agentic"

- **Agents = Map Workers**: Each shard processed by named agent functions
- **Registry Pattern**: Pluggable agents, reducers, producers without changing core runtime
- **Spec-Driven**: All behavior declared in YAML, validated before execution
- **Parallel Execution**: Automatic work distribution across available cores
- **Composable**: Easy to add new processing patterns and output formats

## 💡 Use Cases

- **Biological sequence analysis** (current demo)
- **Data preprocessing pipelines**
- **Batch file processing**
- **ETL workflows**
- **Scientific computing tasks**

## 🛠️ Requirements

- Python 3.7+
- PyYAML 6.0+
- ThreadPoolExecutor (built-in)

## 📈 Performance

- **Parallel Processing**: Automatic work distribution
- **Minimal Overhead**: Simple thread-based parallelism
- **Scalable**: Configurable worker pool size
- **Memory Efficient**: Processes data in shards

---

*This is a demonstration of agentic computing patterns using standard Python libraries, showing how to build extensible, parallel data processing systems with declarative specifications.*

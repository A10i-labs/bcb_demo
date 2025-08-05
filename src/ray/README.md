# Ray Examples - Distributed Computing Made Simple

This folder contains Ray examples showing how to scale Python code across multiple CPU cores (and eventually multiple machines) with minimal code changes.

## Quick Setup

1. **Activate your virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

2. **Install Ray:**

   ```bash
   pip install ray
   ```

## Examples

### 1. `simple_example.py` - Start Here

The minimal Ray demo (< 100 lines) showing:

- How to parallelize functions with `@ray.remote`
- How to create stateful distributed objects (actors)
- Speed comparison: parallel vs sequential execution

**Run it:**

```bash
cd src/ray
python simple_example.py
```

**Expected output:**

```
🚀 Ray Quick Start
Available CPUs: 8

⏱️  Running 4 tasks in parallel...
Results: [1, 4, 9, 16]
Parallel time: 1.1s (sequential would be ~4s)

🤖 Stateful actor demo...
Count: 1
Count: 2  
Count: 3
Final: 3
```

### 2. `hello_world.py` - Full Demo

Comprehensive example showing:

- Multiple parallel task patterns
- Biological data processing simulation
- Multiple stateful workers collaborating
- Performance comparisons

**Run it:**

```bash
python hello_world.py
```

## Key Ray Concepts (5-Minute Version)

### 1. Remote Tasks = Parallel Functions

```python
@ray.remote
def process_data(data):
    # This function can run on any CPU core
    return expensive_computation(data)

# Run 100 tasks in parallel across all CPU cores
futures = [process_data.remote(chunk) for chunk in data_chunks]
results = ray.get(futures)  # Collect all results
```

### 2. Remote Actors = Distributed Objects

```python
@ray.remote  
class DataProcessor:
    def __init__(self):
        self.processed_count = 0
    
    def process(self, data):
        # This object lives on a worker and keeps state
        self.processed_count += 1
        return result

# Create distributed instances
processors = [DataProcessor.remote() for _ in range(4)]
```

### 3. The Ray Pattern

1. **Decorate** functions/classes with `@ray.remote`
2. **Call** them with `.remote()` (returns futures immediately)
3. **Collect** results with `ray.get(futures)` when needed

## Why Ray for Bioinformatics?

✅ **Perfect for embarrassingly parallel workloads:**

- Processing thousands of protein sequences
- Running parameter sweeps on models
- Analyzing genomic data in chunks

✅ **Zero-copy data sharing:**

- Large datasets stay in shared memory between workers
- No serialization overhead for NumPy arrays, DataFrames

✅ **Scales from laptop to cluster:**

- Start development on your laptop
- Deploy to 100-node clusters with same code

## Next Steps

1. **Try the examples** - see the speed difference on your machine
2. **Adapt to your data** - replace example functions with your analysis code
3. **Scale out** - add more machines when ready with `ray start --address=...`

## End-to-End Flow Summary

```python
import ray

# 1. Start Ray (automatically uses all CPU cores)
ray.init()

# 2. Make any function distributed
@ray.remote
def your_analysis_function(data):
    return analyze(data)

# 3. Run in parallel across all cores
futures = [your_analysis_function.remote(chunk) for chunk in data_chunks]
results = ray.get(futures)

# 4. Done! Results collected from all workers
ray.shutdown()
```

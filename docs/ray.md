### Ray (v 2.9+) — Quick 101

| What                                                                                         | Why it matters                                                                                                                                           |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ray is an open-source distributed computing framework for Python.**                        | Lets you scale “regular” Python code—ETL, model training, LLM agents—across many CPU/GPU nodes *without* rewriting it in Spark, MPI, or Kubernetes YAML. |
| **Core idea: annotate functions/objects with `@ray.remote` and Ray schedules them for you.** | Minimal code change → instant concurrency.                                                                                                               |
| **Lightweight, general-purpose runtime** (not just ML).                                      | Same API powers hyper-param search, reinforcement learning, LLM service endpoints, etc.                                                                  |

---

#### 1. Mental Model

1. **Driver** – the Python script you run (`ray.init()`).
2. **Tasks** – stateless remote functions.

   ```python
   @ray.remote
   def square(x): return x * x
   futures = [square.remote(i) for i in range(8)]
   results = ray.get(futures)
   ```

3. **Actors** – stateful remote objects (keep model weights, DB connections, etc.).

   ```python
   @ray.remote
   class Counter:
       def __init__(self): self.v = 0
       def increment(self): self.v += 1; return self.v
   c = Counter.remote()
   ```

4. **Scheduler** – Ray’s control plane decides where each task/actor runs (laptop cores or a 100-node cluster).
5. **Object Store** – zero-copy data sharing between tasks via shared memory.

---

#### 2. Key Built-ins You’ll Use

| Module                            | One-liner use-case                                                                     |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| **Ray Core**                      | Parallelize Python tasks & actors.                                                     |
| **Ray Datasets**                  | Petabyte-scale batch transforms (map, filter) on Parquet/CSV without Spark.            |
| **Ray AIR**                       | Higher-level ML pipelines; integrates with XGBoost, LightGBM, Torch, 🤗 Transformers.  |
| **Ray Serve**                     | Production web service for models or multi-step LLM agents; autoscaling + A/B deploys. |
| **Ray Workflows (stable in 2.9)** | Durable DAG engine; run/recover multi-step pipelines like Airflow.                     |

---

#### 3. Typical “Hello-World” Cluster Flow

```bash
# Laptop or cloud head node
pip install "ray[default]==2.9.0"
ray start --head --port 6379  # prints a connection string

# (Optional) Add worker nodes:
ray start --address='auto'    # on each worker

# In your driver.py
import ray, time
ray.init(address="auto")

@ray.remote
def slow_double(x):
    time.sleep(1)
    return x * 2

print(ray.get([slow_double.remote(i) for i in range(100)]))
```

* Run once: **all 100 calls finish in \~`100 / cluster_cores` seconds**—proof that Ray is distributing work.

---

#### 4. Why Ray Is Handy for Map → Reduce → Produce POCs

1. **Embarrassingly parallel “map”**: spawn thousands of sandboxed analysis tasks with one list-comprehension.
2. **Built-in data locality & object store**: large NCBI records stay in shared plasma memory—no extra serialization cost between map and reduce.
3. **Fan-in “reduce”**: simply read Parquet shards or collect futures, then run a single aggregation task.
4. **No infra lock-in**: Start on a laptop; later point `ray.init()` at an EKS, GCP GKE or on-prem Slurm cluster.
5. **Plays well with LLM agents**: each agent can be an Actor; Ray Serve turns them into autoscaling endpoints when you move beyond the prototype.

---

#### 5. Next Steps

1. **Install & run the quick demo above.** Verify you can add CPU cores and see speed-up.
2. **Wrap your NCBI analysis function with `@ray.remote`.**
3. **Persist outputs** (`ray.data.write_parquet(...)`) for the reduce step.
4. **Add basic logging** inside each task (write to local file or S3).
5. **Scale out** by starting `ray start --address='auto'` on extra VMs, or use Ray’s Kubernetes operator when ready.

That’s Ray in a nutshell—minimal Python code changes, automatic distribution, and lots of batteries included for ML and LLM workloads.

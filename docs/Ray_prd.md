Below is a **step-by-step “container-first” walkthrough** that turns your *hello-world* script into a fully containerised Ray demo, proves that the **map (parallel tasks) + reduce (aggregation) + shared state (actor)** logic still works, and shows how to re-use the *exact* same image on AWS.

---

## 1 ⃣ Create a Ray image that bundles your code

**Dockerfile**

```dockerfile
# ----- Dockerfile (project root) -----
FROM python:3.11-slim

# 1. Install Ray + helper libs
RUN pip install --no-cache-dir "ray[default]==2.9.0"

# 2. Copy your demo script
WORKDIR /app
COPY hello_ray.py .

# 3. Default entrypoint = run the script
CMD ["python", "hello_ray.py"]
```

```bash
docker build -t ray-hello:latest .
```

---

## 2 ⃣ Run the demo **inside the container** (single-node Ray)

```bash
docker run --rm -it \
  --name ray-head \
  -p 8265:8265  \        # Ray dashboard
  -p 10001:10001 \       # Job-submission API
  ray-hello:latest
```

Inside the container, Ray auto-starts via `ray.init()` in your script and:

* **Tasks (`slow_task`)** run in local Ray workers.
* **Actor (`Counter`)** runs in a separate worker process yet shares state via Ray’s object store.
* Dashboard available at `http://localhost:8265`.
* When the script exits the container stops — clean demo. ([Ray][1])

---

## 3 ⃣ Optional: give *each* map-task its **own sandbox**

Add a `runtime_env` on the decorator:

```python
@ray.remote(
    num_cpus=1,
    runtime_env={"container": {"image": "ray-hello:latest"}}  # ← per-task container
)
def slow_task(x):
    ...
```

Ray now spins up **one lightweight container per task** using your image, then tears them down automatically — great for education on “task-level isolation”. ([Ray][2])

---

## 4 ⃣ Turn the same image into a tiny **local cluster**

```yaml
# docker-compose.yml (minimal)
version: "3.9"
services:
  head:
    image: ray-hello:latest
    command: ray start --head --port=6379 --dashboard-host=0.0.0.0
    ports: [ "8265:8265", "10001:10001" ]
  worker:
    image: ray-hello:latest
    depends_on: [ head ]
    environment:
      - RAY_HEAD_IP=head   # workers join the head
    command: >
      bash -c "ray start --address=$${RAY_HEAD_IP}:6379 --block"
    deploy:
      replicas: 2
```

```bash
docker compose up --scale worker=2     # spin head + 2 workers
export RAY_ADDRESS="http://localhost:8265"
ray job submit -- python /app/hello_ray.py   # runs on the cluster
```

*All three containers run the identical code/image, so “works-on-my-machine” stays true.* ([Ray][3])

---

## 5 ⃣ Reuse the image on **AWS EC2** in minutes

1. **Push** the image to ECR.
2. **Create** a Ray cluster YAML (excerpt):

```yaml
docker:
  image: "<acct>.dkr.ecr.<region>.amazonaws.com/ray-hello:latest"
  container_name: ray_container
head_node: { InstanceType: t3.medium }
worker_nodes: { InstanceType: t3.large }
```

3. Launch:

```bash
ray up aws_cluster.yaml      # provisions EC2 + pulls your container
ray attach aws_cluster.yaml  # SSH into head
python /app/hello_ray.py     # same demo, now on AWS
```

The cluster launcher ensures every EC2 node boots **inside your Docker image**, so behaviour matches local runs. ([Ray][4], [ray-robert.readthedocs.io][5])

---

## 6 ⃣ Show a *reduce* step & shared state (tiny tweak)

Add after the `results = ray.get(..)` line:

```python
total = sum(results)                 # simple reduce
print(f"Sum of squares: {total}")
```

Everything still happens inside Ray’s object store, so data moves via shared memory even across containers on the same node.

---

### Key Take-aways

| Need                          | How it’s met                                                              |
| ----------------------------- | ------------------------------------------------------------------------- |
| **Fully containerised**       | Single Dockerfile → identical image for local, Compose, or AWS            |
| **Parallel analysis (“map”)** | `slow_task.remote` fan-out (optionally each task in its own container)    |
| **Aggregation (“reduce”)**    | Collect futures → aggregate in driver or another Ray task                 |
| **Shared state**              | Ray Actor (`Counter`) persists across calls & containers via object store |
| **Portability**               | Build once, run anywhere Ray runs—desktop, Compose, EKS, or VM            |

With this pattern you can swap in real NCBI analysis code for `slow_task`, grow the worker replica count, and still keep the same container workflow for students or prod experiments.

[1]: https://docs.ray.io/en/latest/ray-observability/getting-started.html?utm_source=chatgpt.com "Ray Dashboard — Ray 2.48.0 - Ray Docs"
[2]: https://docs.ray.io/en/latest/ray-core/api/doc/ray.runtime_env.RuntimeEnv.html?utm_source=chatgpt.com "ray.runtime_env.RuntimeEnv — Ray 2.48.0 - Ray Docs"
[3]: https://docs.ray.io/en/latest/cluster/running-applications/job-submission/quickstart.html?utm_source=chatgpt.com "Quickstart using the Ray Jobs CLI"
[4]: https://docs.ray.io/en/latest/ray-core/starting-ray.html?utm_source=chatgpt.com "Starting Ray — Ray 2.48.0 - Ray Docs"
[5]: https://ray-robert.readthedocs.io/en/latest/using-ray-and-docker-on-a-cluster.html?utm_source=chatgpt.com "Using Ray and Docker on a Cluster (EXPERIMENTAL)"

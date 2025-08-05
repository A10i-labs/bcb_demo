#!/usr/bin/env python3
"""
Ray Quick Start - Minimal Example

The simplest possible Ray demo showing:
1. Parallel tasks
2. Stateful actors  
3. How much faster parallel execution is
"""

import ray
import time

# Start Ray
ray.init()

print("🚀 Ray Quick Start")
print(f"Available CPUs: {ray.available_resources().get('CPU', 0)}")

# =============================================================================
# PARALLEL TASKS - Functions that run simultaneously 
# =============================================================================

@ray.remote
def slow_task(x):
    """A slow function - perfect for parallelization"""
    time.sleep(1)
    return x * x

print("\n⏱️  Running 4 tasks in parallel...")
start = time.time()

# This line does the magic - runs all 4 tasks simultaneously!
futures = [slow_task.remote(i) for i in range(1, 5)]
results = ray.get(futures)  # Wait for all to complete

parallel_time = time.time() - start

print(f"Results: {results}")
print(f"Parallel time: {parallel_time:.1f}s (sequential would be ~4s)")

# =============================================================================
# STATEFUL ACTORS - Objects that keep state between calls
# =============================================================================

@ray.remote
class Counter:
    """A distributed counter that remembers its state"""
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
        return self.count
    
    def get_count(self):
        return self.count

print("\n🤖 Stateful actor demo...")

# Create a distributed counter
counter = Counter.remote()

# Call it multiple times - it remembers state
print(f"Count: {ray.get(counter.increment.remote())}")  # 1
print(f"Count: {ray.get(counter.increment.remote())}")  # 2
print(f"Count: {ray.get(counter.increment.remote())}")  # 3
print(f"Final: {ray.get(counter.get_count.remote())}")  # 3

print("\n✅ That's Ray! Key points:")
print("   • Add @ray.remote to any function → instant parallelization")
print("   • Add @ray.remote to any class → distributed stateful objects")
print("   • Use .remote() to call them, ray.get() to collect results")
print("   • Perfect for scaling Python workloads without code rewrites")

ray.shutdown() 
#!/usr/bin/env python3
"""
Ray Hello World - A Simple Distributed Computing Example

This demonstrates Ray's core concepts:
1. Remote tasks (@ray.remote functions)
2. Remote actors (@ray.remote classes)  
3. Parallel execution and object sharing
"""

import ray
import time
import random

# Initialize Ray (connects to existing cluster or starts local one)
ray.init()

print("🚀 Ray Hello World - Distributed Computing Demo")
print(f"Ray cluster info: {ray.cluster_resources()}")

# =============================================================================
# 1. BASIC REMOTE TASKS - Stateless functions that run in parallel
# =============================================================================

@ray.remote
def slow_square(x):
    """A function that takes time to compute - perfect for parallelization"""
    time.sleep(1)  # Simulate heavy computation
    result = x * x
    print(f"  Worker computed {x}² = {result}")
    return result

@ray.remote
def slow_process_data(data_chunk):
    """Simulate processing a chunk of biological data"""
    time.sleep(random.uniform(0.5, 1.5))  # Variable processing time
    processed = [item.upper() for item in data_chunk if len(item) > 3]
    return f"Processed {len(processed)} items from chunk of {len(data_chunk)}"

# =============================================================================
# 2. REMOTE ACTORS - Stateful objects that maintain state across calls
# =============================================================================

@ray.remote
class DataProcessor:
    """A stateful worker that maintains processing statistics"""
    
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.tasks_completed = 0
        self.total_items_processed = 0
    
    def process_batch(self, batch_data):
        """Process a batch and update internal state"""
        time.sleep(0.5)  # Simulate processing time
        processed = len([item for item in batch_data if item.startswith('A')])
        
        self.tasks_completed += 1
        self.total_items_processed += len(batch_data)
        
        return {
            'worker_id': self.worker_id,
            'batch_size': len(batch_data),
            'processed_count': processed,
            'total_tasks': self.tasks_completed
        }
    
    def get_stats(self):
        """Return worker statistics"""
        return {
            'worker_id': self.worker_id,
            'tasks_completed': self.tasks_completed,
            'total_items_processed': self.total_items_processed
        }

# =============================================================================
# DEMO 1: Parallel Task Execution
# =============================================================================

print("\n📊 Demo 1: Parallel Mathematical Computation")
print("Computing squares of numbers 1-8 in parallel...")

start_time = time.time()

# Submit all tasks in parallel (non-blocking)
futures = [slow_square.remote(i) for i in range(1, 9)]

# Wait for all results (blocking)
results = ray.get(futures)

end_time = time.time()

print(f"Results: {results}")
print(f"⏱️  Parallel execution time: {end_time - start_time:.2f} seconds")
print(f"   (Sequential would take ~8 seconds)")

# =============================================================================
# DEMO 2: Data Processing Pipeline
# =============================================================================

print("\n🧬 Demo 2: Biological Data Processing Pipeline")

# Sample biological data (gene names, protein sequences, etc.)
bio_data = [
    ["ATCG", "GCTA", "TGCA", "CGAT", "AATG"],
    ["PROTEIN_A", "ENZYME_B", "RECEPTOR_C", "KINASE_D"],
    ["ATP", "NADH", "GLUCOSE", "GLYCOGEN", "LACTATE"],
    ["HEMOGLOBIN", "INSULIN", "COLLAGEN", "KERATIN"]
]

print("Processing biological data chunks in parallel...")

start_time = time.time()

# Process all chunks in parallel
processing_futures = [slow_process_data.remote(chunk) for chunk in bio_data]
processing_results = ray.get(processing_futures)

end_time = time.time()

for result in processing_results:
    print(f"  📋 {result}")

print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")

# =============================================================================
# DEMO 3: Stateful Actors Working Together
# =============================================================================

print("\n🤖 Demo 3: Multiple Stateful Workers (Actors)")

# Create multiple worker actors
num_workers = 3
workers = [DataProcessor.remote(f"Worker-{i+1}") for i in range(num_workers)]

# Sample dataset to distribute
dataset = [
    ["ALBUMIN", "ANTIBODY", "ANTIGEN", "ALKALINE"],
    ["BACTERIAL", "BIOMASS", "BUFFER", "BASELINE"],
    ["COLLAGEN", "CALCIUM", "CATALYST", "CELLULAR"],
    ["DEXTROSE", "DILUTION", "DENSITY", "DOMAIN"],
    ["ENZYME", "EPITOPE", "EXPRESSION", "EXTRACT"],
    ["FIBRIN", "FLUORESCENCE", "FRACTION", "FUSION"]
]

print(f"Distributing {len(dataset)} batches across {num_workers} workers...")

# Distribute work across workers
batch_futures = []
for i, batch in enumerate(dataset):
    worker = workers[i % num_workers]  # Round-robin distribution
    batch_futures.append(worker.process_batch.remote(batch))

# Collect all batch results
batch_results = ray.get(batch_futures)

print("\n📈 Batch Processing Results:")
for result in batch_results:
    print(f"  {result['worker_id']}: processed {result['processed_count']}/{result['batch_size']} items (total tasks: {result['total_tasks']})")

# Get final statistics from each worker
print("\n📊 Final Worker Statistics:")
stats_futures = [worker.get_stats.remote() for worker in workers]
final_stats = ray.get(stats_futures)

for stats in final_stats:
    print(f"  {stats['worker_id']}: {stats['tasks_completed']} tasks, {stats['total_items_processed']} total items processed")

# =============================================================================
# CLEANUP
# =============================================================================

print("\n✅ Demo completed! Key takeaways:")
print("   • @ray.remote functions run in parallel across available CPU cores")
print("   • @ray.remote classes maintain state and can handle multiple requests")
print("   • ray.get() collects results from distributed computations")
print("   • Perfect for embarrassingly parallel workloads (bioinformatics, data processing)")

# Clean up Ray
ray.shutdown()
print("\n🔄 Ray cluster shut down.") 
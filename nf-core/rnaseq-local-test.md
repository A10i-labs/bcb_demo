# nf-core/rnaseq Local Test Run Guide

## Overview

This document describes how to run the nf-core/rnaseq pipeline locally on macOS (Apple Silicon) with a test dataset. The guide covers system requirements, setup, execution, and understanding how the test data works.

**Date**: October 13, 2025  
**System**: MacBook Pro M3 Pro (Apple Silicon)  
**Pipeline Version**: nf-core/rnaseq 3.20.0  
**Reference Documentation**: https://nf-co.re/rnaseq/3.20.0/docs/usage/

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Running the Test Pipeline](#running-the-test-pipeline)
4. [Understanding Test Data Inputs](#understanding-test-data-inputs)
5. [Results and Output](#results-and-output)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## System Requirements

### Hardware Verified

- **CPU**: Apple M3 Pro (12 cores) - ARM64 architecture
- **RAM**: 36 GB
- **Storage**: ~500 MB for test run (including Docker images)

### Software Required

- **Docker**: Version 28.4.0 or later
- **Nextflow**: Version 25.04.8 or later (requires ≥24.10.5)
- **Java**: Included with Nextflow installation

---

## Prerequisites Installation

### 1. Verify Docker Installation

```bash
# Check Docker is installed and running
docker --version
# Output: Docker version 28.4.0, build d8eb465

# Verify Docker daemon is running
docker ps
# Should return an empty list or running containers (no errors)
```

### 2. Check System Resources

```bash
# Check CPU count
sysctl -n hw.ncpu
# Output: 12

# Check RAM (in GB)
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}'
# Output: 36 GB

# Check chip architecture
system_profiler SPHardwareDataType | grep -E "Chip|Memory"
# Output: Chip: Apple M3 Pro, Memory: 36 GB
```

### 3. Install Nextflow via Homebrew

```bash
# Install Nextflow
brew install nextflow

# Verify installation
nextflow -version
# Output:
#   N E X T F L O W
#   version 25.04.8 build 5956
```

---

## Running the Test Pipeline

### Quick Start Command

The simplest way to run the test:

```bash
# Create working directory
mkdir -p ~/Github/temp/rnasq-test
cd ~/Github/temp/rnasq-test

# Run the pipeline with test profile
nextflow run nf-core/rnaseq \
    -r 3.20.0 \
    -profile test,docker \
    --outdir results \
    --max_memory 8.GB \
    --max_cpus 4
```

### Command Breakdown

| Parameter | Purpose |
|-----------|---------|
| `-r 3.20.0` | Specifies pipeline version 3.20.0 |
| `-profile test,docker` | Uses test dataset + Docker containers |
| `--outdir results` | Output directory for results |
| `--max_memory 8.GB` | Limits memory usage to 8GB |
| `--max_cpus 4` | Limits CPU usage to 4 cores |

### Resume After Interruption

If the pipeline is interrupted or fails, resume from the last successful step:

```bash
nextflow run nf-core/rnaseq \
    -r 3.20.0 \
    -profile test,docker \
    --outdir results \
    --max_memory 8.GB \
    --max_cpus 4 \
    -resume
```

The `-resume` flag uses Nextflow's caching to skip completed steps.

---

## Understanding Test Data Inputs

### How the Test Profile Works

When you use `-profile test`, Nextflow reads the test configuration file located at:

```
~/.nextflow/assets/nf-core/rnaseq/conf/test.config
```

This configuration file contains **URLs** pointing to test data hosted on GitHub, not local files!

### Test Configuration Contents

```groovy
params {
    // Input samplesheet (CSV with FASTQ file URLs)
    input = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../samplesheet_test.csv'

    // Reference genome (tiny Saccharomyces cerevisiae subset)
    fasta = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../genome.fasta'
    gtf   = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../genes_with_empty_tid.gtf.gz'
    
    // Pre-built indices (saves time during testing)
    salmon_index = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../salmon.tar.gz'
    hisat2_index = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../hisat2.tar.gz'
    rsem_index   = 'https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab.../rsem.tar.gz'
}
```

### The Samplesheet

The test samplesheet defines 7 FASTQ files from a yeast RNA-seq experiment:

```csv
sample,fastq_1,fastq_2,strandedness
WT_REP1,https://raw.githubusercontent.com/.../SRR6357070_1.fastq.gz,https://raw.githubusercontent.com/.../SRR6357070_2.fastq.gz,auto
WT_REP1,https://raw.githubusercontent.com/.../SRR6357071_1.fastq.gz,https://raw.githubusercontent.com/.../SRR6357071_2.fastq.gz,auto
WT_REP2,https://raw.githubusercontent.com/.../SRR6357072_1.fastq.gz,https://raw.githubusercontent.com/.../SRR6357072_2.fastq.gz,reverse
RAP1_UNINDUCED_REP1,https://raw.githubusercontent.com/.../SRR6357073_1.fastq.gz,,reverse
RAP1_UNINDUCED_REP2,https://raw.githubusercontent.com/.../SRR6357074_1.fastq.gz,,reverse
RAP1_UNINDUCED_REP2,https://raw.githubusercontent.com/.../SRR6357075_1.fastq.gz,,reverse
RAP1_IAA_30M_REP1,https://raw.githubusercontent.com/.../SRR6357076_1.fastq.gz,https://raw.githubusercontent.com/.../SRR6357076_2.fastq.gz,reverse
```

### Test Dataset Details

| Property | Value |
|----------|-------|
| **Organism** | *Saccharomyces cerevisiae* (yeast) |
| **Original Study** | GSE110004 - RAP1 depletion study |
| **Sample Types** | Wild-type controls + RAP1 knockdown |
| **Library Types** | Both paired-end and single-end |
| **Total Files** | 10 FASTQ files (7 R1, 3 R2) |
| **Total Size** | ~26 MB (highly subsampled for testing) |
| **Read Count** | ~10,000 reads per sample |
| **Repository** | https://github.com/nf-core/test-datasets |
| **Commit** | 626c8fab639062eade4b10747e919341cbf9b41a |

### Automatic File Download Process

**You don't need to manually download any files!** Here's what happens:

1. **Pipeline Start**: Nextflow reads the samplesheet URLs
2. **First Download**: Files are downloaded from GitHub to local cache
3. **Caching**: Files stored in `work/stage-<hash>/` directory
4. **Symbolic Links**: Process directories contain symlinks to cached files
5. **Reuse**: With `-resume`, cached files are reused (no re-download)

```bash
# Check cached FASTQ files
find work/stage-*/*/SRR*.fastq.gz -type f

# Example output:
# work/stage-275aa59b.../bf/780c5156.../SRR6357070_1.fastq.gz  # 2.1 MB
# work/stage-275aa59b.../9d/cb084608.../SRR6357070_2.fastq.gz  # 2.1 MB
# ... (etc)

# Total cached data
du -sh work/stage-*/
# Output: 26M
```

---

## Results and Output

### Pipeline Execution Summary

The test run completed with:

- **Total Processes**: 141
- **Successful**: 140 (99.3%)
- **Failed**: 1 (MultiQC - architecture incompatibility)
- **Execution Time**: ~35-40 minutes
- **Output Size**: ~58 MB

### Output Directory Structure

```
results/
├── bbsplit/              # 20 KB  - Contamination screening
├── custom/               # 432 KB - Custom processing
├── fastqc/               # 15 MB  - Quality control reports
│   ├── raw/              #        - QC on raw FASTQ files
│   └── trim/             #        - QC on trimmed FASTQ files
├── fq_lint/              # 60 KB  - FASTQ validation logs
├── pipeline_info/        # 10 MB  - Execution reports & logs
│   ├── execution_report_*.html      # Resource usage
│   ├── execution_timeline_*.html    # Timeline visualization
│   └── pipeline_dag_*.html          # Workflow diagram
├── salmon/               # 460 KB - Pseudoalignment results
│   ├── deseq2_qc/        #        - DESeq2 QC plots
│   ├── salmon.merged.gene_counts.tsv
│   └── salmon.merged.transcript_counts.tsv
├── star_salmon/          # 32 MB  - Main alignment results
│   ├── *.sorted.bam      #        - Aligned reads (BAM format)
│   ├── *.bigWig          #        - Coverage tracks
│   ├── deseq2_qc/        #        - DESeq2 QC plots
│   ├── dupradar/         #        - Duplication analysis
│   ├── featurecounts/    #        - Gene counts
│   ├── picard_metrics/   #        - Alignment metrics
│   ├── qualimap/         #        - Comprehensive QC
│   ├── rseqc/            #        - RNA-seq specific QC
│   ├── salmon/           #        - Quantification
│   ├── stringtie/        #        - Transcript assembly
│   └── salmon.merged.gene_counts.tsv
└── trimgalore/           # 32 KB  - Adapter trimming logs
```

### Key Output Files

#### Gene Expression Matrices

```bash
# Gene counts from STAR + Salmon
results/star_salmon/salmon.merged.gene_counts.tsv

# Transcript counts
results/star_salmon/salmon.merged.transcript_counts.tsv

# Pseudoalignment counts
results/salmon/salmon.merged.gene_counts.tsv
```

#### Quality Control Reports

```bash
# Individual sample FastQC reports (HTML)
results/fastqc/raw/*_fastqc.html
results/fastqc/trim/*_fastqc.html

# Pipeline execution reports
results/pipeline_info/execution_report_*.html
results/pipeline_info/execution_timeline_*.html
results/pipeline_info/pipeline_dag_*.html
```

#### Alignment Files

```bash
# BAM files (aligned reads)
results/star_salmon/*/*.sorted.bam
results/star_salmon/*/*.sorted.bam.bai  # BAM index

# BigWig files (genome coverage tracks)
results/star_salmon/*/*.bigWig
```

### Viewing Results

Open any HTML report in your browser:

```bash
# Open a FastQC report
open results/fastqc/raw/WT_REP1_raw_1_fastqc.html

# Open execution timeline
open results/pipeline_info/execution_timeline_*.html

# Open workflow diagram
open results/pipeline_info/pipeline_dag_*.html
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. MultiQC Fails on Apple Silicon

**Error Message**:
```
WARNING: The requested image's platform (linux/amd64) does not match 
the detected host platform (linux/arm64/v8)
Illegal instruction
```

**Cause**: MultiQC container is x86_64 only, incompatible with ARM architecture.

**Impact**: Only affects the final aggregated QC report. All scientific analysis completes successfully.

**Workaround**: 
- View individual QC reports instead of the combined MultiQC report
- All important QC metrics are available in separate HTML files

#### 2. Docker Container Download Failures

**Error Message**:
```
docker: failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://quay.io/...": EOF
```

**Cause**: Transient network issues or quay.io rate limiting.

**Solution**:
```bash
# Pre-pull the problematic container
docker pull quay.io/biocontainers/qualimap:2.3--hdfd78af_0

# Resume the pipeline
nextflow run nf-core/rnaseq -r 3.20.0 -profile test,docker --outdir results -resume
```

#### 3. Out of Memory Errors

**Symptom**: Process killed with exit code 137 or OOM errors.

**Solution**: Increase memory limits:
```bash
nextflow run nf-core/rnaseq \
    -r 3.20.0 \
    -profile test,docker \
    --outdir results \
    --max_memory 12.GB \  # Increased from 8GB
    --max_cpus 4
```

#### 4. Work Directory Size

The `work/` directory can grow large with caching:

```bash
# Check work directory size
du -sh work/

# Clean up after successful completion
rm -rf work/

# Or use Nextflow's clean command
nextflow clean -f
```

---

## Next Steps

### Running with Your Own Data

1. **Create a samplesheet** (`my_samples.csv`):

```csv
sample,fastq_1,fastq_2,strandedness
SAMPLE_1,/path/to/sample1_R1.fastq.gz,/path/to/sample1_R2.fastq.gz,auto
SAMPLE_2,/path/to/sample2_R1.fastq.gz,/path/to/sample2_R2.fastq.gz,auto
SAMPLE_3,/path/to/sample3_R1.fastq.gz,,reverse
```

2. **Prepare reference files**:
   - Genome FASTA (`.fa` or `.fasta`)
   - Gene annotation GTF (`.gtf`)
   - Or use iGenomes: `--genome GRCh38`

3. **Run the pipeline**:

```bash
nextflow run nf-core/rnaseq \
    -r 3.20.0 \
    --input my_samples.csv \
    --outdir my_results \
    --fasta /path/to/genome.fa \
    --gtf /path/to/genes.gtf \
    --aligner star_salmon \
    -profile docker \
    --max_memory 16.GB \
    --max_cpus 8
```

### Using iGenomes References

For common organisms, use pre-configured genomes:

```bash
nextflow run nf-core/rnaseq \
    -r 3.20.0 \
    --input my_samples.csv \
    --outdir my_results \
    --genome GRCh38 \  # Human genome
    -profile docker
```

Available genomes: `GRCh38`, `GRCm39`, `mm10`, `hg38`, `hg19`, etc.

### Downstream Analysis

After the pipeline completes:

1. **Differential Expression Analysis**:
   - Use `nf-core/differentialabundance` pipeline
   - Or analyze counts in R with DESeq2/edgeR

2. **Visualization**:
   - Load BigWig files in IGV (Integrative Genomics Viewer)
   - Visualize BAM files for read alignments

3. **Further QC**:
   - Review FastQC reports for quality issues
   - Check RSeQC reports for library strandedness
   - Examine Qualimap for alignment quality

### Learning Resources

- **nf-core/rnaseq Documentation**: https://nf-co.re/rnaseq/3.20.0
- **Nextflow Tutorial**: https://training.nextflow.io/
- **nf-core Training**: https://nf-co.re/docs/usage/getting_started
- **RNA-seq Analysis Guide**: https://nf-co.re/rnaseq/3.20.0/docs/usage
- **Pipeline Parameters**: https://nf-co.re/rnaseq/3.20.0/parameters

---

## Summary

✅ **Successfully ran** nf-core/rnaseq 3.20.0 on Apple Silicon  
✅ **Completed** 140/141 processes (99.3% success rate)  
✅ **Generated** comprehensive RNA-seq analysis results  
✅ **Understood** how test data is automatically downloaded and cached  
✅ **Learned** how to adapt the workflow for custom datasets  

The pipeline demonstrates excellent compatibility with macOS and Apple Silicon, with only minor compatibility issues in the final reporting step (MultiQC).

---

## Appendix: Full System Specifications

```
Hardware:
  - Chip: Apple M3 Pro
  - CPU Cores: 12
  - Memory: 36 GB
  - Architecture: ARM64 (arm64/v8)

Software:
  - OS: macOS 24.6.0 (Sequoia)
  - Shell: /bin/zsh
  - Docker: 28.4.0, build d8eb465
  - Nextflow: 25.04.8 build 5956
  - Java: Embedded in Nextflow

Pipeline:
  - Name: nf-core/rnaseq
  - Version: 3.20.0
  - Profile: test,docker
  - Execution Time: ~35-40 minutes
  - Max Resources: 8GB RAM, 4 CPUs
```

---

**Document Version**: 1.0  
**Last Updated**: October 13, 2025  
**Maintained By**: hb


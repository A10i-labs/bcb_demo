# nf-core/demo pipeline

## docker profile

```
 OUTDIR=results
nextflow run nf-core/demo \
  -r 1.0.2 \
  -profile docker \
  --input samplesheet.csv \
  --outdir "${OUTDIR}" \
  -c cap.config \
  -resume

```

## config (cap.config)

```
process {
  // Safety defaults (apply if a step doesn't set its own)
  cpus   = 1
  memory = 6.GB
  time   = 2.h

  // Run serially to keep peak RAM low
  maxForks = 1

  // Explicit per-step caps for this pipeline
  withName: 'NFCORE_DEMO:DEMO:SEQTK_TRIM' { 
    memory = 3.GB
    cpus   = 1
    time   = 2.h
  }

  withName: 'NFCORE_DEMO:DEMO:FASTQC' { 
    memory = 1.5.GB
    cpus   = 1
    time   = 1.h
  }

  // Use MultiQC's multi-arch image to avoid amd64-on-ARM segfaults
  withName: 'NFCORE_DEMO:DEMO:MULTIQC' { 
    container = 'ghcr.io/multiqc/multiqc:v1.29'
    memory    = 2.GB
    cpus      = 1
    time      = 1.h
  }
}

executor {
  // Don’t queue more than one task at a time
  queueSize = 1
}

docker {
  // Hard-cap container memory so nothing can burst past your system limit
  runOptions = "-m 6g"
}
```

# README: SwissProt and NR Database Relationship, Structure, and Findings

## Overview

This document summarizes the relationship between the SwissProt and NR (Non-Redundant) protein databases, describes the structure and content of NR, and presents key findings from both the repository and authoritative web sources. It also documents the steps taken to download sample data and perform schema analysis.

---

## 1. What is the NR Database?

- **NR (Non-Redundant) Database** is a comprehensive protein sequence collection maintained by NCBI.
- It combines sequences from multiple sources:
  - **GenBank/GenPept** (unreviewed, user-submitted)
  - **RefSeq** (curated by NCBI)
  - **SwissProt** (manually reviewed, UniProt)
  - **TrEMBL** (computational, UniProt)
  - **PDB, PIR, PRF** (other curated/experimental sources)
- **Goal:** Remove exact duplicates, but keep all unique sequences, even if they have different taxonomic or functional annotations.

---

## 2. Data Collection Process: Steps Taken

### 2.1 Installing Tools

1. **Conda Installation:** Installed Miniconda for package management
2. **NCBI Datasets CLI:** Installed via conda for downloading sample protein sequences

   ```bash
   conda install -c conda-forge ncbi-datasets-cli
   ```

3. **EDirect Tools:** Installed for accessing NR database directly

   ```bash
   conda install -c bioconda entrez-direct
   ```

### 2.2 Sample Data Downloads

We downloaded several small protein datasets for analysis:

#### A. NCBI Datasets CLI Downloads

1. **SARS-CoV-2 ORF10 Protein** (4.8KB)

   ```bash
   datasets download virus protein ORF10 --refseq --filename tiny_sars_cov2_orf10.zip
   ```

   - Contains: 1 tiny protein sequence (38 amino acids)
   - Perfect for quick testing

2. **SARS-CoV-2 Envelope Protein** (4.8KB)

   ```bash
   datasets download virus protein E --refseq --filename sars_cov2_envelope_proteins.zip
   ```

   - Contains: 1 small protein sequence (75 amino acids)

3. **E. coli Reference Proteins** (1.9MB)

   ```bash
   datasets download genome taxon "Escherichia coli" --reference --include protein --filename ecoli_reference_proteins.zip
   ```

   - Contains: 4,298 protein sequences from E. coli K-12 reference genome

#### B. EDirect Downloads from NR Database

4. **NR Sample Proteins** (1.2KB FASTA + 49KB metadata)

   ```bash
   efetch -db protein -id "NP_000508.1,NP_001009.1,NP_001001.1,NP_001002.1,NP_001003.1" -format fasta > NR_sample_5proteins.fasta
   efetch -db protein -id "NP_000508.1,NP_001009.1,NP_001001.1,NP_001002.1,NP_001003.1" -format gp > NR_sample_5proteins_metadata.txt
   ```

   - Contains: 5 human proteins with full metadata

#### C. SwissProt Database Sample

5. **SwissProt Database** (258MB uncompressed)
   - Downloaded and unzipped SwissProt database from NCBI FTP
   - Contains: ~570,000 manually curated protein sequences

### 2.3 File Organization

```
datasets/
├── tiny_sars_cov2_orf10/
├── sars_envelope/
├── ecoli/
├── NR_sample_5proteins.fasta
├── NR_sample_5proteins_metadata.txt
└── NR/
    ├── SwissProt database (258MB)
    └── README.md (this file)
```

---

## 3. Data Schema Analysis

### 3.1 SwissProt Database Schema

Based on analysis of the uncompressed SwissProt database:

**File Format:** Text-based FASTA format with rich annotation
**Structure:** Each entry consists of:

#### Header Line (starts with ">")

```
>ACCESSION.VERSION RecName: Full=PROTEIN_NAME; AltName: Full=ALTERNATE_NAME; Short=ABBREVIATION [ORGANISM]
```

#### Field Meanings

- **ACCESSION.VERSION**: Unique UniProt accession (e.g., Q5R654.1)
- **RecName: Full=...**: Recommended full protein name
- **AltName: Full=...**: Alternative full protein names (may be multiple)
- **Short=...**: Short names or abbreviations
- **[ORGANISM]**: Species name in brackets

#### Example Entry

```
>Q5R654.1 RecName: Full=Histone-binding protein RBBP7; AltName: Full=Nucleosome-remodeling factor subunit RBAP46; AltName: Full=Retinoblastoma-binding protein 7; Short=RBBP-7 [Pongo abelii]
MASKEMFEDTVEERVINEEYKIWKKNTPFLYDLVMTHALQWPSLTVQWLPEVTKPEGKDYALHWLVLGTHTSDEQNHLVV
ARVHIPNDDAQFDASHCDSDKGEFGGFGSVTGKIECEIKINHEGEVNRARYMPQNPHIIATKTPSSGVLVFDYTKHPAKP
```

### 3.2 NR Database Sample Schema

From our NR sample analysis:

**Downloaded NR Sample Proteins:**

| Accession | Protein Name | Length (aa) | Organism | Function |
|-----------|--------------|-------------|-----------|----------|
| NP_000508.1 | Hemoglobin subunit alpha | 142 | Homo sapiens | Oxygen transport |
| NP_001001.1 | Ribosomal protein S6 | 249 | Homo sapiens | Protein synthesis |
| NP_001002.1 | Small ribosomal subunit protein eS7 | 194 | Homo sapiens | Protein synthesis |
| NP_001003.1 | Small ribosomal subunit protein uS8 | 208 | Homo sapiens | Protein synthesis |
| NP_001009.1 | Ribosomal protein L7 | 248 | Homo sapiens | Protein synthesis |

**Taxonomic Distribution:**

- **Homo sapiens**: 5 proteins (100% human in our sample)
- All entries are from RefSeq (NP_ prefix indicates RefSeq)

---

## 4. SwissProt as a Subset of NR

- **SwissProt** is a high-quality, manually curated subset of NR.
- All SwissProt entries are included in NR, but NR also contains many more sequences from less curated sources.
- SwissProt entries are reviewed and have authoritative taxonomic assignments, while NR can contain conflicting or multiple taxonomic assignments for the same sequence.

---

## 5. Structure of NR Database

- **Format:** FASTA (nr.gz on NCBI FTP)
- **Header Example:**

  ```
  >gi|123456|ref|NP_123456.1| protein name [Homo sapiens]
  MSEQUENCE...
  ```

- **Merged Entries:**
  - The same sequence may appear with different IDs and organism names, or with multiple taxonomic assignments in the header.
  - Example:

    ```
    >gi|123456|ref|NP_123456.1|sp|P12345.1|tr|Q54321.1| protein name [Homo sapiens] [Mus musculus] [Bos taurus]
    MSEQUENCE...
    ```

- **Size:** Enormous (186GB compressed as of 2024)

---

## 6. Key Findings from the Repository and Web

- The repo downloads NR.gz and processes it to parse sequence IDs, taxonomic assignments, and metadata.
- Many sequences in NR have multiple or conflicting taxonomic assignments due to merging from different sources or mislabeling.
- The repo's pipeline detects and corrects these misclassifications using clustering and annotation analysis.
- SwissProt is a curated, high-quality subset of NR, but NR is much larger and more heterogeneous.
- For BLAST and other tools, SwissProt can be used as a mask or alias database with NR ([BioStars discussion](https://www.biostars.org/p/100437/)).
- NCBI FTP provides both databases: [NCBI FTP: /blast/db/FASTA/](https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/)
- More details: [NCBI documentation](https://www.nlm.nih.gov/ncbi/workshops/2023-08_BLAST_evol/databases.html)

---

## 7. Database Comparison Summary

| File            | What it Contains                | Size (2024) | Quality | Notes                                 |
|-----------------|---------------------------------|------------|---------|---------------------------------------|
| `nr.gz`         | All unique protein sequences    | 186GB      | Mixed   | Includes SwissProt, GenBank, etc.     |
| `swissprot.gz`  | Curated SwissProt proteins only | 137MB      | High    | Subset of NR, manually reviewed       |

---

## 8. References

- [NCBI FTP: /blast/db/FASTA/](https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/)
- [NCBI BLAST+ Documentation](https://www.nlm.nih.gov/ncbi/workshops/2023-08_BLAST_evol/databases.html)
- [UniProt/SwissProt FASTA Headers](https://www.uniprot.org/help/fasta-headers)
- [BioStars: Using SwissProt with BLAST](https://www.biostars.org/p/100437/)

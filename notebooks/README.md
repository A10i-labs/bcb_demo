# Protein Sequence Analysis Demo

## 📁 Project Structure

```
project_root/
├── dataset/                              # Data files
│   ├── NR_sample_5proteins.fasta        # Protein sequences
│   └── NR_sample_5proteins_metadata.txt # Sequence metadata
├── Demo_non_redundant_db.ipynb          # Main protein analysis notebook
├── Phylogenetic_test.ipynb              # Phylogenetic analysis notebook
├── phylogenetic_utils.py                # Phylogenetic analysis library
├── quick_demo.py                        # Standalone Python script
└── README_Demo.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

Install required packages:

```bash
pip install biopython pandas numpy matplotlib seaborn scipy networkx
```

### Running the Analysis

#### 1. **Main Protein Analysis** (`Demo_non_redundant_db.ipynb`)

- **Purpose**: Comprehensive protein sequence analysis
- **Features**: Sequence properties, amino acid composition, functional annotation
- **Run**: Open in Jupyter and run all cells
- **Data**: Uses `dataset/NR_sample_5proteins.fasta` and metadata

#### 2. **Phylogenetic Analysis** (`Phylogenetic_test.ipynb`)

- **Purpose**: Evolutionary relationship analysis
- **Features**: Distance matrices, dendrograms, phylogenetic trees
- **Run**: Open in Jupyter and run all cells
- **Dependencies**: Imports `phylogenetic_utils.py`

#### 3. **Quick Demo Script** (`quick_demo.py`)

- **Purpose**: Standalone Python script version
- **Run**: `python quick_demo.py`
- **Output**: Command-line analysis results

## 📊 Expected Outputs

### Main Analysis

- Sequence property plots (length, molecular weight, pI)
- Amino acid composition heatmaps
- Functional classification charts
- Distance matrices

### Phylogenetic Analysis

- Distance heatmaps
- UPGMA dendrograms
- Network trees
- Neighbor-joining trees (when available)

## 🔧 Usage Examples

### Quick phylogenetic analysis

```python
from phylogenetic_utils import run_quick_analysis
analyzer, results = run_quick_analysis('dataset/NR_sample_5proteins.fasta')
```

### Individual visualizations

```python
from phylogenetic_utils import plot_just_dendrogram
analyzer = plot_just_dendrogram('dataset/NR_sample_5proteins.fasta')
```

## 📝 File Descriptions

| File | Type | Description |
|------|------|-------------|
| `Demo_non_redundant_db.ipynb` | Notebook | Main protein analysis pipeline |
| `Phylogenetic_test.ipynb` | Notebook | Phylogenetic tree construction |
| `phylogenetic_utils.py` | Library | Reusable phylogenetic functions |
| `quick_demo.py` | Script | Standalone analysis script |
| `dataset/` | Folder | Contains FASTA and metadata files |

## ⚠️ Notes

- Ensure `dataset/` folder contains the required FASTA and metadata files
- Some phylogenetic methods may require additional dependencies
- Large datasets may take longer to process

## 🐛 Troubleshooting

- **Import errors**: Check that all packages are installed
- **File not found**: Verify dataset files are in the correct location
- **ETE3/4 issues**: Phylogenetic analysis will fall back to alternative methods

---
*For questions or issues, check the notebook outputs for detailed error messages.*

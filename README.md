# BCB Demo Repository

A bioinformatics computing repository demonstrating parallel processing patterns, MapReduce workflows, and biological data analysis.

## 📁 Repository Structure

```
bcb_demo/
├── notebooks/              # Jupyter notebooks and analysis scripts
│   ├── README.md              # Detailed notebook documentation
│   ├── JupyterLab README.md   # JupyterLab setup guide
│   ├── Demo Non Redundant DB.ipynb
│   ├── Phylogenetic Test.ipynb
│   ├── Quick Demo.py
│   └── Phylogenetic Utils.py
│
├── src/                    # Source code implementations
│   ├── mrp/                   # MapReduce Produce system
│   │   ├── README.md            # MRP documentation
│   │   ├── compile.py           # NL→YAML translator
│   │   ├── run_job.py           # Parallel runtime
│   │   ├── job.yml              # Example specification
│   │   └── outputs/             # Generated results
│   └── ray/                   # Ray distributed computing
│       ├── README.md            # Ray examples
│       ├── hello_world.py
│       └── simple_example.py
│
├── docs/                   # Documentation and specifications
│   ├── mapreduceproduce_prd.md  # MRP product requirements
│   ├── Ray_prd.md              # Ray product requirements  
│   └── ray.md                  # Ray documentation
│
├── dataset/                # Sample biological data
│   ├── NR/                     # Non-redundant database samples
│   ├── Sample 5 Proteins.fasta
│   ├── Sample Proteins.fasta
│   └── Sample 5 Proteins Metadata.txt
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### MapReduce Produce System

```bash
cd src/mrp
python compile.py "run the biological data processing given the data"
python run_job.py job.yml
```

### Jupyter Notebooks

```bash
cd notebooks
jupyter lab
```

### Ray Distributed Computing

```bash
cd src/ray
python hello_world.py
```

## 📊 Key Components

- **MRP System**: Minimal English→YAML→Parallel execution for biological data
- **Ray Examples**: Distributed computing demonstrations
- **Notebooks**: Interactive analysis and visualization
- **Datasets**: Sample biological sequences and metadata

## 🔧 Requirements

- Python 3.7+
- PyYAML 6.0+
- Ray 2.48.0+
- Jupyter Lab (for notebooks)

Install dependencies:

```bash
pip install -r requirements.txt
```

## 📖 Documentation

- [MRP System](src/mrp/README.md) - MapReduce Produce documentation
- [Notebooks](notebooks/README.md) - Jupyter notebook details  
- [Ray Examples](src/ray/README.md) - Distributed computing examples

---

*Demonstrating agentic computing patterns, parallel processing, and biological data analysis workflows.*

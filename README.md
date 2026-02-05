# KAPRA: Strategic (k,P)-Anonymity for Time Series Data

[![Documentation](https://img.shields.io/badge/DOCS-Read%20the%20Documentation-blue?style=for-the-badge&logo=github)](https://federissoo.github.io/KAPRA-TimeSeries-Anonymization/)

This project implements the **KAPRA** algorithm to protect time-series data against unified attacks. It ensures privacy by guaranteeing both value-based ($k$-anonymity) and pattern-based ($P$-anonymity) protection.

## Getting Started

### Prerequisites
- Python $\ge$ 3.10
- [Poetry](https://python-poetry.org/) (for dependency management)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/federissoo/KAPRA-TimeSeries-Anonymization.git
   cd KAPRA-TimeSeries-Anonymization
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

## Usage

To run the anonymization process on the default dataset:

# Run KAPRA Anonymization (Default)
```bash
   poetry run python src/kapra_anonymization.py
```

# Run Naive Anonymization
```bash
   poetry run python src/naive_anonymization.py
```

# Generate Optimization Results & Graphs
```bash
   poetry run python src/generate_plots.py
```


Check the `data/` folder for input/output files and `src/` for the implementation details.
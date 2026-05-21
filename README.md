![Project Logo](assets/banner.png)

![Coverage Status](assets/coverage-badge.svg)

<h1 align="center">
green_chemistry_analysis
</h1>

<br>


This package allows you to calculate the green chemistry factors for multiple reactions and gives you an analysis of the impact of this reaction on environment.

## 🔥 Usage

```python
from mypackage import main_func

# One line to rule them all
result = main_func(data)
```

This usage example shows how to quickly leverage the package's main functionality with just one line of code (or a few lines of code). 
After importing the `main_func` (to be renamed by you), you simply pass in your `data` and get the `result` (this is just an example, your package might have other inputs and outputs). 
Short and sweet, but the real power lies in the detailed documentation.

# 🌿 Green Chemistry Dashboard

An interactive student project for comparing antihistamine synthesis pathways from a green chemistry perspective.

## Project Overview

This project evaluates and compares the environmental sustainability of different antihistamine synthesis routes using quantitative green chemistry indicators and qualitative principle-based assessment.

The analysis includes:

- **E-Factor** — waste generated relative to product mass
- **PMI (Process Mass Intensity)** — overall material consumption
- **Atom Economy** — efficiency of reactant incorporation into the final product
- **Solvent Hazard Assessment** — based on GHS hazard classifications
- **Global Green Score** — comparative sustainability score
- **Green Chemistry Principle Evaluation** — qualitative compliance assessment

The application provides an interactive dashboard for visual comparison of synthesis pathways.

---

## Features

- Interactive Streamlit dashboard
- Comparison of multiple antihistamine synthesis routes
- Sustainability metric computation
- Global comparative Green Score
- Simplified chemical reaction visualization
- Green chemistry principle evaluation
- Molecular visualization using PubChem data

---

## Project Structure

```text
.
├── app.py                  # Main Streamlit application
├── data/
│   ├── reactions.json      # Reaction dataset
│   ├── molecules.json      # Molecular property dataset
│   ├── reactions.py        # Reaction data loading module
│   └── molecules.py        # Molecular data loading module
│
├── utils/
│   ├── metrics.py          # Sustainability metric calculations
│   └── scoring.py          # Green score computation
│
├── notebooks/              # Jupyter notebooks and project report
└── README.md




![Project Logo](assets/banner.png)

---

<h1 align="center"> Green Chemistry Analyse Tool</h1>

---

## Table of content

- [About](#about)
- [Original Outputs](#original-outputs)
- [Usage](#usage)
- [Installation](#installation)
  - [Structure](#project-structure)
- [Context and Authors](#context-and-authors)

## About

This project consists of the development of an interactive and visual tool designed to familiarize the audience with green chemistry and raise awareness of the need to make chemical synthesis more sustainable in terms of environmental impact, safety, yield, and resource efficiency.

It calculates key indicators such as atom economy, E-factor, and the number of hazardous solvents for a range of antihistamine synthesis pathways.

## Original Outputs

These indicators were developed specifically for this project 
and are not established industry standards:

- **Green Score:** a proposed composite metric combining traditional 
  indicators with other quantitative characteristics of each pathway.
- **12 Principles Assessment:** a custom evaluation of each pathway's 
  compliance with the 12 principles of green chemistry.

## Usage

The application provides an intuitive comparison workflow. Upon launching, 
the user is presented with available symptom categories corresponding to 
different antihistamine use cases. After selecting a category, the relevant 
compounds become available for comparison.

Once one or more synthesis pathways are selected, the dashboard dynamically 
displays:
- The overall Green Score
- Quantitative sustainability indicators 
- A simplified visual representation of the synthesis pathway
- A qualitative evaluation of the 12 Green Chemistry Principles
- A Ranking of the antihistamine synthesis based on the greenscore

The interface was designed to provide immediate visual feedback and remain 
accessible to users without familiarity with the underlying code.

##  Installation

Create and activate a new conda environment:
```bash
conda create -n green_chemistry_analysis python=3.10
conda activate green_chemistry_analysis
```
Install the package:
```bash
pip install .
```
Optionally, install JupyterLab to explore the notebooks:
```bash
pip install jupyterlab
```
### Project Structure

After installation, here is an overview of the repository structure:

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

```

### Ready? Let's make chemistry greener! 

You can now execute the following commands to run the app! 🚀
```bash
streamlit run app.py
```

## Context and Authors

This project was developed in an educational context as part of a Bachelor’s program at EPFL.

**Authors:**
 
- Anna Griffa  
- Elsa Chevalier 
- Antoine Tran  
- Thomas Clément  

**Aknowledgment:**

This project was developed under the supervision of the academic team for the course “Practical Programming in Chemistry”.
AI-assisted tools were used during the development process.
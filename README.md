# GES-xml-converter
![Tests](https://github.com/GES-compchem/GES-xml-converter/actions/workflows/tests.yml/badge.svg)

This repo contains a simple python parser for XML files. An example script (`invoices.py`), capable of converting Italian electronic invoices to a `.xlsx` formatted table, is provided together with a simple streamlit-based GUI (`invoices_gui.py`).

## Requirements

The following packages are required to run the parser:

* python (3.8.13)
* pandas (1.4.3)
* lxml (4.9.0)
* cryptography (37.0.2)
* pyOpenSSL (22.0.0)
* openpyxl (3.0.10)
* streamlit (1.10.0)

The indicated version represents the package release used during development, other versions may work as well.

It is advisable to run the parser using the anaconda virtual environment. A conda environment (named `GES-XML`) containing all the requirements pre-installed can be created using the command:
```
conda env create .
```
The `xml_parser` package can be installed locally in development mode using the command:
```
pip install -e .
```

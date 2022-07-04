# GES-xml-converter

This repo contains a simple python parser for XML files. An example script (`invoices.py`), capable of converting Italian electronic invoices to a `.xlsx` formatted table is provided.

## Requirements

The following packages are required to run the parser:

* python (3.8.13)
* pandas (1.4.3)
* lxml (4.9.0)
* cryptography (37.0.2)
* pyOpenSSL (22.0.0)
* openpyxl (3.0.10)

The indicated version represents the package release used during development, other versions may work as well.

It is advisable to run the parser using the anaconda virtual environment. A conda environment (named `GES-XML`) containing all the requirements pre-installed can be created using the command:
```
conda env create .
```

CALCULADORA COSTES
==================

A modular **Python 3.10+** package that cleans, validates and analyses manufacturing
data to obtain **accurate product‑level cost margins**.  
The project is organised as a *reusable* library (`calculadora_margen`) plus a
companion demonstration notebook (`notebooks/test.ipynb`) that orchestrates the
full ETL pipeline from raw CSVs to insightful visualisations.

-------------------------------------------------------------------------------
TABLE OF CONTENTS
-------------------------------------------------------------------------------
1.  Key Features  
2.  Quick Start  
3.  Minimal Example  
4.  Project Structure  
5.  Module Overview  
6.  Configuration  
7.  Development & Tests  
8.  Autoría  
9.  Contributing  
10. License & Acknowledgements  
11. UML Diagrams  
12. Changelog  

-------------------------------------------------------------------------------
1  KEY FEATURES
-------------------------------------------------------------------------------
✓ **DataFrameCleaner** – chainable façade to drop/rename columns, remove NA/
  duplicate rows, normalise numeric & date formats, and enforce uppercase text.  
✓ **Validator** – regex‑based row filtering with automatic reporting of
  discarded records.  
✓ **OutliersManager** – iterative, z‑score driven detection & replacement of
  outliers by group mean.  
✓ **Encoder** – utility to build composite keys for safe merges.  
✓ **CostCalculator** – recursive algorithm that propagates costs from raw
  components to semi‑finished goods and final products.  
✓ **VisualizationManager** – pastel‑style Matplotlib charts for single and
  multi‑article cost trends.  
✓ **Fully parameterised** via `config/parameters.py`, making it trivial to plug
  new datasets or tweak thresholds.  
✓ Clean separation between **data**, **docs**, **src** and **notebooks** for
  reproducibility.

-------------------------------------------------------------------------------
2  QUICK START
-------------------------------------------------------------------------------
```bash
# Clone & enter the repo
git clone https://github.com/your‑org/calculadora_margen.git
cd calculadora_margen

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt
# (For development extras use requirements_dev.txt)

# Launch the demo notebook
jupyter lab notebooks/test.ipynb
```

The notebook walks through:

* cleaning **costes.csv**, **master_lotes.csv** and **fabricaciones_2025.csv**  
* merging them with composite keys  
* recursive cost calculation  
* outlier treatment  
* interactive visualisations

-------------------------------------------------------------------------------
3  MINIMAL EXAMPLE
-------------------------------------------------------------------------------
A quick taste of the API in bare Python (no Jupyter needed):

```python
import pandas as pd
from calculadora_margen.cleaning.cleaner_df import DataFrameCleaner
from calculadora_margen.config.parameters import Parameters
from calculadora_margen.services.cost_calculator import CostCalculator

#  Load raw purchases
df_costes = pd.read_csv("data/raw/costes.csv", sep=";", dtype=str)

# Clean & coerce types
cleaner = DataFrameCleaner(df_costes)
costes = (cleaner
          .columns_cleaner.keep_and_rename(
              Parameters.costes.cols_to_keep,
              Parameters.costes.rename_map)
          .data_cleaner.fix_numeric_format(
              Parameters.costes.cols_to_float)
          .get_df())

# Compute manufacturing costs (recursive)
calc = CostCalculator(costes)
result = calc.calculate_costs_recursively()
print(result.head())
```

-------------------------------------------------------------------------------
4  PROJECT STRUCTURE
-------------------------------------------------------------------------------
```
calculadora_margen/
├── data/
│   ├── raw/        ← original CSV exports from the ERP
│   └── clean/      ← cleaned artefacts written by the notebook
├── docs/           ← UML diagrams & architecture artefacts
├── notebooks/
│   └── test.ipynb  ← end‑to‑end demo
├── src/
│   └── calculadora_margen/
│       ├── cleaning/
│       │   └── cleaner_df.py
│       ├── config/
│       │   └── parameters.py
│       └── services/
│           ├── cost_calculator.py
│           ├── encoder.py
│           ├── outliers_manager.py
│           ├── validator.py
│           └── visualizations_manager.py
├── .gitignore
├── CHANGELOG.md
├── LICENSE.txt
├── README.txt      ← (this file)
├── LICENSE.txt
├── setup.cfg
├── setup.py
├── VERSION.txt
├── requirements_dev.txt
└── requirements.txt
```

-------------------------------------------------------------------------------
5  MODULE OVERVIEW
-------------------------------------------------------------------------------
| Module | Purpose | Highlight |
|--------|---------|-----------|
| **cleaning/cleaner_df.py** | Chainable façade around `pandas` ops | `.columns_cleaner`, `.rows_cleaner`, `.data_cleaner` sub‑APIs |
| **services/validator.py** | Regex validation & logging of invalid rows | `.get_invalid()` for inspection |
| **services/outliers_manager.py** | Replace extreme values iteratively | Configurable `z_score`, `min_threshold`, `max_iterations` |
| **services/cost_calculator.py** | Recursive roll‑up of component costs | Handles semi‑finished goods (`SEM*`) gracefully |
| **services/encoder.py** | Build composite merge keys | Avoids accidental duplicates |
| **services/visualizations_manager.py** | Matplotlib visual aides | Custom exception `VisualizationError` |

-------------------------------------------------------------------------------
6  CONFIGURATION
-------------------------------------------------------------------------------
All dataset‑specific rules live in `config/parameters.py`:

* **DatasetParams** dataclass – one instance per CSV  
* Cleaning rules: columns to keep/rename, numeric & date coercion  
* Validation regex patterns  
* Outlier rules per numerical column  
* Visualisation labels & titles  

Changing behaviour = editing a *single central file*.

-------------------------------------------------------------------------------
7  DEVELOPMENT & TESTS
-------------------------------------------------------------------------------
*Follow PEP‑8* and ensure **pre‑commit** hooks pass (`ruff`, `black`, `isort`).  
Run type checks with **mypy**.  
Unit tests will live under `tests/` (currently empty—feel free to contribute!).

-------------------------------------------------------------------------------
8  AUTORÍA
-------------------------------------------------------------------------------
Laura Vela Pascual
laura.vela.pas@gmail.com
27/04/2025

-------------------------------------------------------------------------------
9  CONTRIBUTING
-------------------------------------------------------------------------------
1. Fork → feature branch → PR against `main`.  
2. Update `CHANGELOG.md` under *Unreleased* with your additions.  
3. Ensure CI passes and code is well commented.

-------------------------------------------------------------------------------
10  LICENSE & ACKNOWLEDGEMENTS
-------------------------------------------------------------------------------
Distributed under the terms of the license found in **LICENSE.txt**  
Built with ♥ by the *Data & Analytics* team using **pandas**, **numpy** &
**matplotlib**.

-------------------------------------------------------------------------------
11  UML DIAGRAMS
-------------------------------------------------------------------------------
Detailed class relationships are documented in the UML diagram located at
`docs/UML_CalculadoraCostes.pdf`.

-------------------------------------------------------------------------------
12  CHANGELOG
-------------------------------------------------------------------------------
See **CHANGELOG.md** for a human‑readable history
(Adheres to *Keep a Changelog 1.0* and *Semantic Versioning 2.0*).

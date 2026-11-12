# Functional protein annotations

Example notebooks that annotate bacterial proteins (RefSeq `WP_` IDs) with functional categories from
The Seed (BV-BRC subsystems), TIGRFAM, KEGG, COG and GO.

## Installation

Requires [uv](https://docs.astral.sh/uv/). Python 3.13 is installed automatically by uv if missing.

```bash
git clone <repo-url>
cd functional_protein_annotations
uv sync                 # creates .venv with all dependencies (incl. ipykernel)
mkdir -p data           # output folder, ignored by git
```

Open the notebooks in VS Code / Jupyter and select the `.venv` kernel, or run:

```bash
uv run --with jupyter jupyter lab
```

## Run order

Notebooks write intermediate files to `data/` that later notebooks read, so run them in this order:

1. `01_the_seed.ipynb` – finds the genome, builds the BV-BRC ↔ `WP_` ID mapping (`data/example_features_wp.tsv`), adds The Seed subsystems
2. `02_a_download_NCBI.ipynb` – downloads TIGRFAM, COG and GO hits from NCBI for a list of `WP_` IDs
3. `02_tigrfam.ipynb`, `03_KEGG.ipynb`, `04_COG.ipynb`, `05_GO.ipynb` – add the respective annotations (any order)

## Variables to set

| Notebook | Variable / line | Example value | Meaning |
|---|---|---|---|
| `01_the_seed` | `terms` | `["Staphylococcus", "aureus", "Newman"]` | Words that must all appear in the BV-BRC genome name |
| `01_the_seed` | `genome_id` | `"426430.67"` | BV-BRC genome to use. Pick one from the printed `refseq_counts` table with many RefSeq features (`n_refseq_features`) |
| `02_a_download_NCBI` | `Entrez.email` | `"name@institute.de"` | Your e-mail address, required by NCBI E-utilities |
| `02_a_download_NCBI` | input ID file | `"../data/example_wp_ids.txt"` | Text file with one `WP_` ID per line (see below) |
| `03_KEGG` | `genome_id` | `"426430.67"` | Must be the same genome as in `01_the_seed` |
| all except `02_a` | input data file | `"../../Example_Staphylococcus_aureus_Newman_TaxId_426430.xlsx"`, sheet `"Tabelle1"` | Your own protein list (Excel) to annotate |
| all except `02_a` | ID column | `"Majority protein IDs"` | Column in the input data containing the protein IDs |
| all | output file names | `../data/example_*.tsv/.xlsx` | Change the `example_` prefix if you do not want to overwrite previous runs |

### Input data requirements

- The input Excel file needs a column with RefSeq protein IDs (`WP_…`). In the example this is
  `Majority protein IDs`; the first `WP_` ID in each cell is extracted with
  `str.extract(r"(WP_[\d.]+)")` into a new `wp_id` column, which is used to join all annotations.
  If your column has a different name, change it in every notebook that reads the input file.
- `02_a_download_NCBI` needs the `WP_` IDs as a plain text file (one ID per line). No notebook creates it
  automatically; e.g. export it from the `wp_id` column of your input data:

  ```python
  import pandas as pd

  # read the input data and extract the first WP_ ID per row
  test_data = pd.ExcelFile("../../Example_Staphylococcus_aureus_Newman_TaxId_426430.xlsx").parse("Tabelle1")
  test_data = test_data.assign(wp_id=test_data["Majority protein IDs"].str.extract(r"(WP_[\d.]+)", expand=False))

  # write the unique IDs, one per line
  test_data["wp_id"].dropna().drop_duplicates().to_csv("../data/example_wp_ids.txt", index=False, header=False)
  ```

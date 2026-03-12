# Harmonization - Electrolyzer Patent Analysis

Patent applicant name harmonisation and sector analysis for the electrolyzer technology domain, using PATSTAT on EPO's TIP platform.

## Notebooks

| Notebook | Description |
|----------|-------------|
| **12_Patent_Analysis.ipynb** | General electrolyzer patent landscape analysis with sector classification, interactive search HTML and Plotly visualisations |
| **13_Siemens_Deep_Dive.ipynb** | Siemens-focused deep dive with Eurostat/ECOOM name harmonisation methodology |

## Data

| File | Description |
|------|-------------|
| `03_Dataset_Enhancement__Elettrolizzatori_Enhanced_Final_Dataset_2025!!!.xlsx` | Source dataset with electrolyzer patent family IDs (docdb_family_id). Required input for both notebooks. |

## How to Use

### Prerequisites

- EPO TIP JupyterLab environment with PATSTAT PROD access
- Python packages: `pandas`, `numpy`, `plotly`, `openpyxl`, `sqlalchemy` (pre-installed on TIP)
- The `epo.tipdata.patstat` module (TIP-specific)

### Running the Notebooks

1. Open a notebook in TIP's JupyterLab
2. Run all cells sequentially ("Run All" or Shift+Enter through each cell)
3. Cells 1-6 load data from PATSTAT (takes a few minutes due to batch queries)
4. Output files are generated in the same directory

### Viewing HTML Reports

The notebooks generate interactive HTML reports with Plotly charts. These require JavaScript, which JupyterLab's built-in HTML viewer blocks.

**To view:** Right-click the HTML file in the file browser and select **"Open in New Browser Tab"**.

## 12_Patent_Analysis.ipynb

Analyses all electrolyzer patent applicants across the full dataset.

**Pipeline:**
1. Load electrolyzer patent family IDs from the Excel dataset
2. Query PATSTAT (TLS201, TLS206, TLS207) for applicant names, sectors, filing years
3. Classify applicants into sectors (Company, University, Research Institution, etc.) using PATSTAT's `psn_sector` with name-based fallback
4. Generate aggregated summary, interactive HTML with search, Plotly visualisations
5. Export to CSV, Excel, HTML

**Output files:**
- `electrolyzer_interactive_analysis.html` - Searchable applicant dashboard
- `Electrolyzer_Patent_Analysis_Enhanced_Report.html` - Static report with charts
- `Electrolyzer_Patent_Analysis_Enhanced_Data.csv`
- `Electrolyzer_Patent_Analysis_Enhanced_Complete.xlsx`

## 13_Siemens_Deep_Dive.ipynb

Focused analysis of all Siemens entities, applying the Eurostat/ECOOM name harmonisation methodology (as described in KS-RA-11-008-EN) to consolidate 17+ name variations into corporate groups.

**Name Harmonisation Pipeline (Eurostat methodology):**
1. Character Cleaning (HTML entities, unicode to ASCII)
2. Punctuation Cleaning (normalise separators)
3. Legal Form Removal (AG, GmbH, Co. KG, Inc., Ltd., etc.)
4. Common Company Word Removal (Company, International, Global, etc.)
5. Spelling Variation Harmonisation (Systems/Systeme, Technologies/Technologien)
6. Condensing (remove non-alphanumeric characters)
7. Umlaut Harmonisation (ae/oe/ue variants)
8. Corporate Group Assignment (Siemens AG, Siemens Energy, Siemens Gamesa, Joint Ventures)

**Additional analyses:**
- IPC/CPC technology profile
- Geographic filing strategy (publication offices)
- Timeline by corporate group
- Competitive context (ranking, market share)

**Output files:**
- `Siemens_Electrolyzer_Deep_Dive.html` - Comprehensive report with Sankey diagram, harmonisation table, charts
- `Siemens_Electrolyzer_Patent_Data.csv`
- `Siemens_Electrolyzer_Analysis.xlsx` (sheets: Name_Harmonisation, Corporate_Groups, IPC_Profile, Filing_Offices, Raw_Data)

## Reference

The name harmonisation methodology follows:
> Callaert, J. et al. (2011). *Patent Statistics at Eurostat: Methods for Regionalisation, Sector Allocation and Name Harmonisation.* Eurostat Methodologies & Working Papers, KS-RA-11-008-EN.

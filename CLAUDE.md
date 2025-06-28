# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack

TSUMUGI is a bioinformatics web application that analyzes mouse phenotype data from the International Mouse Phenotyping Consortium (IMPC). The project consists of:

- **Frontend**: Pure JavaScript/HTML/CSS web application with no build system
- **Data Processing**: Python-based Jupyter notebooks using pandas, polars, and scientific libraries
- **Visualization**: Cytoscape.js for network visualization
- **Deployment**: Static site deployment to GitHub Pages

## Project Architecture

### Core Components

1. **TSUMUGI/**: The main web application directory
   - `index.html`: Main landing page
   - `js/`: Core JavaScript functionality
   - `css/`: Styling
   - `app/`: Generated pages for genes and phenotypes
   - `data/`: JSON data files for the web app

2. **notebooks/**: Data processing and deployment workflows
   - `notebooks-experiments/`: Research and analysis notebooks
   - `notebools-web/`: Deployment notebooks that generate the web application

3. **data/**: Raw and processed datasets
   - IMPC phenotyping data
   - Gene-phenotype associations
   - Network similarity calculations

### Data Flow

The application follows this data pipeline:
1. Raw IMPC data is processed in `notebooks-experiments/`
2. Deployment notebooks in `notebools-web/` generate the static web files
3. Templates in `TSUMUGI/template/` are used to create individual gene/phenotype pages
4. Final output is deployed to GitHub Pages

## Development Environment

### Setup Commands

```bash
# Create conda environment
conda create -y -n env-tsumugi python=3.12
conda install -y -n env-tsumugi -c conda-forge \
    numpy pandas polars pyarrow matplotlib seaborn plotnine scikit-learn statsmodels \
    ipykernel ipywidgets nbstripout \
    tqdm networkx dash dash_cytoscape nodejs yarn prettier

# Activate environment
conda activate env-tsumugi
```

### Development Workflow

1. **Data Analysis**: Work in `notebooks/notebooks-experiments/` for research
2. **Web Development**: Modify templates in `TSUMUGI/template/` and core JS in `TSUMUGI/js/`
3. **Deployment**: Run deployment notebook `notebooks/notebools-web/955_deploy_for_main.ipynb`
4. **Formatting**: Code is automatically formatted with prettier

### Key Deployment Commands

The main deployment process is handled by the notebook `notebooks/notebools-web/955_deploy_for_main.ipynb`, which:
- Generates thousands of HTML/JS files from templates
- Copies data files to the web directory
- Formats code with prettier
- Creates the complete static site

## Important Files and Patterns

### Template System
- `TSUMUGI/template/template_index.html`: Main page template
- `TSUMUGI/template/template-app-html/`: HTML templates for gene/phenotype pages
- `TSUMUGI/template/template-app-js/`: JavaScript templates for different page types

### Data Processing
- Phenotype similarity calculated using Jaccard index
- Binary vs. continuous phenotypes handled differently
- Gene-gene networks based on shared phenotypes

### Web Application Features
- Three input modes: phenotype search, gene search, gene list analysis
- Interactive network visualization with Cytoscape.js
- Filtering by similarity, severity, genotype, sex, and life stage
- Mobile-responsive design

## Code Style and Conventions

- JavaScript uses no build system - pure ES modules
- Jupyter notebooks use nbstripout to exclude outputs from Git
- Prettier formatting applied to all web files
- Template placeholders use `XXX_` prefix (e.g., `XXX_TITLE`, `XXX_NAME`)
- 型ヒントは組み込み型を使用し、typingモジュールは使用しないこと。
- クラスは使わず、関数で実装すること。


## Testing and Quality Assurance

The deployment notebook includes validation steps to ensure:
- All `XXX_` placeholders are replaced in generated files
- Required data files are present
- File counts match expected values

## Data Sources

- IMPC Release 22.1/23.0 statistical results
- Mouse Genome Informatics (MGI) gene annotations
- Mammalian Phenotype Ontology (MPO) terms

> ⚠️ Esta es una traducción generada por IA; si tienes dudas, consulta el original (README.md).  
> Original: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="https://raw.githubusercontent.com/akikuno/TSUMUGI-dev/refs/heads/main/image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![Test](https://img.shields.io/github/actions/workflow/status/akikuno/tsumugi-dev/pytest.yml?branch=main&label=Test&color=brightgreen)](https://github.com/akikuno/tsumugi-dev/actions)
[![PyPI](https://img.shields.io/pypi/v/tsumugi.svg?label=PyPI&color=orange)](https://pypi.org/project/tsumugi/)
[![Bioconda](https://img.shields.io/conda/v/bioconda/tsumugi?label=Bioconda&color=orange)](https://anaconda.org/bioconda/tsumugi)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** es una herramienta web que usa datos de fenotipo de ratones KO del [IMPC](https://www.mousephenotype.org/) para **extraer y visualizar módulos génicos basados en similitud fenotípica**.  
Está disponible para cualquiera en la web👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI (紡ぎ)** procede de “tejer los grupos génicos que forman los fenotipos”.

# 📖 Cómo usar TSUMUGI

TSUMUGI admite tres tipos de entrada.

### 1. Fenotipo (Phenotype)
Introduce un fenotipo de interés para buscar **genes cuyos ratones KO tengan perfiles fenotípicos similares**.  
Los nombres de fenotipo siguen el [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Lista de fenotipos](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. Gen (Gene)
Especifica un gen para buscar **otros genes con fenotipos KO semejantes**.  
Símbolos según [MGI](http://www.informatics.jax.org/).  
👉 [Lista de genes](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. Lista de genes (Gene List)
Varios genes (uno por línea) para buscar **dentro de la lista**.  
> [!CAUTION]  
> Si no se encuentra ninguno: `No similar phenotypes were found among the entered genes.`  
> Si hay más de 200: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Descarga de datos brutos
TSUMUGI publica ficheros JSONL comprimidos con gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Símbolo génico (p. ej., "1110059G10Rik")  
- Marker accession ID (p. ej., "MGI:1913452")  
- Nombre/ID de fenotipo (p. ej., "fused joints", "MP:0000137")  
- Effect size (p. ej., 0.0, 1.324)  
- Significancia (True/false)  
- Cigocidad ("Homo", "Hetero", "Hemi")  
- Etapa vital ("Embryo", "Early", "Interval", "Late")  
- Dimorfismo sexual ("", "Male", "Female")  
- Anotación de enfermedad ([], "Premature Ovarian Failure 18", etc.)

Ejemplo:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Par génico (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (etapa vital, cigocidad, dimorfismo sexual) para fenotipos compartidos  
- `phenotype_similarity_score`: puntuación Resnik→Phenodigm (0–100)

Ejemplo:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Red

La red se dibuja automáticamente según la entrada.

> [!IMPORTANT]  
> Se visualizan pares con **≥3 fenotipos anómalos compartidos** y **similitud > 0.0**.

### Panel de red
**Nodos**: genes. Clic para ver fenotipos anómalos; arrastra para reubicar.  
**Aristas**: clic para ver fenotipos compartidos.

### Panel de control
Ajusta la visualización desde el panel izquierdo.

#### Filtro por similitud fenotípica
`Phenotypes similarity` ajusta el umbral de aristas según Resnik→Phenodigm.  
> Detalles: 👉 [🔍 Cómo calculamos los genes con fenotipos similares](#-cómo-calculamos-los-genes-con-fenotipos-similares)

#### Filtro por severidad fenotípica
`Phenotype severity` filtra nodos por effect size en KO; valores mayores indican más impacto.  
> Oculto para fenotipos binarios (p. ej., [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); lista binaria [aquí](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) o entrada de un solo gen.

#### Especificar genotipo
- `Homo` (homocigoto)
- `Hetero` (heterocigoto)
- `Hemi` (hemicigoto)

#### Especificar sexo
- `Female`
- `Male`

#### Especificar etapa vital
- `Embryo`
- `Early` (0–16 semanas)
- `Interval` (17–48 semanas)
- `Late` (49+ semanas)

### Panel de marcado
#### Highlight: Human Disease
Resalta genes ligados a enfermedad humana (IMPC Disease Models Portal).

#### Search: Specific Gene
Busca nombres de genes en la red.

#### Layout & Display
Ajusta layout, tamaño de fuente, grosor de aristas, repulsión de nodos (Cose).

#### Export
Exporta PNG/CSV/GraphML. CSV incluye IDs de módulo y listas de fenotipos; GraphML es compatible con Cytoscape.

# 🛠 Edición por línea de comandos

Esta versión añade CLI para actualizar con datos IMPC, aplicar filtros finos y exportar GraphML o webapp offline.

- Recalcula con `statistical-results-ALL.csv.gz` (opcional `mp.obo`, `impc_phenodigm.csv`)  
- Filtra por presencia/ausencia de término MP  
- Filtra por lista de genes (CSV o archivo de texto)  
- Salidas: GraphML (`tsumugi build-graphml`), webapp offline (`tsumugi build-webapp`)

## Comandos disponibles
- `tsumugi run`: recalcula desde datos IMPC  
- `tsumugi mp --include/--exclude`: pares que muestran/no muestran término MP  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: por número de fenotipos (par/gen)  
- `tsumugi genes --keep/--drop`: mantener/eliminar por lista de genes  
- `tsumugi life-stage --keep/--drop`: filtrar por etapa  
- `tsumugi sex --keep/--drop`: filtrar por sexo  
- `tsumugi zygosity --keep/--drop`: filtrar por cigocidad  
- `tsumugi build-graphml`: generar GraphML  
- `tsumugi build-webapp`: generar assets de webapp TSUMUGI

## Instalación
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
Listo cuando `tsumugi --version` muestre la versión.

## Uso habitual (por comando)

### 1. Recalcular con datos IMPC (`tsumugi run`)
Si se omite `--mp_obo`, se usa el incluido `data-version: releases/2025-08-27/mp.obo`.  
Si se omite `--impc_phenodigm`, se usa el archivo obtenido el 2025-10-01 del [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Salidas en `./tsumugi-output`: genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz y assets de visualización (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` incluye scripts según SO; doble clic para abrir la app local:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. Filtrar por término MP (`tsumugi mp --include/--exclude`)
Extrae solo pares de genes que contengan los fenotipos de interés o pares en los que esos fenotipos se midieron pero no mostraron anomalías significativas.

```bash
# Extraer solo los pares que incluyan MP:0001146 (abnormal testis morphology) o términos descendientes (p. ej., MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extraer pares en los que se midieron MP:0001146 y términos descendientes y no se observó una anomalía significativa
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl
```

> [!IMPORTANT]
> **También se manejan los términos MP descendientes del ID especificado.**  
> Por ejemplo, si indicas `MP:0001146 (abnormal testis morphology)`, también se consideran términos descendientes como `MP:0004849 (abnormal testis size)`.

### 3. Filtrar por número de fenotipos (`tsumugi n-phenos`)
- Fenotipos compartidos por par:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Fenotipos por gen (requiere genewise):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```

### 4. Lista de genes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. Etapa vital / sexo / cigocidad
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### 6. Exportar GraphML / webapp
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --output_dir ./webapp_output
```
Ejemplo de pipeline: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cómo calculamos los genes con fenotipos similares

## Fuente de datos
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Campos: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Preprocesamiento
Extraer pares gen–fenotipo con P (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`) ≤ 0.0001.  
- Cigocidad: `homo`, `hetero`, `hemi`  
- Sexo: `female`, `male`

## Similitud fenotípica
Calculamos **Resnik** entre términos MP y escalamos a **Phenodigm (0–100)**.

1. Construir ontología MP y calcular IC:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC del ancestro común más informativo (MICA); si no hay, 0.  
3. Para cada par de genes: matriz de Resnik entre términos significativos, ponderada por coincidencia de metadatos (cigocidad/etapa/sexo: 1.0/0.75/0.5/0.25); tomar máximos/medias reales.  
4. Obtener máximos/medias teóricas de los IC y normalizar:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   Si el denominador teórico es 0, poner 0. El rango 0–100 se usa en descargas y en el control `Phenotypes similarity`.

# ✉️ Contacto
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

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

### Fenotipo (Phenotype)
Introduce un fenotipo de interés para buscar **genes cuyos ratones KO tengan perfiles fenotípicos similares**.  
Los nombres de fenotipo siguen el [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Lista de fenotipos](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gen (Gene)
Especifica un gen para buscar **otros genes con fenotipos KO semejantes**.  
Símbolos según [MGI](http://www.informatics.jax.org/).  
👉 [Lista de genes](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Lista de genes (Gene List)
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
**Módulos** delinean subredes génicas. Clic para listar fenotipos de los genes del módulo; arrastra para moverlos y evitar solaparse.

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
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: pares o genes que muestran/no muestran un término MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: por número de fenotipos (par/gen)  
- `tsumugi score (--min/--max)`: filtrar por puntuación de similitud (pares de genes)
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

### Recalcular con datos IMPC (`tsumugi run`)
Si se omite `--mp_obo`, se usa el incluido `data-version: releases/2025-08-27/mp.obo`.  
Si se omite `--impc_phenodigm`, se usa el archivo obtenido el 2025-10-01 del [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Salidas en `./tsumugi-output`: genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz y assets de visualización (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` incluye scripts según SO; doble clic para abrir la app local:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filtrar por término MP (`tsumugi mp --include/--exclude`)
Extrae solo pares de genes que contengan los fenotipos de interés o pares en los que esos fenotipos se midieron pero no mostraron anomalías significativas.

- `--pairwise` (predeterminado si no se establece): salida por pares de genes. Usa `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: salida por genes individuales. Usa `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (obligatorio con `--exclude`, recomendado con `--include`).

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

# Extraer anotaciones significativas a nivel de gen que contengan MP:0001146 (descendientes incluidos)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Extraer genes medidos para MP:0001146 (descendientes incluidos) sin anomalía significativa
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **También se manejan los términos MP descendientes del ID especificado.**  
> Por ejemplo, si indicas `MP:0001146 (abnormal testis morphology)`, también se consideran términos descendientes como `MP:0004849 (abnormal testis size)`.

### Filtrar por número de fenotipos (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- Fenotipos compartidos por par:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Fenotipos por gen (requiere genewise):
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```


### Filtrar por puntuación de similitud (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Filtra pares de genes por `phenotype_similarity_score` (0–100). Se requiere al menos `--min` o `--max`.

#### `--min MIN`, `--max MAX`
Límites inferior/superior del score. Puedes usar solo uno para filtrar en un sentido.

#### `--in IN`
Ruta al archivo de anotaciones por pares (JSONL/.gz); si se omite, lee de STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` o `--max` por sí solo funciona.

### Lista de genes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Etapa vital / sexo / cigocidad
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### Exportar GraphML / webapp
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
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
TSUMUGI sigue un enfoque similar a Phenodigm. Calculamos la similitud de **Resnik** entre términos MP y la similitud de **Jaccard** entre conjuntos de ancestros, y las combinamos mediante la **media geométrica**. La diferencia clave con Phenodigm original es la ponderación por metadatos (cigocidad, etapa de vida, dimorfismo sexual) al agregar similitudes.

1. Construir la ontología MP y calcular IC:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   Los términos por debajo del percentil 5 de IC se ponen a 0.
2. Para cada par de términos MP, encontrar el ancestro común más específico (MICA) y usar su IC como Resnik.  
   Calcular el índice de Jaccard sobre los conjuntos de ancestros.  
   Similitud de términos = `sqrt(Resnik * Jaccard)`.
3. Para cada par de genes, construir una matriz término×término y aplicar ponderación por metadatos.  
   Coincidencias de cigocidad/etapa de vida/dimorfismo sexual aportan pesos 0.25/0.5/0.75/1.0 para 0/1/2/3 coincidencias.
4. Escalado tipo Phenodigm a 0–100:  
   Usar máximos de filas/columnas para obtener el máximo y la media reales.  
   Normalizar por máximo/media teóricos basados en IC y calcular  
   `Score = 100 * (normalized_max + normalized_mean) / 2`.  
   Si un denominador teórico es 0, ese término se fija en 0.

# ✉️ Contacto
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

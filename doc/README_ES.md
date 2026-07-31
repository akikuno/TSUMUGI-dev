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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** es una herramienta web que usa datos de fenotipo de ratones KO del [IMPC](https://www.mousephenotype.org/) para **extraer y visualizar módulos génicos basados en similitud fenotípica**.  
Está disponible para cualquiera en la web👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Esta documentación describe el funcionamiento actual de **TSUMUGI v1.1.0**. La aplicación web pública utiliza datos de IMPC **Release 24.0**.

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
> Si la red generada contiene 200 genes o más: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Descarga de datos brutos
TSUMUGI publica ficheros JSONL comprimidos con gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Símbolo génico (p. ej., "1110059G10Rik")  
- Marker accession ID (p. ej., "MGI:1913452")  
- Nombre/ID de fenotipo (p. ej., "fused joints", "MP:0000137")  
- Effect size (`number` o `null`; p. ej., 0.0, 1.324)
- Significancia (True/false)  
- Cigocidad ("Homo", "Hetero", "Hemi")  
- Etapa vital ("Embryo", "Early", "Interval", "Late")  
- Dimorfismo sexual ("", "Male", "Female")  
- Anotación de enfermedad ([], "Premature Ovarian Failure 18", etc.)

Ejemplo:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Par génico (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (etapa vital, cigocidad, dimorfismo sexual) para fenotipos compartidos  
- `phenotype_similarity_score`: puntuación Resnik→Phenodigm (0–100)

Ejemplo:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Red

La red se dibuja automáticamente según la entrada.

> [!IMPORTANT]  
> Se visualizan pares con **≥3 fenotipos anómalos compartidos** y **similitud > 0.0**.

### Panel de red
**Nodos**: genes. Clic para ver fenotipos anómalos; arrastra para reubicar.  
**Aristas**: clic para ver fenotipos compartidos.  
**Módulos** delinean subredes génicas. Clic para listar fenotipos de los genes del módulo; arrastra para moverlos y evitar solaparse.
Las páginas de genes usan módulos Top-level MP soft/fuzzy, por lo que un gen puede pertenecer a varios módulos. Las páginas de fenotipo y Gene List pueden alternar entre módulos `Similarity` basados en componentes conectados y módulos `Top-level MP`.

### Panel de control
Ajusta la visualización desde el panel izquierdo.

#### Filtro por similitud fenotípica
`Phenotypes similarity` ajusta el umbral de aristas según Resnik→Phenodigm.  
> Detalles: 👉 [🔍 Cómo calculamos los genes con fenotipos similares](#-cómo-calculamos-los-genes-con-fenotipos-similares)

#### Filtro por effect size
`Effect size` filtra nodos por la magnitud del effect size derivado de IMPC cuando está disponible.
Los effect sizes ausentes se serializan en JSONL como `null` de JSON estándar, se mantienen semánticamente ausentes en vez de convertirse en cero y sus nodos se muestran en blanco.
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
#### Visualización de módulos
En el panel derecho se pueden elegir la definición y el módulo visible. Los bordes de los módulos pueden ocultarse sin eliminar genes ni aristas de la red.

#### Highlight: Human Disease
Resalta genes ligados a enfermedad humana (IMPC Disease Models Portal).

#### Search: Specific Gene
Busca nombres de genes en la red.

#### Layout & Display
Ajusta layout, tamaño de fuente, grosor de aristas, repulsión de nodos (Cose).

#### Export
Exporta PNG, JPG, SVG, CSV o GraphML. Los marcos de módulo pueden incluirse en PNG, JPG y SVG. CSV registra la asignación activa de módulos Similarity o Top-level MP y las listas de fenotipos; GraphML es compatible con Cytoscape.

# 🛠 Interfaz de línea de comandos

El CLI de TSUMUGI permite usar localmente los datos IMPC más recientes y ofrece filtros y salidas más detalladas que la herramienta web.

## Características

- Recalcular con `statistical-results-ALL.csv.gz` de IMPC (opcional `mp.obo`, `impc_phenodigm.csv`).  
- Filtrar por presencia/ausencia de términos MP.  
- Filtrar por lista de genes (separada por comas o archivo de texto).  
- Salidas: GraphML (`tsumugi build-graphml`), bundle webapp sin conexión (`tsumugi build-webapp`).

## Instalación

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Listo cuando `tsumugi --version` muestra la versión.

## Comandos disponibles

- `tsumugi run`: recalcular la red desde datos IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: filtrar pares o genes que contienen/no muestran un término MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: filtrar por número de fenotipos (pares/gen)  
- `tsumugi score (--min/--max)`: filtrar por puntuación de similitud (pares)  
- `tsumugi genes --keep/--drop`: conservar/eliminar por lista de genes (comas o archivo de texto)  
- `tsumugi life-stage --keep/--drop`: filtrar por etapa de vida (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: filtrar por sexo (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: filtrar por cigocidad (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: generar GraphML (Cytoscape, etc.)  
- `tsumugi build-webapp`: generar assets web de TSUMUGI (HTML/CSS/JS locales)

> [!NOTE]
> Todos los subcomandos de filtrado emiten JSONL a STDOUT.  
> Redirige con `>` si quieres guardar en un archivo.

> [!IMPORTANT]
> Todos los comandos excepto `tsumugi run` requieren `pairwise_similarity_annotation.jsonl.gz` o `genewise_phenotype_annotation.jsonl.gz`.
> Ambos archivos pueden descargarse desde la [página principal de TSUMUGI](https://larc-tsukuba.github.io/tsumugi/).

## Uso

### Recalcular desde datos IMPC (`tsumugi run`)
Si se omite `--mp_obo`, TSUMUGI usa el `data-version: releases/2025-08-27/mp.obo` incluido.  
Si se omite `--impc_phenodigm`, usa el archivo obtenido el 2025-10-01 desde el [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Salidas: `./tsumugi-output` contiene anotaciones genewise (genewise_phenotype_annotations.jsonl.gz), datos de similitud pairwise (pairwise_similarity_annotations.jsonl.gz) y assets de visualización (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> El directorio `TSUMUGI-webapp` incluye scripts de arranque por SO; haz doble clic para abrir la app local:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filtrar por término MP (`tsumugi mp --include/--exclude`)
Extrae pares de genes (o genes) que incluyan fenotipos de interés, o pares medidos sin anomalías significativas.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Incluye genes/pares que tengan el término MP especificado (descendientes incluidos).

#### `-e MP_ID`, `--exclude MP_ID`
Devuelve genes/pares medidos para el término MP (descendientes incluidos) que no mostraron un fenotipo significativo. Requiere `-a/--genewise_annotations`.

#### `-g`, `--genewise`
Filtra a nivel de gen. Lee `genewise_phenotype_annotations.jsonl(.gz)`. Con `--genewise`, indica `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filtra a nivel de pares. Apunta a `pairwise_similarity_annotations.jsonl(.gz)`. Si se omite `--in`, lee desde STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Ruta al ontology Mammalian Phenotype (mp.obo). Si se omite, usa `data/mp.obo` incluido.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Ruta al archivo genewise (JSONL/.gz). Requerido para `--exclude`; indícalo también con `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

#### `--life_stage LIFE_STAGE`
Filtro adicional por etapa de vida. Valores: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Filtro adicional por dimorfismo sexual. Usa valores de las anotaciones (p. ej., `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Filtro adicional por cigocidad. Valores: `Homo`, `Hetero`, `Hemi`.

```bash
# Extraer solo pares que incluyan MP:0001146 (abnormal testis morphology) o términos descendientes (p. ej., MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Extraer pares donde MP:0001146 y términos descendientes se midieron sin anomalía significativa
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Extraer anotaciones significativas a nivel de gen que contengan MP:0001146 (descendientes incluidos)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Extraer genes medidos para MP:0001146 (descendientes incluidos) sin anomalía significativa
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **También se manejan términos MP descendientes del ID especificado.**  
> Por ejemplo, si indicas `MP:0001146 (abnormal testis morphology)`, también se consideran términos descendientes como `MP:0004849 (abnormal testis size)`.

### Filtrar por número de fenotipos (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filtra genes o pares por el número de fenotipos. Se requiere al menos `--min` o `--max`.

#### `-g`, `--genewise`
Filtra por número de fenotipos significativos por gen. Requiere `-a/--genewise_annotations` con `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filtra por número de fenotipos compartidos por par. Si se omite `--in`, lee desde STDIN.

#### `--min MIN`, `--max MAX`
Límites inferior/superior del número de fenotipos. Un solo límite sirve para filtrado unilateral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Ruta al archivo genewise (JSONL/.gz). Requerido con `--genewise`.

- Fenotipos compartidos por par:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Fenotipos por gen (requiere genewise):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

Se puede usar solo `--min` o `--max`.

### Filtrar por puntuación de similitud (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filtra pares por `phenotype_similarity_score` (0–100). Se requiere al menos `--min` o `--max`.

#### `--min MIN`, `--max MAX`
Límites inferior/superior del score. Un solo límite sirve para filtrado unilateral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

Se puede usar solo `--min` o `--max`.

### Filtrar por lista de genes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Conserva solo pares que contengan los genes especificados en un archivo de texto.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Elimina pares que contengan los genes especificados en un archivo de texto.

#### `-g`, `--genewise`
Filtra por símbolos de genes proporcionados por el usuario.

#### `-p`, `--pairwise`
Filtra por pares de genes proporcionados por el usuario.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

```bash
cat << EOF > genes.txt
Maf
Aamp
Cacna1c
EOF

tsumugi genes --genewise --keep genes.txt   --in "$directory"/pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

cat << EOF > gene_pairs.csv
Maf,Aamp
Maf,Cacna1c
EOF

tsumugi genes --pairwise --drop gene_pairs.csv   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_drop_genes.jsonl

```

### Filtrar por etapa de vida (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Conserva solo la etapa de vida indicada (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Elimina la etapa de vida indicada.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Filtrar por sexo (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Conserva solo el sexo indicado (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Elimina el sexo indicado.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Filtrar por cigocidad (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Conserva solo la cigocidad indicada (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Elimina la cigocidad indicada.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### Exportar GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Ruta al archivo genewise (JSONL/.gz). Requerido.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Ruta al archivo pairwise (JSONL/.gz). Si se omite, lee desde STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Ruta al archivo genewise (JSONL/.gz). Requerido.

#### `-o OUT`, `--out OUT`
Directorio de salida del bundle webapp (HTML/CSS/JS + datos de red). No especifiques un nombre de archivo con extensión.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

El CLI admite STDIN/STDOUT, así que puedes encadenar comandos:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cómo calculamos los genes con fenotipos similares

## Fuente de datos

Usamos el conjunto de datos IMPC [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Columnas del dataset: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Preprocesamiento

Extraemos pares gen–fenotipo cuyos P-values en ratón KO (`p_value`, `female_ko_effect_p_value` o `male_ko_effect_p_value`) son ≤ 0.0001.  
- Anotamos los fenotipos específicos por genotipo como `homo`, `hetero` o `hemi`.  
- Anotamos los fenotipos específicos por sexo como `female` o `male`.

## Similitud fenotípica

TSUMUGI aplica la fórmula de puntuación original de PhenoDigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) para comparar perfiles fenotípicos de genes de ratón KO de IMPC dentro de Mammalian Phenotype Ontology.

> [!NOTE]
> TSUMUGI utiliza la fórmula de puntuación de PhenoDigm, pero no ejecuta el pipeline original entre especies HPO-MP/ZP OWLSim. Compara anotaciones MP de genes de ratón KO de IMPC.

### 1. Definición de la similitud de pares de términos MP

* Construir la ontología MP y calcular el Information Content (IC) a partir de anotaciones significativas de IMPC:
   `IC(term) = -log2(|anotaciones propagadas al término| / |todas las anotaciones significativas|)`
   Cada anotación directa se propaga al término MP anotado y a todos sus ancestros.

* Para cada par de términos MP, encontrar los ancestros comunes con el IC derivado de anotaciones más alto. Si hay empate, seleccionar de forma determinista el candidato con menos descendientes transitivos en la ontología MP y después el ID de término MP lexicográficamente menor. El IC del MICA seleccionado es la similitud de Resnik. Este desempate no cambia la puntuación de similitud ni el esquema de salida.

* Para dos términos MP, calcular el índice de Jaccard de sus conjuntos de atributos inferidos, definidos como cada término más todos sus ancestros.

* Definir la similitud de pares de términos MP como `sqrt(Resnik * Jaccard)`.

### 2. Matriz de similitud de pares de genes

* Para cada par de genes, construir una matriz de similitud término MP × término MP a partir de las puntuaciones de pares de términos.

* Los metadatos de genotipo, etapa de vida y sexo se conservan en las anotaciones de fenotipos compartidos, pero no ponderan la puntuación PhenoDigm.

### 3. Escalado Phenodigm

* Aplicar el escalado máximo/promedio de PhenoDigm para normalizar la similitud de cada par de genes de ratón KO a 0–100:
   Calcular el máximo y la media de best match observados y normalizar por la puntuación óptima simétrica de self match de los dos genes.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Si el denominador es 0, la puntuación es 0.

---

# ✉️ Contacto
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Citación

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

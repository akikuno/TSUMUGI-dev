> ⚠️ Tradução gerada por IA; em caso de dúvida consulte o original (README.md).  
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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** é uma ferramenta web que usa dados de fenótipo de camundongos KO do [IMPC](https://www.mousephenotype.org/) para **extrair e visualizar módulos gênicos com base na similaridade fenotípica**.  
Disponível para todos na web 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI (紡ぎ)** vem da ideia de “tecer os grupos de genes que formam os fenótipos”.

# 📖 Como usar o TSUMUGI

TSUMUGI oferece três tipos de entrada.

### Fenótipo (Phenotype)
Informe um fenótipo de interesse para buscar **genes cujos KO tenham perfis fenotípicos semelhantes**.  
Nomes baseados na [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Lista de fenótipos](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gene (Gene)
Informe um gene para encontrar **outros genes com fenótipos KO parecidos**.  
Símbolos seguem a [MGI](http://www.informatics.jax.org/).  
👉 [Lista de genes](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Lista de genes (Gene List)
Cole vários genes (um por linha) para buscar **dentro da lista**.  
> [!CAUTION]  
> Se nada for encontrado: `No similar phenotypes were found among the entered genes.`  
> Se mais de 200: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Baixar dados brutos
TSUMUGI publica arquivos JSONL comprimidos em gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Símbolo do gene (ex.: "1110059G10Rik")  
- Marker accession ID (ex.: "MGI:1913452")  
- Nome/ID do fenótipo (ex.: "fused joints", "MP:0000137")  
- Effect size (ex.: 0.0, 1.324)  
- Significância (True/false)  
- Zigosidade ("Homo", "Hetero", "Hemi")  
- Estágio de vida ("Embryo", "Early", "Interval", "Late")  
- Dimorfismo sexual ("", "Male", "Female")  
- Anotação de doença (ex.: [] ou "Premature Ovarian Failure 18")

Exemplo:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Par de genes (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadados (estágio de vida, zigosidade, sexo) para fenótipos compartilhados  
- `phenotype_similarity_score`: Resnik→Phenodigm (0–100)

Exemplo:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Rede

Página muda e desenha a rede automaticamente.

> [!IMPORTANT]  
> Visualiza pares com **≥3 fenótipos anormais compartilhados** e **similaridade > 0.0**.

### Painel da rede
**Nós** representam genes. Clique para ver fenótipos anormais; arraste para reposicionar.  
**Arestas**: clique para ver detalhes de fenótipos compartilhados.

### Painel de controle
Ajuste de exibição no painel esquerdo.

#### Filtrar por similaridade fenotípica
`Phenotypes similarity` define o limiar das arestas pelo score Resnik→Phenodigm.  
> Detalhes: 👉 [🔍 Cálculo de grupos de genes com fenótipos similares](#-cálculo-de-grupos-de-genes-com-fenótipos-similares)

#### Filtrar por severidade fenotípica
`Phenotype severity` filtra nós por effect size em KO; valores maiores indicam impacto maior.  
> Oculto para fenótipos binários (ex.: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); lista binária [aqui](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) ou entrada de um gene.

#### Especificar genótipo
- `Homo`
- `Hetero`
- `Hemi`

#### Especificar sexo
- `Female`
- `Male`

#### Especificar estágio de vida
- `Embryo`
- `Early` (0–16 semanas)
- `Interval` (17–48 semanas)
- `Late` (49+ semanas)

### Painel de marcação
#### Highlight: Human Disease
Realça genes associados a doenças humanas (IMPC Disease Models Portal).

#### Search: Specific Gene
Busca nomes de genes na rede.

#### Layout & Display
Ajusta layout, tamanho de fonte, espessura de aresta, repulsão de nós (Cose).

#### Export
Exporta PNG/CSV/GraphML. CSV inclui IDs de módulo e listas de fenótipos; GraphML é compatível com Cytoscape.

# 🛠 Versão linha de comando

Esta versão adiciona o CLI para recalcular com dados IMPC, aplicar filtros finos e exportar GraphML ou webapp offline.

- Recalcular com `statistical-results-ALL.csv.gz` (opcional `mp.obo`, `impc_phenodigm.csv`)  
- Filtrar presença/ausência de termos MP  
- Filtrar por lista de genes (CSV ou texto)  
- Saídas: GraphML (`tsumugi build-graphml`), webapp offline (`tsumugi build-webapp`)

## Comandos disponíveis
- `tsumugi run`: recalcular a rede a partir de dados IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: incluir/excluir pares ou genes pelo termo MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: filtrar por contagem de fenótipos (pares/genes)  
- `tsumugi score (--min/--max)`: filtrar por pontuação de similaridade (pares de genes)
- `tsumugi genes --keep/--drop`: manter/remover por lista de genes  
- `tsumugi life-stage --keep/--drop`: filtrar por estágio de vida  
- `tsumugi sex --keep/--drop`: filtrar por sexo  
- `tsumugi zygosity --keep/--drop`: filtrar por zigosidade  
- `tsumugi build-graphml`: gerar GraphML  
- `tsumugi build-webapp`: gerar assets da webapp TSUMUGI

## Instalação
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
Pronto se `tsumugi --version` mostrar a versão.

## Uso comum (por comando)

### Recalcular com dados IMPC (`tsumugi run`)
Se `--mp_obo` for omitido, usa o `data-version: releases/2025-08-27/mp.obo` incluído.  
Se `--impc_phenodigm` for omitido, usa o arquivo obtido em 01/10/2025 do [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Saídas: `./tsumugi-output` contém genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz e assets de visualização (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` traz scripts específicos por SO; clique duplo abre o app local:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filtrar por termo MP (`tsumugi mp --include/--exclude`)
Extraia apenas pares de genes com os fenótipos de interesse ou pares em que esses fenótipos foram medidos, mas não apresentaram anomalias significativas.

- `--pairwise` (padrão se nada for definido): saída em pares de genes. Use `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: saída por gene individual. Use `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (obrigatório com `--exclude`, recomendado com `--include`).

```bash
# Extrair apenas os pares que incluam MP:0001146 (abnormal testis morphology) ou termos descendentes (ex.: MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extrair pares em que MP:0001146 e termos descendentes foram medidos e não mostraram anomalia significativa
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extrair anotações significativas por gene contendo MP:0001146 (descendentes incluídos)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Extrair genes medidos para MP:0001146 (descendentes incluídos) sem anomalia significativa
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Termos MP descendentes do ID especificado também são considerados.**  
> Por exemplo, ao indicar `MP:0001146 (abnormal testis morphology)`, termos descendentes como `MP:0004849 (abnormal testis size)` também são incluídos.

### Filtrar por número de fenótipos (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- Fenótipos compartilhados por par:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Fenótipos por gen (genewise necessário):
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```


### Filtrar por pontuação de similaridade (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Filtra pares de genes por `phenotype_similarity_score` (0–100). É obrigatório informar ao menos `--min` ou `--max`.

#### `--min MIN`, `--max MAX`
Limites inferior/superior do score. Use apenas um deles para filtragem unidirecional.

#### `--in IN`
Caminho para o arquivo de anotações pairwise (JSONL/.gz); se omitido, lê de STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` ou `--max` isoladamente funciona.

### Lista de genes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Estágio de vida / sexo / zigosidade
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### Exportar GraphML / Webapp
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
```
Pipeline: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cálculo de grupos gênicos com fenótipos similares

## Fonte de dados
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Campos: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Pré-processamento
Extrair pares gen–fenótipo com P ≤ 0.0001 (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`).  
- Zigosidade: `homo`, `hetero`, `hemi`  
- Sexo: `female`, `male`

## Similaridade fenotípica
Calcula **Resnik** entre termos MP e escala para **Phenodigm (0–100)**.

1. Construir ontologia MP e calcular IC:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC do ancestral comum mais informativo (MICA); se não houver, 0.  
3. Para cada par: matriz de Resnik dos termos significativos, ponderada por metadados (zigosidade/estágio/sexo: 1.0/0.75/0.5/0.25); obter max/média reais.  
4. Derivar max/média teóricos dos IC e normalizar:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   Se o denominador teórico for 0, usar 0. O score 0–100 alimenta os downloads e o controle `Phenotypes similarity`.

# ✉️ Contato
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

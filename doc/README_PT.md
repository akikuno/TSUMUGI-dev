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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** é uma ferramenta web que usa dados de fenótipo de camundongos KO do [IMPC](https://www.mousephenotype.org/) para **extrair e visualizar módulos gênicos com base na similaridade fenotípica**.  
Disponível para todos na web 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Esta documentação descreve o funcionamento atual do **TSUMUGI v1.1.0**. A aplicação web pública utiliza dados do IMPC **Release 24.0**.

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
> Se a rede gerada contiver 200 genes ou mais: `Too many genes submitted. Please limit the number to 200 or fewer.`

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
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Par de genes (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadados (estágio de vida, zigosidade, sexo) para fenótipos compartilhados  
- `phenotype_similarity_score`: Resnik→Phenodigm (0–100)

Exemplo:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Rede

Página muda e desenha a rede automaticamente.

> [!IMPORTANT]  
> Visualiza pares com **≥3 fenótipos anormais compartilhados** e **similaridade > 0.0**.

### Painel da rede
**Nós** representam genes. Clique para ver fenótipos anormais; arraste para reposicionar.  
**Arestas**: clique para ver detalhes de fenótipos compartilhados.  
**Módulos** contornam sub-redes gênicas. Clique para listar fenótipos dos genes do módulo; arraste os módulos para reposicionar e evitar sobreposição.
As páginas Gene usam módulos Top-level MP soft/fuzzy, portanto um gene pode pertencer a vários módulos. As páginas Phenotype e Gene List podem alternar entre módulos `Similarity` baseados em componentes conectados e módulos `Top-level MP`.

### Painel de controle
Ajuste de exibição no painel esquerdo.

#### Filtrar por similaridade fenotípica
`Phenotypes similarity` define o limiar das arestas pelo score Resnik→Phenodigm.  
> Detalhes: 👉 [🔍 Cálculo de grupos de genes com fenótipos similares](#-cálculo-de-grupos-de-genes-com-fenótipos-similares)

#### Filtrar por effect size
`Effect size` filtra nós pela magnitude do effect size derivado do IMPC quando disponível.
Effect sizes ausentes permanecem ausentes, não são convertidos em zero, e os nós correspondentes são exibidos em branco.
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
#### Exibição de módulos
No painel direito, selecione a definição e o módulo visível. As bordas dos módulos podem ser ocultadas sem remover genes ou arestas da rede.

#### Highlight: Human Disease
Realça genes associados a doenças humanas (IMPC Disease Models Portal).

#### Search: Specific Gene
Busca nomes de genes na rede.

#### Layout & Display
Ajusta layout, tamanho de fonte, espessura de aresta, repulsão de nós (Cose).

#### Export
Exporta PNG, JPG, SVG, CSV ou GraphML. As molduras dos módulos podem ser incluídas em PNG, JPG e SVG. O CSV registra a atribuição ativa de módulos Similarity ou Top-level MP e as listas de fenótipos; GraphML é compatível com Cytoscape.

# 🛠 Interface de linha de comando

A CLI do TSUMUGI permite usar localmente os dados IMPC mais recentes e oferece filtros e saídas mais detalhadas que a ferramenta web.

## Recursos

- Recalcular com `statistical-results-ALL.csv.gz` do IMPC (opcional `mp.obo`, `impc_phenodigm.csv`).  
- Filtrar por presença/ausência de termos MP.  
- Filtrar por lista de genes (separada por vírgulas ou arquivo de texto).  
- Saídas: GraphML (`tsumugi build-graphml`), bundle webapp offline (`tsumugi build-webapp`).

## Instalação

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Pronto quando `tsumugi --version` exibir a versão.

## Comandos disponíveis

- `tsumugi run`: recalcular a rede a partir dos dados IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: filtrar pares ou genes que contêm/não mostram um termo MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: filtrar por número de fenótipos (pares/genes)  
- `tsumugi score (--min/--max)`: filtrar por score de similaridade (pares)  
- `tsumugi genes --keep/--drop`: manter/remover por lista de genes (vírgulas ou arquivo de texto)  
- `tsumugi life-stage --keep/--drop`: filtrar por estágio de vida (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: filtrar por sexo (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: filtrar por zigotia (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: gerar GraphML (Cytoscape, etc.)  
- `tsumugi build-webapp`: gerar assets web do TSUMUGI (HTML/CSS/JS locais)

> [!NOTE]
> Todos os subcomandos de filtragem enviam JSONL para STDOUT.  
> Redirecione com `>` se quiser salvar em um arquivo.

> [!IMPORTANT]
> Todos os comandos, exceto `tsumugi run`, exigem `pairwise_similarity_annotation.jsonl.gz` ou `genewise_phenotype_annotation.jsonl.gz`.
> Ambos os arquivos podem ser baixados na [página inicial do TSUMUGI](https://larc-tsukuba.github.io/tsumugi/).

## Uso

### Recalcular a partir dos dados IMPC (`tsumugi run`)
Se `--mp_obo` for omitido, o TSUMUGI usa o `data-version: releases/2025-08-27/mp.obo` incluído.  
Se `--impc_phenodigm` for omitido, usa o arquivo obtido em 2025-10-01 no [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Saídas: `./tsumugi-output` contém anotações genewise (genewise_phenotype_annotations.jsonl.gz), dados de similaridade pairwise (pairwise_similarity_annotations.jsonl.gz) e assets de visualização (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> O diretório `TSUMUGI-webapp` inclui scripts de inicialização por SO; dê duplo clique para abrir o app local:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filtrar por termo MP (`tsumugi mp --include/--exclude`)
Extraia pares de genes (ou genes) que incluam fenótipos de interesse, ou pares medidos sem anomalia significativa.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Inclui genes/pares que tenham o termo MP especificado (descendentes incluídos).

#### `-e MP_ID`, `--exclude MP_ID`
Retorna genes/pares medidos para o termo MP (descendentes incluídos) que não mostraram fenótipo significativo. Requer `-a/--genewise_annotations`.

#### `-g`, `--genewise`
Filtra no nível de gene. Lê `genewise_phenotype_annotations.jsonl(.gz)`. Ao usar `--genewise`, indique `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filtra no nível de pares. Alvo: `pairwise_similarity_annotations.jsonl(.gz)`. Se `--in` for omitido, lê de STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Caminho para a ontologia Mammalian Phenotype (mp.obo). Se omitido, usa `data/mp.obo` incluído.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Caminho para o arquivo genewise (JSONL/.gz). Obrigatório para `--exclude`; indique também com `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

#### `--life_stage LIFE_STAGE`
Filtro adicional por estágio de vida. Valores: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Filtro adicional por dimorfismo sexual. Use os valores das anotações (ex.: `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Filtro adicional por zigotia. Valores: `Homo`, `Hetero`, `Hemi`.

```bash
# Extrair apenas pares que incluam MP:0001146 (abnormal testis morphology) ou termos descendentes (ex.: MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Extrair pares em que MP:0001146 e termos descendentes foram medidos sem anomalia significativa
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Extrair anotações significativas no nível de gene contendo MP:0001146 (descendentes incluídos)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Extrair genes medidos para MP:0001146 (descendentes incluídos) sem anomalia significativa
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Os termos MP descendentes do ID especificado também são considerados.**  
> Por exemplo, se você indicar `MP:0001146 (abnormal testis morphology)`, termos descendentes como `MP:0004849 (abnormal testis size)` também são incluídos.

### Filtrar por número de fenótipos (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filtra genes ou pares pelo número de fenótipos. Pelo menos `--min` ou `--max` é obrigatório.

#### `-g`, `--genewise`
Filtra pelo número de fenótipos significativos por gene. Requer `-a/--genewise_annotations` com `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filtra pelo número de fenótipos compartilhados por par. Se `--in` for omitido, lê de STDIN.

#### `--min MIN`, `--max MAX`
Limites inferior/superior do número de fenótipos. Um único limite serve para filtragem unilateral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Caminho para o arquivo genewise (JSONL/.gz). Obrigatório com `--genewise`.

- Fenótipos compartilhados por par:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Fenótipos por gene (genewise requerido):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

É possível usar somente `--min` ou `--max`.

### Filtrar por score de similaridade (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filtra pares por `phenotype_similarity_score` (0–100). Pelo menos `--min` ou `--max` é obrigatório.

#### `--min MIN`, `--max MAX`
Limites inferior/superior do score. Um único limite serve para filtragem unilateral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

É possível usar somente `--min` ou `--max`.

### Filtrar por lista de genes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Mantém apenas pares que contenham os genes especificados em um arquivo de texto.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Remove pares que contenham os genes especificados em um arquivo de texto.

#### `-g`, `--genewise`
Filtra por símbolos de genes fornecidos pelo usuário.

#### `-p`, `--pairwise`
Filtra por pares de genes fornecidos pelo usuário.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

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

### Filtrar por estágio de vida (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Mantém apenas o estágio de vida indicado (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Remove o estágio de vida indicado.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Filtrar por sexo (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Mantém apenas o sexo indicado (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Remove o sexo indicado.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Filtrar por zigotia (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Mantém apenas a zigotia indicada (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Remove a zigotia indicada.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### Exportar GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Caminho para o arquivo genewise (JSONL/.gz). Obrigatório.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Caminho para o arquivo pairwise (JSONL/.gz). Se omitido, lê de STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Caminho para o arquivo genewise (JSONL/.gz). Obrigatório.

#### `-o OUT`, `--out OUT`
Diretório de saída do bundle webapp (HTML/CSS/JS + dados de rede). Não forneça um nome de arquivo com extensão.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

A CLI suporta STDIN/STDOUT, então você pode encadear comandos:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cálculo de grupos gênicos com fenótipos similares

## Fonte de dados

Usamos o conjunto de dados IMPC [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Colunas do dataset: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Pré-processamento

Extraímos pares gene–fenótipo cujos P-values em camundongos KO (`p_value`, `female_ko_effect_p_value` ou `male_ko_effect_p_value`) são ≤ 0.0001.  
- Anotar fenótipos específicos de genótipo como `homo`, `hetero` ou `hemi`.  
- Anotar fenótipos específicos de sexo como `female` ou `male`.

## Similaridade fenotípica

O TSUMUGI aplica a fórmula de pontuação original do PhenoDigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) para comparar perfis fenotípicos de genes de camundongos KO do IMPC na Mammalian Phenotype Ontology.

> [!NOTE]
> O TSUMUGI usa a fórmula de pontuação do PhenoDigm, mas não executa o pipeline original entre espécies HPO-MP/ZP OWLSim. Ele compara anotações MP de genes de camundongos KO do IMPC.

### 1. Definição da similaridade de pares de termos MP

* Construir a ontologia MP e calcular o Information Content (IC) a partir de anotações significativas do IMPC:
   `IC(term) = -log2(|anotações propagadas para o termo| / |todas as anotações significativas|)`
   Cada anotação direta é propagada para o termo MP anotado e todos os seus ancestrais.

* Para cada par de termos MP, encontrar os ancestrais comuns com o maior IC derivado de anotações. Em caso de empate, selecionar de forma determinística o candidato com menos descendentes transitivos na ontologia MP e, depois, o menor ID de termo MP em ordem lexicográfica. O IC do MICA selecionado é a similaridade de Resnik. Esse desempate não altera o score de similaridade nem o schema de saída.

* Para dois termos MP, calcular o índice de Jaccard dos conjuntos de atributos inferidos, definidos como o próprio termo e todos os seus ancestrais.

* Definir a similaridade de pares de termos MP como `sqrt(Resnik * Jaccard)`.

### 2. Matriz de similaridade de pares de genes

* Para cada par de genes, construir uma matriz de similaridade termo MP × termo MP a partir dos scores de pares de termos.

* Os metadados de genótipo, estágio de vida e sexo são preservados nas anotações de fenótipos compartilhados, mas não ponderam o score PhenoDigm.

### 3. Escalonamento Phenodigm

* Aplicar o escalonamento máximo/média do PhenoDigm para normalizar a similaridade de cada par de genes de camundongos KO em 0–100:
   Calcular o máximo e a média de best match observados e normalizar pelo score ótimo simétrico de self match dos dois genes.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Se o denominador for 0, a pontuação será 0.

---

# ✉️ Contato
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Citação

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

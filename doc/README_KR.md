> ⚠️ 본 문서는 생성 AI 번역본입니다. 정확한 내용은 원문(README.md)을 참조해 주세요.  
> 원문: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI(Trait-driven Surveillance for Mutation-based Gene module Identification)**는 [IMPC](https://www.mousephenotype.org/)의 KO 마우스 표현형 데이터를 활용해 **표현형 유사성 기반의 유전자 모듈을 추출·시각화하는 웹 도구**입니다.  
웹에서 누구나 사용할 수 있는 공개 도구입니다👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI(紡ぎ)**는 “표현형을 이루는 유전자 군을 실잣듯 엮는다”는 뜻에서 유래했습니다.

# 📖 TSUMUGI 사용법

TSUMUGI는 세 가지 입력을 지원합니다.

### 표현형(Phenotype)
관심 있는 표현형을 입력하면, 그 표현형을 보이는 KO 마우스 유전자의 집합 중에서 **다른 표현형도 유사한 유전자 군**을 탐색합니다.  
표현형 이름은 [Mammalian Phenotype Ontology(MPO)](https://www.informatics.jax.org/vocab/mp_ontology)를 따릅니다.  
👉 [표현형 목록](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 유전자명(Gene)
유전자 하나를 지정하면, **그 KO 마우스와 표현형이 비슷한 다른 유전자 군**을 탐색합니다.  
유전자 명칭은 [MGI](http://www.informatics.jax.org/) 기호를 따릅니다.  
👉 [유전자 목록](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 유전자 리스트(Gene List)
여러 유전자를 줄바꿈으로 입력합니다. **리스트 내부의 유전자들 간** 표현형 유사 유전자를 추출합니다.  
> [!CAUTION]  
> 유사 유전자를 하나도 찾지 못하면 `No similar phenotypes were found among the entered genes.` 경고 후 중단합니다.  
> 200개를 초과하면 `Too many genes submitted. Please limit the number to 200 or fewer.` 경고 후 중단합니다.

### 📥 원시 데이터 다운로드
TSUMUGI는 gzip 압축된 JSONL을 제공합니다.

#### `genewise_phenotype_annotations.jsonl.gz`
- 유전자 심벌(예: "1110059G10Rik")  
- 마커 Accession ID(예: "MGI:1913452")  
- 표현형 명/ID(예: "fused joints", "MP:0000137")  
- Effect size(예: 0.0, 1.324)  
- 유의성(True/false)  
- Zygosity("Homo", "Hetero", "Hemi")  
- Life stage("Embryo", "Early", "Interval", "Late")  
- Sexual dimorphism("", "Male", "Female")  
- Disease annotation(예: [] 또는 "Premature Ovarian Failure 18")

예시:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 유전자 쌍(`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`(라이프 스테이지, 접합형, 성별 등 공유 표현형 메타데이터)  
- `phenotype_similarity_score`(Resnik 기반 Phenodigm 점수, 0–100)

예시:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 네트워크

입력에 따라 페이지가 전환되고 네트워크가 자동으로 그려집니다.

> [!IMPORTANT]  
> **공유하는 이상 표현형이 3개 이상이고 표현형 유사도가 0.0보다 큰** 유전자 쌍이 시각화 대상입니다.

### 네트워크 패널
**노드**는 유전자를 나타냅니다. 클릭하면 KO 마우스에서 관찰된 이상 표현형 리스트를 표시하며, 드래그로 위치를 조정할 수 있습니다.  
**엣지**를 클릭하면 공유 표현형의 상세를 볼 수 있습니다.  
**모듈**은 유전자 서브네트워크를 다각형으로 둘러싸 표시합니다. 모듈을 클릭하면 포함된 유전자의 관련 표현형을 보여주며, 드래그로 이동시켜 겹치지 않게 배치할 수 있습니다.

### 컨트롤 패널
좌측 패널에서 네트워크 표시를 조정할 수 있습니다.

#### 표현형 유사도 필터
`Phenotypes similarity` 슬라이더로 Resnik→Phenodigm 점수를 기준으로 엣지 표시 임계를 설정합니다.  
> 자세한 계산 방법: 👉 [🔍 표현형 유사 유전자군 계산](#-표현형-유사-유전자군-계산)

#### 표현형 중증도 필터
`Phenotype severity` 슬라이더로 KO 마우스의 효과량(중증도)에 따라 노드를 필터링합니다. 값이 클수록 영향이 큽니다.  
> 이진 표현형(예: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); 이진 목록은 [여기](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt))나 단일 유전자 입력 시에는 표시되지 않습니다.

#### Genotype 지정
표현형이 나타나는 접합형을 선택:
- `Homo` (동형접합)
- `Hetero` (이형접합)
- `Hemi` (반측접합)

#### 성별 지정
- `Female`
- `Male`

#### 라이프 스테이지 지정
- `Embryo`
- `Early`(0–16주)
- `Interval`(17–48주)
- `Late`(49주 이상)

### 마크업 패널
#### Highlight: Human Disease
IMPC Disease Models Portal 데이터를 사용해 질병 관련 유전자를 하이라이트합니다.

#### Search: Specific Gene
네트워크 내 유전자명을 검색합니다.

#### Layout & Display
레이아웃, 폰트 크기, 엣지 두께, 노드 반발력(Cose 레이아웃)을 조정합니다.

#### Export
PNG/CSV/GraphML로 내보낼 수 있습니다.  
CSV에는 모듈ID와各 유전자의 표현형 리스트가 포함되며, GraphML은 Cytoscape 호환입니다.

# 🛠 커맨드라인 인터페이스

TSUMUGI CLI는 로컬에 다운로드한 최신 IMPC 데이터를 사용해 재계산할 수 있으며, 웹 버전보다 더 세밀한 필터와 출력 옵션을 제공합니다.

## 기능

- IMPC `statistical-results-ALL.csv.gz`로 재계산(선택적으로 `mp.obo`, `impc_phenodigm.csv`).  
- MP 용어 포함/제외 필터.  
- 유전자 목록 필터(콤마 구분 또는 텍스트 파일).  
- 출력: GraphML(`tsumugi build-graphml`), 오프라인 웹앱 번들(`tsumugi build-webapp`).

## 설치

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

`tsumugi --version`이 버전을 출력하면 사용 가능합니다.

## 사용 가능한 명령

- `tsumugi run`: IMPC 데이터에서 네트워크 재계산  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: MP 용어를 포함/비포함하는 유전자 쌍 또는 유전자 필터  
- `tsumugi count --pairwise/--genewise (--min/--max)`: phenotype 개수로 필터(쌍/유전자)  
- `tsumugi score (--min/--max)`: phenotype 유사도 점수로 필터(쌍)  
- `tsumugi genes --keep/--drop`: 유전자 목록 기준 유지/제외(콤마 또는 텍스트 파일)  
- `tsumugi life-stage --keep/--drop`: 생애 단계 필터(Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: 성별 필터(Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: 접합형 필터(Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: GraphML 생성(Cytoscape 등)  
- `tsumugi build-webapp`: TSUMUGI 웹앱 에셋 생성(로컬 HTML/CSS/JS)

> [!NOTE]
> 모든 필터링 서브커맨드는 JSONL을 STDOUT으로 출력합니다.  
> 파일로 저장하려면 `>`로 리다이렉트하세요.

> [!IMPORTANT]
> `tsumugi run`을 제외한 모든 명령은 `pairwise_similarity_annotation.jsonl.gz` 또는 `genewise_phenotype_annotation.jsonl.gz`가 필요합니다.
> 두 파일 모두 [TSUMUGI 메인 페이지](https://larc-tsukuba.github.io/tsumugi/)에서 다운로드할 수 있습니다.

## 사용법

### IMPC 데이터로 재계산(`tsumugi run`)
`--mp_obo`를 생략하면 TSUMUGI는 번들 `data-version: releases/2025-08-27/mp.obo`를 사용합니다.  
`--impc_phenodigm`를 생략하면 2025-10-01에 [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)에서 가져온 파일을 사용합니다.
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
출력: `./tsumugi-output`에는 genewise 주석(genewise_phenotype_annotations.jsonl.gz), pairwise 유사도 데이터(pairwise_similarity_annotations.jsonl.gz), 시각화 에셋(`TSUMUGI-webapp`)이 포함됩니다.

> [!IMPORTANT]  
> `TSUMUGI-webapp` 디렉터리에는 OS별 실행 스크립트가 포함되어 있습니다. 더블 클릭하면 로컬 웹앱을 열 수 있습니다:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### MP 용어로 필터(`tsumugi mp --include/--exclude`)
관심 있는 phenotype를 포함하는 유전자 쌍(또는 유전자)을 추출하거나, 측정되었지만 유의한 이상이 없던 쌍을 추출합니다.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
지정한 MP 용어(하위 용어 포함)를 가진 유전자/유전자 쌍을 포함합니다.

#### `-e MP_ID`, `--exclude MP_ID`
지정한 MP 용어(하위 용어 포함)를 측정했지만 유의한 phenotype가 없었던 유전자/유전자 쌍을 반환합니다. `-a/--genewise_annotations`가 필요합니다.

#### `-g`, `--genewise`
유전자 단위로 필터합니다. `genewise_phenotype_annotations.jsonl(.gz)`를 읽으며, `--genewise` 사용 시 `-a/--genewise_annotations`를 지정합니다.

#### `-p`, `--pairwise`
유전자 쌍 단위로 필터합니다. `pairwise_similarity_annotations.jsonl(.gz)`를 대상으로 하며, `--in`을 생략하면 STDIN에서 읽습니다.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Mammalian Phenotype ontology(mp.obo) 경로. 생략 시 `data/mp.obo`를 사용합니다.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise 주석 파일(JSONL/.gz) 경로. `--exclude`에서 필수이며, `--genewise`에서도 지정해야 합니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

#### `--life_stage LIFE_STAGE`
생애 단계 추가 필터. 가능한 값: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
성별 추가 필터. 주석에 있는 값(예: `Male`, `Female`, `None`)을 사용하세요.

#### `--zygosity ZYGOSITY`
접합형 추가 필터. 가능한 값: `Homo`, `Hetero`, `Hemi`.

```bash
# MP:0001146(abnormal testis morphology) 또는 하위 용어(예: MP:0004849 abnormal testis size)를 포함하는 유전자 쌍만 추출
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# MP:0001146 및 하위 용어가 측정되었지만 유의한 이상이 없던 유전자 쌍을 추출
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 유전자 단위로 MP:0001146을 포함하는 유의한 phenotype만 추출
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# 유전자 단위로 MP:0001146을 측정했지만 유의하지 않았던 유전자 추출
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **지정한 MP ID의 하위 용어도 포함됩니다.**  
> 예: `MP:0001146 (abnormal testis morphology)`를 지정하면 `MP:0004849 (abnormal testis size)` 같은 하위 용어도 포함됩니다.

### phenotype 수로 필터(`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

유전자 또는 유전자 쌍을 phenotype 수로 필터합니다. `--min` 또는 `--max` 중 하나는 필수입니다.

#### `-g`, `--genewise`
유전자별 유의한 phenotype 수로 필터합니다. `genewise_phenotype_annotations.jsonl(.gz)`를 위한 `-a/--genewise_annotations`가 필요합니다.

#### `-p`, `--pairwise`
유전자 쌍의 공유 phenotype 수로 필터합니다. `--in`을 생략하면 STDIN에서 `pairwise_similarity_annotations.jsonl(.gz)`를 읽습니다.

#### `--min MIN`, `--max MAX`
phenotype 수의 하한/상한. 한쪽만 지정해도 됩니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise 주석 파일(JSONL/.gz) 경로. `--genewise`에서 필수입니다.

- 유전자 쌍의 공유 phenotype 수:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- 유전자별 phenotype 수(genewise 필요):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

`--min` 또는 `--max` 중 하나만 사용해도 됩니다.

### 유사도 점수로 필터(`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

`phenotype_similarity_score`(0–100)로 유전자 쌍을 필터합니다. `--min` 또는 `--max` 중 하나는 필수입니다.

#### `--min MIN`, `--max MAX`
점수 하한/상한. 한쪽만 지정해도 됩니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

`--min` 또는 `--max` 중 하나만 사용해도 됩니다.

### 유전자 목록으로 필터(`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
텍스트 파일로 지정한 유전자를 포함하는 쌍만 유지합니다.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
텍스트 파일로 지정한 유전자를 포함하는 쌍을 제거합니다.

#### `-g`, `--genewise`
사용자 지정 유전자 심볼로 필터합니다.

#### `-p`, `--pairwise`
사용자 지정 유전자 쌍으로 필터합니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

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

### 생애 단계로 필터(`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
지정한 생애 단계(`Embryo`, `Early`, `Interval`, `Late`)만 유지합니다.

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
지정한 생애 단계를 제거합니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### 성별로 필터(`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
지정한 성별(`Male`, `Female`, `None`)만 유지합니다.

#### `-d SEX`, `--drop SEX`
지정한 성별을 제거합니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### 접합형으로 필터(`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
지정한 접합형(`Homo`, `Hetero`, `Hemi`)만 유지합니다.

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
지정한 접합형을 제거합니다.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### GraphML / webapp 내보내기
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise 주석 파일(JSONL/.gz) 경로. 필수입니다.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise 주석 파일(JSONL/.gz) 경로. 생략 시 STDIN에서 읽습니다.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise 주석 파일(JSONL/.gz) 경로. 필수입니다.

#### `-o OUT`, `--out OUT`
웹앱 번들(HTML/CSS/JS + 네트워크 데이터) 출력 디렉터리. 확장자가 있는 파일명은 지정하지 마세요.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

CLI는 STDIN/STDOUT을 지원하므로 파이프로 연결할 수 있습니다:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 표현형 유사 유전자군 계산

## 데이터 소스
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results)의 `statistical-results-ALL.csv.gz` 사용.  
열 정보: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 전처리
KO 마우스의 P값(`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`)이 0.0001 이하인 유전자–표현형을 추출합니다.  
- Zygosity: `homo`, `hetero`, `hemi`  
- Sex: `female`, `male`

## 표현형 유사도
TSUMUGI는 현재 Phenodigm과 유사한 접근을 사용합니다. MP용어 간 **Resnik 유사도**와 조상 집합의 **Jaccard 유사도**를 계산한 뒤 **기하평균**으로 결합합니다. 원래 Phenodigm과의 핵심 차이는 메타데이터(zygosity, life stage, sexual dimorphism) 일치도에 따른 가중치를 적용한다는 점입니다.

1. MP 온톨로지를 구축하고 정보량(IC) 계산:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   IC 하위 5퍼센타일 용어는 0으로 설정합니다.
2. 각 MP 용어 쌍에서 가장 특이한 공통 조상(MICA)을 찾고 그 IC를 Resnik으로 사용합니다.  
   조상 집합의 Jaccard 지수를 계산합니다.  
   용어 쌍 유사도 = `sqrt(Resnik * Jaccard)`.
3. 각 유전자 쌍에 대해 용어×용어 유사도 행렬을 만들고 메타데이터 가중치를 적용합니다.  
   zygosity/라이프스테이지/성적 이형 일치 수(0/1/2/3)에 대해 0.25/0.5/0.75/1.0을 부여합니다.
4. Phenodigm 방식으로 0–100 정규화를 적용합니다:  
   행/열 최대값에서 실제 max/mean을 구하고 IC 기반 이론 max/mean으로 정규화합니다.  
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   이론 분모가 0이면 0으로 둡니다.

# ✉️ 문의
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

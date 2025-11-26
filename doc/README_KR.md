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

### 1. 표현형(Phenotype)
관심 있는 표현형을 입력하면, 그 표현형을 보이는 KO 마우스 유전자의 집합 중에서 **다른 표현형도 유사한 유전자 군**을 탐색합니다.  
표현형 이름은 [Mammalian Phenotype Ontology(MPO)](https://www.informatics.jax.org/vocab/mp_ontology)를 따릅니다.  
👉 [표현형 목록](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. 유전자명(Gene)
유전자 하나를 지정하면, **그 KO 마우스와 표현형이 비슷한 다른 유전자 군**을 탐색합니다.  
유전자 명칭은 [MGI](http://www.informatics.jax.org/) 기호를 따릅니다.  
👉 [유전자 목록](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. 유전자 리스트(Gene List)
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
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 유전자 쌍(`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`(라이프 스테이지, 접합형, 성별 등 공유 표현형 메타데이터)  
- `phenotype_similarity_score`(Resnik 기반 Phenodigm 점수, 0–100)

예시:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 네트워크

입력에 따라 페이지가 전환되고 네트워크가 자동으로 그려집니다.

> [!IMPORTANT]  
> **공유하는 이상 표현형이 3개 이상이고 표현형 유사도가 0.0보다 큰** 유전자 쌍이 시각화 대상입니다.

### 네트워크 패널
**노드**는 유전자를 나타냅니다. 클릭하면 KO 마우스에서 관찰된 이상 표현형 리스트를 표시하며, 드래그로 위치를 조정할 수 있습니다.  
**엣지**를 클릭하면 공유 표현형의 상세를 볼 수 있습니다.

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

# 🛠 커맨드라인 버전

이번 릴리스에서 **CLI**가 추가되었습니다. 최신 IMPC 데이터를 받아 스스로 파이프라인을 실행하고, Web보다 세밀한 필터·출력 옵션을 적용할 수 있습니다.

- IMPC `statistical-results-ALL.csv.gz`(및 옵션 `mp.obo`, `impc_phenodigm.csv`)로 재계산  
- MP 용어 포함/제외 필터  
- 유전자 리스트(쉼표 구분 또는 텍스트 파일)로 필터  
- 출력: GraphML(`tsumugi build-graphml`), 오프라인 웹앱 번들(`tsumugi build-webapp`)

## 사용 가능한 명령
- `tsumugi run`: IMPC 데이터에서 네트워크 재계산  
- `tsumugi mp --include/--exclude`: MP 용어 포함/미표시 쌍 필터  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: 표현형 개수로 필터(쌍/유전자)  
- `tsumugi genes --keep/--drop`: 유전자 리스트로 유지/제거  
- `tsumugi life-stage --keep/--drop`: 라이프 스테이지 필터  
- `tsumugi sex --keep/--drop`: 성별 필터  
- `tsumugi zygosity --keep/--drop`: 접합형 필터  
- `tsumugi build-graphml`: GraphML 생성  
- `tsumugi build-webapp`: TSUMUGI 웹앱 자산 생성

## 설치
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
`tsumugi --version`이 출력되면 준비 완료입니다.

## 대표 사용 예(명령별)

### 1. IMPC 데이터로 네트워크 재계산(`tsumugi run`)
`--mp_obo`를 생략하면 동봉된 `data-version: releases/2025-08-27/mp.obo`를 사용합니다.  
`--impc_phenodigm`을 생략하면 2025-10-01에 [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)에서 받은 파일을 사용합니다.
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
출력: `./tsumugi-output`에 genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz, 시각화 자산(`TSUMUGI-webapp`)이 생성됩니다.

> [!IMPORTANT]  
> `TSUMUGI-webapp`에는 OS별 실행 스크립트가 포함되어 있으며, 더블클릭으로 로컬 웹앱을 열 수 있습니다.  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. MP 용어로 필터(`tsumugi mp --include/--exclude`)
```bash
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl
```

### 3. 표현형 개수로 필터(`tsumugi n-phenos`)
- 유전자 쌍의 공유 표현형 수:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 유전자별 표현형 수(genewise 필요):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` 또는 `--max` 단독 지정도 가능합니다.

### 4. 유전자 리스트로 필터(`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. 라이프 스테이지로 필터(`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### 6. 성별로 필터(`tsumugi sex --keep/--drop`)
```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### 7. 접합형으로 필터(`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### 8. GraphML / 웹앱을 생성
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

CLI는 표준입력/출력을 지원하므로, `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`처럼 파이프 연결도 가능합니다.

# 🔍 표현형 유사 유전자군 계산

## 데이터 소스
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results)의 `statistical-results-ALL.csv.gz` 사용.  
열 정보: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 전처리
KO 마우스의 P값(`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`)이 0.0001 이하인 유전자–표현형을 추출합니다.  
- Zygosity: `homo`, `hetero`, `hemi`  
- Sex: `female`, `male`

## 표현형 유사도
MP 용어 간 **Resnik 유사도**를 계산하고, 유전자 쌍을 **Phenodigm(0–100)**으로 스케일링합니다.

1. MP 온톨로지를 구축하고 정보량(IC) 계산:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(두 용어) = 가장 정보량이 큰 공통조상(MICA)의 IC(공통조상 없으면 0).  
3. 유전자 쌍: 유의한 MP 용어 간 Resnik 점수를 zygosity/라이프스테이지/성별 일치도(1.0/0.75/0.5/0.25)로 가중.  
4. 실제 max/mean을 이론적 max/mean으로 정규화 후 평균:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   이론 분모가 0이면 0으로 둡니다. 0–100 점수는 다운로드와 `Phenotypes similarity` 슬라이더에 사용됩니다.

# ✉️ 문의
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

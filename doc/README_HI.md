> ⚠️ यह AI द्वारा生成 किया गया अनुवाद है; यदि कोई疑問 हो तो मूल (README.md) देखें।  
> मूल: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** [IMPC](https://www.mousephenotype.org/) के KO माउस फेनोटाइप डेटा से **फेनोटाइपिक समानता के आधार पर जीन मॉड्यूल निकालने और दृश्य बनाने** का वेब टूल है।  
यह वेब पर सभी के लिए उपलब्ध है👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI(紡ぎ)** का अर्थ है “फेनोटाइप बनाने वाले जीन समूह को धागे की तरह बुनना”।

# 📖 TSUMUGI कैसे उपयोग करें

TSUMUGI तीन तरह के इनपुट का समर्थन करता है।

### 1. फेनोटाइप (Phenotype)
रुचि का फेनोटाइप दर्ज करें ताकि उस फेनोटाइप को दिखाने वाले KO माउस में **कुल मिलाकर समान फेनोटाइप वाले जीन समूह** मिलें।  
फेनोटाइप नाम [MPO](https://www.informatics.jax.org/vocab/mp_ontology) पर आधारित हैं।  
👉 [फेनोटाइप सूची](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. जीन (Gene)
एक जीन दें और **समान KO फेनोटाइप वाले अन्य जीन समूह** खोजें।  
जीन प्रतीक [MGI](http://www.informatics.jax.org/) के अनुरूप हैं।  
👉 [जीन सूची](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. जीन सूची (Gene List)
एकाधिक जीन (प्रति पंक्ति एक) दें और **सूची के भीतर** समान फेनोटाइप खोजें।  
> [!CAUTION]  
> यदि कोई समान जीन नहीं मिला: `No similar phenotypes were found among the entered genes.`  
> यदि 200 से अधिक मिले: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 कच्चा डेटा डाउनलोड
TSUMUGI gzip-कंप्रेस्ड JSONL प्रकाशित करता है।

#### `genewise_phenotype_annotations.jsonl.gz`
- जीन प्रतीक (जैसे "1110059G10Rik")  
- Marker accession ID (जैसे "MGI:1913452")  
- फेनोटाइप नाम/ID (जैसे "fused joints", "MP:0000137")  
- Effect size (जैसे 0.0, 1.324)  
- Significance (True/false)  
- Zygosity ("Homo", "Hetero", "Hemi")  
- Life stage ("Embryo", "Early", "Interval", "Late")  
- Sexual dimorphism ("", "Male", "Female")  
- Disease annotation (जैसे [] या "Premature Ovarian Failure 18")

उदाहरण:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- जीन युग्म (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (जीवन चरण, zygosity, यौन द्विरूपता जैसे मेटाडेटा)  
- `phenotype_similarity_score` (Resnik-आधारित Phenodigm स्कोर, 0–100)

उदाहरण:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 नेटवर्क

इनपुट के आधार पर पेज स्थानांतरित होकर नेटवर्क स्वतः बनता है।

> [!IMPORTANT]  
> **3 या अधिक साझा असामान्य फेनोटाइप** तथा **फेनोटाइप समानता > 0.0** वाले जीन युग्म दृश्य में दिखते हैं।

### नेटवर्क पैनल
**नोड** जीन दर्शाते हैं। क्लिक पर KO माउस में देखे गए असामान्य फेनोटाइप सूची दिखती है; ड्रैग से स्थान समायोजित करें।  
**एज** क्लिक पर साझा फेनोटाइप का विवरण दिखता है।

### कंट्रोल पैनल
बाएँ 패널 से नेटवर्क 표시 को समायोजित करें।

#### फेनोटाइप समानता से फ़िल्टर
`Phenotypes similarity` स्लाइडर Resnik→Phenodigm स्कोर से एज의 임계값을 설정합니다。  
> 계산 방법: 👉 [🔍 표현형 유사 유전자군 계산](#-표현형-유사-유전자군-계산)

#### फेनोटाइप गंभीरता से 필्टर
`Phenotype severity` स्लाइडर KO माउस में 효과량(중증도)으로 노드 필터링합니다。값이 클수록 영향이 큽니다。  
> 이진 표현형(예: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); 이진 목록은 [여기](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt))나 단일 유전자 입력 시에는 숨겨집니다。

#### Genotype 지정
- `Homo`(동형접합)
- `Hetero`(이형접합)
- `Hemi`(반측접합)

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
IMPC Disease Models Portal 데이터로 질병 관련 유전자를 하이라이트합니다。

#### Search: Specific Gene
네트워크에서 유전자명을 검색합니다。

#### Layout & Display
레이아웃, 폰트 크기, 엣지 두께, 노드 반발력(Cose 레이아웃) 조정。

#### Export
PNG/CSV/GraphML로 내보낼 수 있습니다。  
CSV에는 모듈ID와 각 유전자 표현형 리스트가 포함되고, GraphML은 Cytoscape 호환입니다。

# 🛠 커맨드라인 버전

이번 릴리스에서 **CLI**를 추가했습니다。최신 IMPC 데이터를 받아 스스로 파이프라인을 실행하고, 웹보다 더 세밀한 필터와 출력 옵션을 적용할 수 있습니다。

- IMPC `statistical-results-ALL.csv.gz`(옵션 `mp.obo`, `impc_phenodigm.csv`)로 재계산  
- MP 용어 포함/제외 필터  
- 유전자 리스트(쉼표 또는 텍스트 파일)로 필터  
- 출력: GraphML(`tsumugi build-graphml`), 오프라인 웹앱 번들(`tsumugi build-webapp`)

## 사용 가능한 명령
- `tsumugi run`: IMPC 데이터로 네트워크 재계산  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: MP 용어 기준으로 페어 또는 유전자 단위 필터  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: 표현형 수로 필터(페어/유전자)  
- `tsumugi genes --keep/--drop`: 유전자 리스트로 유지/삭제  
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
`tsumugi --version`이 보이면 준비 완료입니다。

## 주요 사용 예(명령별)

### 1. IMPC 데이터로 재계산(`tsumugi run`)
`--mp_obo`를 생략하면 동봉된 `data-version: releases/2025-08-27/mp.obo`를 사용합니다。  
`--impc_phenodigm`을 생략하면 2025-10-01에 IMPC Disease Models Portal에서 받은 파일을 사용합니다。
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
출력: `./tsumugi-output`에 genewise/pairwise JSONL과 `TSUMUGI-webapp`이 생성됩니다。

> [!IMPORTANT]  
> `TSUMUGI-webapp`에는 OS별 실행 스크립트가 포함되어 있습니다。더블클릭으로 로컬 웹앱을 열 수 있습니다。  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. MP 용어 필터(`tsumugi mp --include/--exclude`)
관심 있는 표현형을 가진 유전자 페어만 추출하거나, 해당 표현형을 측정했지만 유의한 이상이 없었던 유전자 페어를 추출할 수 있습니다。

- `--pairwise`(기본값): 유전자 페어 단위 출력. `--in pairwise_similarity_annotations.jsonl(.gz)`를 전달합니다.
- `--genewise`: 유전자 단위 출력. `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)`를 사용합니다(`--exclude` 필수, `--include` 권장).

```bash
# MP:0001146(abnormal testis morphology)와 그 하위 표현형(MP:0004849 (abnormal testis size) 등)을 포함하는 유전자 페어만 추출
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# MP:0001146(abnormal testis morphology)와 그 하위 표현형(MP:0004849 (abnormal testis size) 등)을 측정했지만 유의한 이상이 없었던 유전자 페어를 추출
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# MP:0001146(하위 포함)을 갖는 유의한 유전자 단위 주석만 추출
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# MP:0001146(하위 포함)을 측정했으나 유의하지 않았던 유전자 추출
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **지정한 MP 용어의 하위 용어도 함께 처리됩니다.**  
> 예를 들어 `MP:0001146 (abnormal testis morphology)`를 지정하면 `MP:0004849 (abnormal testis size)` 등의 하위 용어도 고려됩니다。

### 3. 표현형 수 필터(`tsumugi n-phenos`)
- 페어당 공유 표현형:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 유전자별 표현형( genewise 필요 ):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` 또는 `--max` 단독 사용도 가능합니다。

### 4. 유전자 리스트 필터(`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. 라이프 스테이지 / 성별 / 접합형
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### 6. GraphML / 웹앱 생성
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

파이프 예: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 동일 표현형 유전자군 계산

## 데이터 소스
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
필드: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 전처리
P ≤ 0.0001(`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`)인 유전자–표현형 추출  
- Zygosity: `homo`, `hetero`, `hemi`  
- Sex: `female`, `male`

## 표현형 유사도
MP 용어 간 **Resnik** 유사도를 계산하고, **Phenodigm(0–100)**으로 스케일링합니다。

1. MP 온톨로지 구축, IC 계산: `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = 가장 정보가 큰 공통 조상(MICA)의 IC(없으면 0)  
3. 유전자 쌍: zygosity/라이프스테이지/성별 일치도(1.0/0.75/0.5/0.25)로 가중  
4. 실제 max/mean을 이론적 max/mean으로 나눈 뒤 평균:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   분모 0이면 0으로 설정. 0–100 점수는 다운로드 및 `Phenotypes similarity` 슬라이더에 사용됩니다。

# ✉️ 연락
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


## CLI option details (updated)

### 2. Filter by MP term (`tsumugi mp --include/--exclude`)
```
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m MP_OBO] [-a GENEWISE_ANNOTATIONS] [--in IN] [--out OUT] [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```
- `-i/--include`: include specified MP term (descendants included)
- `-e/--exclude`: measured for the term but no significant phenotype (descendants included); requires `-a/--genewise_annotations`
- `-g/--genewise`: gene-level filtering; specify `-a/--genewise_annotations`
- `-p/--pairwise`: pairwise filtering; if `--in` is omitted, reads from STDIN
- `-m/--mp_obo`: path to mp.obo; defaults to bundled file if omitted
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz)
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT
- `--life_stage`: filter by life stage (`Embryo`, `Early`, `Interval`, `Late`)
- `--sex`: filter by sexual dimorphism (`Male`, `Female`, `None`)
- `--zygosity`: filter by zygosity (`Homo`, `Hetero`, `Hemi`)

### 3. Filter by phenotype counts (`tsumugi n-phenos`)
```
tsumugi n-phenos [-h] (-g | -p) [--min MIN] [--max MAX] [--in IN] [--out OUT] [-a GENEWISE_ANNOTATIONS]
```
- `-g/--genewise`: per-gene counts; requires `-a/--genewise_annotations`
- `-p/--pairwise`: shared phenotype counts per pair; if `--in` omitted, reads from STDIN
- `--min/--max`: thresholds (at least one required)
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required with `--genewise`

### 4. Filter by gene list (`tsumugi genes --keep/--drop`)
```
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only pairs containing specified genes (comma-separated or text file)
- `-d/--drop`: drop pairs containing specified genes
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 5. Filter by life stage (`tsumugi life-stage --keep/--drop`)
```
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified life stage (`Embryo`, `Early`, `Interval`, `Late`)
- `-d/--drop`: drop the specified life stage
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 6. Filter by sex (`tsumugi sex --keep/--drop`)
```
tsumugi sex [-h] (-k SEX | -d SEX) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified sex (`Male`, `Female`, `None`)
- `-d/--drop`: drop the specified sex
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 7. Filter by zygosity (`tsumugi zygosity --keep/--drop`)
```
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified zygosity (`Homo`, `Hetero`, `Hemi`)
- `-d/--drop`: drop the specified zygosity
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 8. Export GraphML / webapp
```
tsumugi build-graphml [-h] [--in IN] -a GENEWISE_ANNOTATIONS
```
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required
```
tsumugi build-webapp [-h] [--in IN] -a GENEWISE_ANNOTATIONS -o OUT
```
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required
- `-o/--out`: output directory for the webapp bundle (do not pass a filename with extension)

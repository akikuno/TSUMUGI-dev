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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** [IMPC](https://www.mousephenotype.org/) के KO माउस फेनोटाइप डेटा से **फेनोटाइपिक समानता के आधार पर जीन मॉड्यूल निकालने और दृश्य बनाने** का वेब टूल है।  
यह वेब पर सभी के लिए उपलब्ध है👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI(紡ぎ)** का अर्थ है “फेनोटाइप बनाने वाले जीन समूह को धागे की तरह बुनना”।

# 📖 TSUMUGI कैसे उपयोग करें

TSUMUGI तीन तरह के इनपुट का समर्थन करता है।

### फेनोटाइप (Phenotype)
रुचि का फेनोटाइप दर्ज करें ताकि उस फेनोटाइप को दिखाने वाले KO माउस में **कुल मिलाकर समान फेनोटाइप वाले जीन समूह** मिलें।  
फेनोटाइप नाम [MPO](https://www.informatics.jax.org/vocab/mp_ontology) पर आधारित हैं।  
👉 [फेनोटाइप सूची](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### जीन (Gene)
एक जीन दें और **समान KO फेनोटाइप वाले अन्य जीन समूह** खोजें।  
जीन प्रतीक [MGI](http://www.informatics.jax.org/) के अनुरूप हैं।  
👉 [जीन सूची](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### जीन सूची (Gene List)
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
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- जीन युग्म (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (जीवन चरण, zygosity, यौन द्विरूपता जैसे मेटाडेटा)  
- `phenotype_similarity_score` (Resnik-आधारित Phenodigm स्कोर, 0–100)

उदाहरण:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 नेटवर्क

इनपुट के आधार पर पेज स्थानांतरित होकर नेटवर्क स्वतः बनता है।

> [!IMPORTANT]  
> **3 या अधिक साझा असामान्य फेनोटाइप** तथा **फेनोटाइप समानता > 0.0** वाले जीन युग्म दृश्य में दिखते हैं।

### नेटवर्क पैनल
**नोड** जीन दर्शाते हैं। क्लिक पर KO माउस में देखे गए असामान्य फेनोटाइप सूची दिखती है; ड्रैग से स्थान समायोजित करें।  
**एज** क्लिक पर साझा फेनोटाइप का विवरण दिखता है।
**Modules** outline gene subnetworks. Click a module to list phenotypes of its genes; drag modules to reposition and avoid overlap.

### कंट्रोल पैनल
बाएँ पैनल से नेटवर्क का प्रदर्शन समायोजित करें।

#### फेनोटाइप समानता से फ़िल्टर
`Phenotypes similarity` स्लाइडर Resnik→Phenodigm स्कोर के आधार पर edges का threshold सेट करता है。  
> गणना विधि: 👉 [🔍 समान फेनोटाइप वाले जीन समूह की गणना](#-समान-फेनोटाइप-वाले-जीन-समूह-की-गणना)

#### फेनोटाइप गंभीरता से फ़िल्टर
`Phenotype severity` स्लाइडर KO माउस में प्रभाव आकार (severity) के आधार पर नोड्स को फ़िल्टर करता है。 मान जितना बड़ा होगा, प्रभाव उतना अधिक होगा。  
> द्विआधारी फेनोटाइप (उदाहरण: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); द्विआधारी सूची: [यहाँ](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) या एकल जीन इनपुट पर यह छिपा रहता है。

#### Genotype निर्दिष्ट करें
- `Homo`(समयुग्मजी)
- `Hetero`(विषमयुग्मजी)
- `Hemi`(अर्धयुग्मजी)

#### लिंग निर्दिष्ट करें
- `Female`
- `Male`

#### जीवन चरण निर्दिष्ट करें
- `Embryo`
- `Early`(0–16 सप्ताह)
- `Interval`(17–48 सप्ताह)
- `Late`(49 सप्ताह से अधिक)

### मार्कअप पैनल
#### Highlight: Human Disease
IMPC Disease Models Portal डेटा से रोग-संबंधित जीन को हाइलाइट करता है。

#### Search: Specific Gene
नेटवर्क में जीन नाम खोजें。

#### Layout & Display
लेआउट, फ़ॉन्ट आकार, एज की मोटाई, और नोड प्रतिकर्षण (Cose लेआउट) समायोजित करें。

#### Export
PNG/CSV/GraphML में निर्यात कर सकते हैं。  
CSV में मॉड्यूल ID और प्रत्येक जीन की फेनोटाइप सूची शामिल होती है, और GraphML Cytoscape संगत है。

# 🛠 कमांड-लाइन इंटरफ़ेस

TSUMUGI CLI आपको स्थानीय रूप से डाउनलोड किए गए नवीनतम IMPC डेटा का उपयोग करने देता है और वेब टूल से अधिक सूक्ष्म फ़िल्टरिंग/आउटपुट विकल्प प्रदान करता है।

## विशेषताएँ

- IMPC `statistical-results-ALL.csv.gz` से पुनः गणना (वैकल्पिक `mp.obo`, `impc_phenodigm.csv`).  
- MP शब्दों की उपस्थिति/अनुपस्थिति पर फ़िल्टर।  
- जीन सूची से फ़िल्टर (कॉमा-सेपरेटेड या टेक्स्ट फ़ाइल)।  
- आउटपुट: GraphML (`tsumugi build-graphml`), ऑफ़लाइन webapp बंडल (`tsumugi build-webapp`).

## इंस्टॉलेशन

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

`tsumugi --version` से वर्ज़न दिखे तो आप तैयार हैं।

## उपलब्ध कमांड

- `tsumugi run`: IMPC डेटा से नेटवर्क पुनः गणना  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: MP शब्दों को शामिल/बहिष्कृत करने वाले gene pairs या genes फ़िल्टर करें  
- `tsumugi count --pairwise/--genewise (--min/--max)`: phenotype गिनती के आधार पर फ़िल्टर (pairs/genes)  
- `tsumugi score (--min/--max)`: phenotype similarity score पर फ़िल्टर (pairs)  
- `tsumugi genes --keep/--drop`: gene list से keep/drop (कॉमा या टेक्स्ट फ़ाइल)  
- `tsumugi life-stage --keep/--drop`: life stage फ़िल्टर (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: sex फ़िल्टर (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: zygosity फ़िल्टर (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: GraphML बनाएँ (Cytoscape आदि)  
- `tsumugi build-webapp`: TSUMUGI webapp assets बनाएं (स्थानीय HTML/CSS/JS)

> [!NOTE]
> सभी फ़िल्टरिंग सबकमांड JSONL को STDOUT पर स्ट्रीम करते हैं।  
> फ़ाइल में सेव करने के लिए `>` से रीडायरेक्ट करें।

> [!IMPORTANT]
> `tsumugi run` को छोड़कर सभी कमांड को `pairwise_similarity_annotation.jsonl.gz` या `genewise_phenotype_annotation.jsonl.gz` चाहिए।
> दोनों फाइलें [TSUMUGI शीर्ष पृष्ठ](https://larc-tsukuba.github.io/tsumugi/) से डाउनलोड की जा सकती हैं।

## उपयोग

### IMPC डेटा से पुनः गणना (`tsumugi run`)
अगर `--mp_obo` छोड़ा गया है, TSUMUGI bundled `data-version: releases/2025-08-27/mp.obo` का उपयोग करता है।  
अगर `--impc_phenodigm` छोड़ा गया है, यह 2025-10-01 को [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/) से प्राप्त फ़ाइल का उपयोग करता है।
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
आउटपुट: `./tsumugi-output` में genewise annotations (genewise_phenotype_annotations.jsonl.gz), pairwise similarity data (pairwise_similarity_annotations.jsonl.gz) और visualization assets (`TSUMUGI-webapp`) शामिल हैं।

> [!IMPORTANT]  
> `TSUMUGI-webapp` डायरेक्टरी में OS-विशिष्ट launch scripts शामिल हैं; डबल-क्लिक करके लोकल webapp खोलें:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### MP term से फ़िल्टर (`tsumugi mp --include/--exclude`)
रुचि के phenotypes शामिल करने वाले gene pairs (या genes) निकालें, या ऐसे pairs जिनमें वे phenotypes मापे गए लेकिन significant abnormality नहीं मिली।

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
निर्दिष्ट MP term वाले genes/gene pairs शामिल करें (descendants सहित)।

#### `-e MP_ID`, `--exclude MP_ID`
निर्दिष्ट MP term (descendants सहित) के लिए मापे गए genes/gene pairs लौटाएँ जिनमें significant phenotype नहीं दिखा। `-a/--genewise_annotations` आवश्यक है।

#### `-g`, `--genewise`
gene स्तर पर फ़िल्टर। `genewise_phenotype_annotations.jsonl(.gz)` पढ़ता है। `--genewise` के साथ `-a/--genewise_annotations` दें।

#### `-p`, `--pairwise`
pair स्तर पर फ़िल्टर। लक्ष्य `pairwise_similarity_annotations.jsonl(.gz)` है। `--in` न देने पर STDIN से पढ़ता है।

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Mammalian Phenotype ontology (mp.obo) का पाथ। छोड़ने पर bundled `data/mp.obo` इस्तेमाल होता है।

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise annotation फ़ाइल (JSONL/.gz) का पाथ। `--exclude` के लिए आवश्यक; `--genewise` में भी दें।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

#### `--life_stage LIFE_STAGE`
life stage के आधार पर अतिरिक्त फ़िल्टर। मान: `Embryo`, `Early`, `Interval`, `Late`।

#### `--sex SEX`
sexual dimorphism के आधार पर अतिरिक्त फ़िल्टर। annotations में मौजूद मान (जैसे `Male`, `Female`, `None`) उपयोग करें।

#### `--zygosity ZYGOSITY`
zygosity के आधार पर अतिरिक्त फ़िल्टर। मान: `Homo`, `Hetero`, `Hemi`।

```bash
# MP:0001146 (abnormal testis morphology) या उसके descendants (जैसे MP:0004849 abnormal testis size) वाले gene pairs निकालें
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# MP:0001146 और descendants मापे गए थे लेकिन significant abnormality नहीं दिखी
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# gene स्तर पर MP:0001146 वाले significant phenotypes निकालें
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# gene स्तर पर MP:0001146 (descendants सहित) मापा गया लेकिन significant नहीं था
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **निर्दिष्ट MP ID के descendant terms भी शामिल होते हैं।**  
> उदाहरण के लिए, `MP:0001146 (abnormal testis morphology)` देने पर `MP:0004849 (abnormal testis size)` जैसे descendants भी शामिल होंगे।

### phenotype counts से फ़िल्टर (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

genes या gene pairs को phenotype संख्या के आधार पर फ़िल्टर करता है। कम से कम `--min` या `--max` चाहिए।

#### `-g`, `--genewise`
प्रत्येक gene के significant phenotype count पर फ़िल्टर। `genewise_phenotype_annotations.jsonl(.gz)` के लिए `-a/--genewise_annotations` आवश्यक है।

#### `-p`, `--pairwise`
प्रत्येक pair के shared phenotype count पर फ़िल्टर। `--in` न देने पर STDIN से पढ़ता है।

#### `--min MIN`, `--max MAX`
phenotype count की lower/upper सीमा। एक सीमा भी पर्याप्त है।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise annotation फ़ाइल (JSONL/.gz) का पाथ। `--genewise` के साथ आवश्यक।

- pairwise shared phenotype counts:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- gene-level phenotype counts (genewise आवश्यक):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

`--min` या `--max` में से केवल एक भी ठीक है।

### similarity score से फ़िल्टर (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

`phenotype_similarity_score` (0–100) के आधार पर gene pairs फ़िल्टर करता है। कम से कम `--min` या `--max` चाहिए।

#### `--min MIN`, `--max MAX`
score की lower/upper सीमा। एक सीमा भी पर्याप्त है।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

`--min` या `--max` में से केवल एक भी ठीक है।

### gene list से फ़िल्टर (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
टेक्स्ट फ़ाइल में दिए गए genes को शामिल करने वाले pairs ही रखें।

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
टेक्स्ट फ़ाइल में दिए गए genes वाले pairs हटाएँ।

#### `-g`, `--genewise`
यूज़र द्वारा दिए गए gene symbols पर फ़िल्टर।

#### `-p`, `--pairwise`
यूज़र द्वारा दिए गए gene pairs पर फ़िल्टर।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

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

### life stage से फ़िल्टर (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
निर्दिष्ट life stage (`Embryo`, `Early`, `Interval`, `Late`) ही रखें।

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
निर्दिष्ट life stage हटाएँ।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### sex से फ़िल्टर (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
निर्दिष्ट sex (`Male`, `Female`, `None`) ही रखें।

#### `-d SEX`, `--drop SEX`
निर्दिष्ट sex हटाएँ।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### zygosity से फ़िल्टर (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
निर्दिष्ट zygosity (`Homo`, `Hetero`, `Hemi`) ही रखें।

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
निर्दिष्ट zygosity हटाएँ।

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### GraphML / webapp एक्सपोर्ट
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise annotation फ़ाइल (JSONL/.gz) का पाथ। आवश्यक।

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise annotation फ़ाइल (JSONL/.gz) का पाथ। न देने पर STDIN से पढ़ता है।

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise annotation फ़ाइल (JSONL/.gz) का पाथ। आवश्यक।

#### `-o OUT`, `--out OUT`
webapp bundle (HTML/CSS/JS + नेटवर्क डेटा) का आउटपुट डायरेक्टरी। एक्सटेंशन वाला फ़ाइल नाम न दें।

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

CLI STDIN/STDOUT सपोर्ट करता है, इसलिए आप कमांड चेन कर सकते हैं:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 समान फेनोटाइप वाले जीन समूह की गणना

## डेटा स्रोत

हम IMPC डेटासेट [Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz` का उपयोग करते हैं।  
डेटासेट कॉलम जानकारी: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## प्रीप्रोसेसिंग

KO माउस P-value (`p_value`, `female_ko_effect_p_value` या `male_ko_effect_p_value`) ≤ 0.0001 वाले gene–phenotype pairs निकाले जाते हैं।  
- genotype-विशिष्ट phenotypes को `homo`, `hetero` या `hemi` के रूप में annotate किया जाता है।  
- sex-विशिष्ट phenotypes को `female` या `male` के रूप में annotate किया जाता है।

## Phenotypic similarity

TSUMUGI Phenodigm-जैसी पद्धति अपनाता है ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)).  

> [!NOTE]
> मूल Phenodigm से अंतर निम्न हैं।  
> 1. **IC के 5वें परसेंटाइल से नीचे के terms को IC=0 पर सेट किया जाता है, ताकि बहुत सामान्य phenotypes (उदाहरण: embryo phenotype) का मूल्यांकन न हो।**
> 2. **genotype, life stage और sex के metadata matches पर आधारित weighting लागू किया जाता है।**

### 1. MP term-pair similarity की परिभाषा

* MP ontology बनाकर हर term का Information Content (IC) निकाला जाता है:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   IC के 5वें परसेंटाइल से नीचे के terms को IC=0 पर सेट किया जाता है।

* प्रत्येक MP term pair के लिए सबसे विशिष्ट common ancestor (MICA) निकाला जाता है और उसका IC Resnik similarity माना जाता है।  

* दो MP terms के ancestor सेट का Jaccard index निकाला जाता है।  

* MP term-pair similarity को `sqrt(Resnik * Jaccard)` के रूप में परिभाषित किया जाता है।

### 2. phenotype metadata match के आधार पर weighting

* genotype, life stage और sex जैसे phenotype metadata के अनुसार weights लागू किए जाते हैं।

* हर gene pair के लिए MP term × MP term similarity matrix बनाया जाता है।  

* genotype/life stage/sex के 0, 1, 2, 3 matches के लिए weights 0.2, 0.5, 0.75, 1.0 लगाए जाते हैं।

### 3. Phenodigm scaling

* Phenodigm-टाइप scaling से प्रत्येक KO माउस की phenotypic similarity को 0–100 में normalize किया जाता है:  
   observed max/mean निकालकर theoretical max/mean से normalize किया जाता है।  
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   यदि denominator 0 हो, तो score 0 सेट किया जाता है।

---

# ✉️ संपर्क
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 उद्धरण

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

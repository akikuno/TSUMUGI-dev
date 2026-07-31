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

यह दस्तावेज़ **TSUMUGI v1.1.1** के वर्तमान व्यवहार का वर्णन करता है। सार्वजनिक वेब ऐप IMPC **Release 24.0** डेटा का उपयोग करता है।

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
> समान genes न मिलने पर: `No similar phenotypes were found among the entered genes.`
> Gene List अधिकतम 200 अलग और उपलब्ध genes स्वीकार करता है। Counting से पहले duplicates और blank lines हटते हैं; unavailable symbols report करके बाहर किए जाते हैं। 201 या अधिक उपलब्ध genes वाली list network data load होने से पहले reject होती है।

### 📥 कच्चा डेटा डाउनलोड
TSUMUGI gzip-कंप्रेस्ड JSONL प्रकाशित करता है।

#### `genewise_phenotype_annotations.jsonl.gz`
- जीन प्रतीक (जैसे "1110059G10Rik")  
- Marker accession ID (जैसे "MGI:1913452")  
- फेनोटाइप नाम/ID (जैसे "fused joints", "MP:0000137")  
- Effect size (`number` या `null`; जैसे 0.0, 1.324)
- Significance flag (`true` IMPC abnormal-phenotype annotation के लिए; `false` significant abnormality के बिना mapped measurement के लिए)
- Zygosity ("Homo", "Hetero", "Hemi")  
- Life stage ("Embryo", "Early", "Interval", "Late")  
- Sexual dimorphism (`None`, `Male`, `Female`)
- Disease annotation (जैसे [] या "Premature Ovarian Failure 18")

उदाहरण:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- जीन युग्म (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (metadata-matched MICA contexts: MP term, life stage, zygosity और sex label)
- `phenotype_similarity_score` (Phenodigm score, 0–100)

उदाहरण:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## व्याख्या संबंधी नोट्स

- **साझा कॉन्टेक्स्ट:** `phenotype_shared_annotations` का प्रत्येक item दो significant MP annotations का सबसे अधिक सूचना वाला साझा पूर्वज (MICA) है, जिनकी zygosity, life stage और sex label समान हैं। इसका यह अर्थ आवश्यक नहीं कि दोनों genes में वही सीधे annotated terminal (leaf) MP term हो। Metadata अलग होने पर वही MICA अलग कॉन्टेक्स्ट के रूप में आ सकता है।
- **प्रदर्शन नियम:** Gene और Phenotype पेज कम से कम तीन साझा abnormal-phenotype कॉन्टेक्स्ट तथा 0 से अधिक similarity score वाले gene pairs दिखाते हैं। Gene List में दिए गए genes के बीच कम से कम एक साझा कॉन्टेक्स्ट आवश्यक है। ये केवल प्रदर्शन नियम हैं, statistical significance के मानदंड नहीं।
- **Similarity display:** वितरित `phenotype_similarity_score` 0–100 का Phenodigm score है। Web app प्रत्येक दिखाए गए network के उपलब्ध मानों को 1–100 पर फिर से scale करता है; इसलिए अलग-अलग pages के slider और tooltip मान एक समान absolute scale पर तुलना योग्य नहीं हैं।
- **Effect-size display:** TSUMUGI IMPC effect size का absolute value लेकर `log1p` लगाता है और target phenotype के मानों को 1–100 पर scale करता है। यह page के भीतर rank देखने का संकेतक है, raw effect size नहीं, और अलग phenotype pages के बीच तुलना योग्य नहीं है। Missing values JSON `null` ही रहते हैं और nodes सफेद दिखते हैं।
- **Modules:** Modules केवल visual groups हैं; वे molecular pathway या protein complex का प्रमाण नहीं हैं। `Similarity` connected components और `Top-level MP` ontology-based groups दर्शाते हैं; Gene page के soft/fuzzy modules में एक gene कई modules में हो सकता है। Module node-count filter केवल दिखने वाले modules सीमित करता है।
- **Sex labels:** `Female` का अर्थ है कि केवल female KO effect P-value ≤ 0.0001 है; `Male` का अर्थ male KO effect के लिए यही है। Web interface में दोनों विकल्प mutually exclusive हैं और formal sex×genotype interaction test का स्थान नहीं लेते।
- **Phenotype highlights:** एक ही phenotype के metadata variants को एक विकल्प में मिलाया जाता है। किसी gene पर Human Disease और एक या अधिक phenotype highlights overlap होने पर categories concentric rings के रूप में दिखती हैं।
- **Disease highlights:** IMPC Disease Models Portal की annotations model similarity का evidence हैं; वे अकेले human gene–disease causal relationship स्थापित नहीं करतीं।
- **Non-significant records:** ये उस mapped measurement को दर्शाते हैं जिसमें चुनी गई condition पर significant abnormal annotation नहीं मिली। ये animal के normal होने या phenotype के अनुपस्थित होने का प्रमाण नहीं हैं; `disease_annotation` खाली रहता है।
- **Score interpretation:** TSUMUGI score P-value, effect size, binding affinity या causal gene interaction का evidence नहीं है।

# 🌐 नेटवर्क

इनपुट के आधार पर पेज स्थानांतरित होकर नेटवर्क स्वतः बनता है।

> [!IMPORTANT]
> Gene और Phenotype पेज कम से कम तीन साझा abnormal-phenotype कॉन्टेक्स्ट तथा 0 से अधिक similarity score वाले gene pairs दिखाते हैं; Gene List में दिए गए genes के बीच कम से कम एक साझा कॉन्टेक्स्ट आवश्यक है। ये प्रदर्शन नियम हैं, statistical significance के मानदंड नहीं।

### नेटवर्क पैनल
**नोड** जीन दर्शाते हैं। क्लिक पर KO माउस में देखे गए असामान्य फेनोटाइप सूची दिखती है; ड्रैग से स्थान समायोजित करें।  
**एज** क्लिक पर साझा फेनोटाइप का विवरण दिखता है।
**Modules** outline gene subnetworks. Click a module to list phenotypes of its genes; drag modules to reposition and avoid overlap.
Gene पेज soft/fuzzy Top-level MP modules का उपयोग करते हैं, इसलिए एक gene एक से अधिक module में हो सकता है। Phenotype और Gene List पेज connected components पर आधारित `Similarity` modules और `Top-level MP` modules के बीच बदल सकते हैं।

### कंट्रोल पैनल
बाएँ पैनल से नेटवर्क का प्रदर्शन समायोजित करें।

#### फेनोटाइप समानता से फ़िल्टर
`Phenotypes similarity` दिखाए गए similarity value के आधार पर edges filter करता है। वितरित `phenotype_similarity_score` 0–100 का है, लेकिन हर दिखाए गए network में इसे 1–100 पर फिर से scale किया जाता है; अलग pages के मान सीधे तुलना योग्य नहीं हैं।
> गणना विधि: 👉 [🔍 समान फेनोटाइप वाले जीन समूह की गणना](#-समान-फेनोटाइप-वाले-जीन-समूह-की-गणना)

#### Effect size से फ़िल्टर
`Effect size` page-specific display value के आधार पर nodes filter करता है। TSUMUGI IMPC effect size का absolute value लेकर `log1p` लगाता है और target phenotype के मानों को 1–100 पर scale करता है। यह page के भीतर ranking aid है, raw effect size नहीं, और phenotype pages के बीच तुलना योग्य नहीं है।
Missing effect sizes को JSONL में standard JSON `null` के रूप में serialize किया जाता है; वे semantically missing रहते हैं, zero में नहीं बदले जाते, और संबंधित nodes सफेद दिखते हैं।
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
#### Module display
दाएँ panel में module definition और दिखाई देने वाला module चुनें। Module borders छिपाने पर network से genes या edges नहीं हटते।

#### Highlight: Phenotype
Phenotype annotation के आधार पर genes highlight करता है। एक ही phenotype के metadata variants को एक विकल्प में मिलाया जाता है। किसी gene पर Human Disease और कम से कम एक phenotype highlight overlap होने पर categories concentric rings के रूप में दिखती हैं।

#### Highlight: Human Disease
IMPC Disease Models Portal में disease-model annotations वाले KO genes highlight करता है। यह annotation model similarity का evidence है और अकेले human gene–disease causal relationship स्थापित नहीं करता।

#### Search: Specific Gene
नेटवर्क में जीन नाम खोजें。

#### Layout & Display
लेआउट, फ़ॉन्ट आकार, एज की मोटाई, और नोड प्रतिकर्षण (Cose लेआउट) समायोजित करें。

#### Export
PNG, JPG, SVG, CSV या GraphML में निर्यात कर सकते हैं। PNG, JPG और SVG में module frames शामिल किए जा सकते हैं। CSV active Similarity या Top-level MP module assignment और phenotype lists को रखता है; GraphML Cytoscape संगत है।

# 🛠 कमांड-लाइन इंटरफ़ेस

TSUMUGI CLI आपको स्थानीय रूप से डाउनलोड किए गए नवीनतम IMPC डेटा का उपयोग करने देता है और वेब टूल से अधिक सूक्ष्म फ़िल्टरिंग/आउटपुट विकल्प प्रदान करता है।

## विशेषताएँ

- IMPC `statistical-results-ALL.csv.gz` से पुनः गणना (वैकल्पिक `mp.obo`, `impc_phenodigm.csv`).  
- Significant MP annotations या mapped non-significant measurements के आधार पर फ़िल्टर।
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
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: significant MP annotations या mapped non-significant measurements के आधार पर gene pairs या genes फ़िल्टर करें
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
> `tsumugi run` को छोड़कर सभी कमांड को `pairwise_similarity_annotations.jsonl.gz` या `genewise_phenotype_annotations.jsonl.gz` चाहिए।
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
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
निर्दिष्ट MP term वाले genes/gene pairs शामिल करें (descendants सहित)।

#### `-e MP_ID`, `--exclude MP_ID`
निर्दिष्ट MP term (descendants सहित) के लिए मापे गए genes/gene pairs लौटाएँ जिनमें significant phenotype नहीं दिखा। `-a/--genewise_annotations` आवश्यक है।

> [!CAUTION]
> Non-significant record यह सिद्ध नहीं करता कि animal normal है या phenotype अनुपस्थित है। यह केवल बताता है कि mapped measurement में उस condition पर significant abnormal annotation नहीं मिली।

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
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# MP:0001146 और descendants मापे गए थे लेकिन significant abnormality नहीं दिखी
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

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
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
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
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
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

tsumugi genes --genewise --keep genes.txt   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

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
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
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
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

CLI STDIN/STDOUT सपोर्ट करता है, इसलिए आप कमांड चेन कर सकते हैं:  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 समान फेनोटाइप वाले जीन समूह की गणना

## डेटा स्रोत

हम IMPC डेटासेट [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz` का उपयोग करते हैं।
डेटासेट कॉलम जानकारी: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## प्रीप्रोसेसिंग

TSUMUGI किसी non-empty IMPC `mp_term_id` को IMPC abnormal-phenotype annotation मानता है। यह mapped measurements को भी रखता है जिनमें significant abnormal annotation नहीं मिली, ताकि measurement-aware exclusion queries की जा सकें।
Non-significant measurements के लिए `intermediate_mp_term_id` के प्रत्येक ontology-incomparable, सबसे specific non-root term को अलग record के रूप में लिखा जाता है। केवल `MP:0000001` से mapped या किसी valid MP term से mapped न होने वाले measurements को phenotype-specific query में उपयोग न कर सकने के कारण output में शामिल नहीं किया जाता।

- Zygosity को `Homo`, `Hetero` या `Hemi` में बदला जाता है।
- केवल `female_ko_effect_p_value` ≤ 0.0001 होने पर `Female`, केवल `male_ko_effect_p_value` ≤ 0.0001 होने पर `Male`, अन्यथा `None` दिया जाता है।
- Effect size का absolute value उपयोग होता है। Missing values missing ही रहती हैं और JSON में `null` के रूप में लिखी जाती हैं।

## Phenotypic similarity

TSUMUGI Mammalian Phenotype Ontology के भीतर IMPC KO mouse gene phenotype profiles की तुलना के लिए मूल PhenoDigm scoring formula ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) लागू करता है।

> [!NOTE]
> TSUMUGI PhenoDigm scoring formula का उपयोग करता है, लेकिन मूल cross-species HPO-MP/ZP OWLSim pipeline नहीं चलाता। यह IMPC KO mouse genes की MP annotations की तुलना करता है।

### 1. MP term-pair similarity की परिभाषा

* MP ontology बनाकर significant IMPC annotations से Information Content (IC) निकाला जाता है:
   `IC(term) = -log2(|term तक propagated annotations| / |सभी significant annotations|)`
   हर direct annotation को annotated MP term और उसके सभी ancestors तक propagate किया जाता है।

* प्रत्येक MP term pair के लिए सबसे अधिक annotation-derived IC वाले common ancestors खोजे जाते हैं। Tie होने पर MP ontology में सबसे कम transitive descendants वाला candidate, फिर lexicographically सबसे छोटा MP term ID deterministically चुना जाता है। चुने गए MICA का IC Resnik similarity होता है। यह tie-break similarity score या output schema नहीं बदलता।
   Tied candidates का numerical term-pair score समान रहता है, लेकिन चुना गया MICA label shared-context count और इसलिए display eligibility बदल सकता है।

* दो MP terms के inferred attribute sets का Jaccard index निकाला जाता है; प्रत्येक set में term स्वयं और उसके सभी ancestors होते हैं।

* MP term-pair similarity को `sqrt(Resnik * Jaccard)` के रूप में परिभाषित किया जाता है।

### 2. Gene-pair similarity matrix

* हर gene pair के लिए term-pair scores से MP term × MP term similarity matrix बनाया जाता है।

* MICA को `phenotype_shared_annotations` में तभी दर्ज किया जाता है जब zygosity, life stage और sex label समान हों। ये metadata PhenoDigm score को weight नहीं करते।

### 3. Phenodigm scaling

* PhenoDigm maximum/average scaling से प्रत्येक KO mouse gene-pair similarity को 0–100 में normalize किया जाता है:
   Observed best-match max/mean निकालकर दोनों genes के symmetric optimal self-match score से normalize किया जाता है।
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   यदि denominator 0 हो, तो score 0 सेट किया जाता है।

अंतिम score phenotype-profile similarity का माप है। यह P-value, effect size, binding affinity या genes के बीच causal interaction का evidence नहीं है।

---

# ✉️ संपर्क
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 उद्धरण

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

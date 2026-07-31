> ⚠️ Ceci est une traduction générée par IA ; en cas de doute, référez-vous à l’original (README.md).  
> Original : https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** est un outil web utilisant les données de phénotype de souris KO de l’[IMPC](https://www.mousephenotype.org/) pour **extraire et visualiser des modules géniques basés sur la similarité phénotypique**.  
Outil accessible à tous en ligne 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Cette documentation décrit le fonctionnement actuel de **TSUMUGI v1.1.1**. L'application web publique utilise les données IMPC **Release 24.0**.

**TSUMUGI (紡ぎ)** découle de l’idée de « tisser ensemble les gènes qui façonnent les phénotypes ».

# 📖 Utilisation de TSUMUGI

TSUMUGI accepte trois types d’entrée.

### Phénotype (Phenotype)
Saisissez un phénotype d’intérêt pour trouver **des gènes dont les souris KO ont des profils phénotypiques similaires**.  
Noms basés sur la [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Liste des phénotypes](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gène (Gene)
Spécifiez un gène pour trouver **d’autres gènes présentant des phénotypes KO proches**.  
Symboles suivant [MGI](http://www.informatics.jax.org/).  
👉 [Liste des gènes](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Liste de gènes (Gene List)
Collez plusieurs gènes (un par ligne) pour chercher **au sein de la liste**.  
> [!CAUTION]
> Si aucun gène similaire n’est trouvé : `No similar phenotypes were found among the entered genes.`
> Gene List accepte au maximum 200 gènes disponibles distincts. Les doublons et lignes vides sont retirés avant le comptage; les symboles indisponibles sont signalés et exclus. Une liste contenant au moins 201 gènes disponibles est rejetée avant le chargement des données du réseau.

### 📥 Télécharger les données brutes
TSUMUGI publie des JSONL compressés en gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Symbole génétique (ex. "1110059G10Rik")  
- Marker accession ID (ex. "MGI:1913452")  
- Nom/ID de phénotype (ex. "fused joints", "MP:0000137")  
- Effect size (`number` ou `null` ; ex. 0.0, 1.324)
- Indicateur de significativité (`true` pour une annotation IMPC de phénotype anormal; `false` pour une mesure associée sans anomalie significative)
- Zygosité ("Homo", "Hetero", "Hemi")  
- Stade de vie ("Embryo", "Early", "Interval", "Late")  
- Dimorphisme sexuel (`None`, `Male`, `Female`)
- Annotation de maladie (ex. [] ou "Premature Ovarian Failure 18")

Exemple :
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Paire de gènes (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (contextes MICA à métadonnées concordantes : terme MP, stade de vie, zygosité et étiquette de sexe)
- `phenotype_similarity_score` (score Phenodigm, 0–100)

Exemple :
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## Notes d’interprétation

- **Contextes partagés :** Chaque élément de `phenotype_shared_annotations` est l’ancêtre commun le plus informatif (MICA) de deux annotations MP significatives dont la zygosité, le stade de vie et l’étiquette de sexe concordent. Cela ne signifie pas nécessairement que les deux gènes portent directement le même terme MP feuille. Un même MICA peut apparaître dans des contextes distincts lorsque les métadonnées diffèrent.
- **Règles d’affichage :** Les pages Gene et Phenotype affichent les paires ayant au moins trois contextes de phénotype anormal partagé et un score de similarité supérieur à 0. Gene List exige au moins un contexte partagé parmi les gènes saisis. Ce sont des règles d’affichage, pas des critères de significativité statistique.
- **Affichage de la similarité :** Le `phenotype_similarity_score` distribué est un score Phenodigm de 0–100. L’application web remet à l’échelle de 1–100 les valeurs présentes dans chaque réseau; les valeurs du curseur et des infobulles ne constituent donc pas une échelle absolue comparable entre pages.
- **Affichage de la taille d’effet :** TSUMUGI prend la valeur absolue de la taille d’effet IMPC, applique `log1p`, puis remet les valeurs du phénotype cible à l’échelle de 1–100. Cette valeur aide au classement dans la page, n’est pas la taille d’effet brute et ne se compare pas directement entre pages de phénotype. Les valeurs manquantes restent `null` en JSON et les nœuds sont affichés en blanc.
- **Modules :** Les modules sont des regroupements visuels, pas la preuve d’une voie moléculaire ou d’un complexe protéique. `Similarity` correspond aux composantes connexes et `Top-level MP` aux groupes ontologiques; les modules souples/fuzzy de la page Gene autorisent plusieurs appartenances. Le filtre du nombre de nœuds limite uniquement les modules affichés.
- **Étiquettes de sexe :** `Female` signifie que seule la P-value de l’effet KO femelle est ≤ 0.0001; `Male` signifie la même chose pour l’effet KO mâle. Les options sont mutuellement exclusives dans l’interface et ne remplacent pas un test formel d’interaction sexe×génotype.
- **Mise en évidence des phénotypes :** Les variantes de métadonnées d’un même phénotype sont regroupées en une option. Si Human Disease et un ou plusieurs phénotypes se chevauchent sur un gène, les catégories sont représentées par des anneaux concentriques.
- **Mise en évidence des maladies :** Les annotations de l’IMPC Disease Models Portal constituent une preuve de similarité de modèle et n’établissent pas à elles seules une relation causale entre gène et maladie chez l’humain.
- **Enregistrements non significatifs :** Ils représentent une mesure associée sans annotation anormale significative dans la condition considérée. Ils ne prouvent ni la normalité ni l’absence du phénotype; `disease_annotation` reste vide.
- **Interprétation du score :** Le score TSUMUGI n’est ni une P-value, ni une taille d’effet, ni une affinité de liaison, ni la preuve d’une interaction génique causale.

# 🌐 Réseau

La page se met à jour et dessine automatiquement le réseau selon l’entrée.

> [!IMPORTANT]
> Les pages Gene et Phenotype affichent les paires ayant au moins trois contextes de phénotype anormal partagé et un score de similarité supérieur à 0; Gene List exige au moins un contexte partagé parmi les gènes saisis. Ce sont des règles d’affichage, pas des critères de significativité statistique.

### Panneau réseau
**Nœuds** : gènes. Clic pour voir la liste des phénotypes anormaux observés; glisser pour repositionner.  
**Arêtes** : clic pour voir les phénotypes partagés.  
**Modules** encadrent des sous-réseaux de gènes. Clic pour lister les phénotypes des gènes du module; glisser pour repositionner et éviter les chevauchements.
Les pages Gene utilisent des modules Top-level MP souples/fuzzy, de sorte qu'un gène peut appartenir à plusieurs modules. Les pages Phenotype et Gene List peuvent basculer entre les modules `Similarity` fondés sur les composantes connexes et les modules `Top-level MP`.

### Panneau de contrôle
Réglez l’affichage réseau dans le panneau de gauche.

#### Filtre par similarité phénotypique
`Phenotypes similarity` filtre les arêtes selon la valeur de similarité affichée. Le `phenotype_similarity_score` distribué va de 0–100, mais chaque réseau affiché est remis à l’échelle de 1–100; les valeurs de pages différentes ne sont pas directement comparables.
> Détails : 👉 [🔍 Calcul des groupes de gènes phénotypiquement similaires](#-calcul-des-groupes-de-gènes-phénotypiquement-similaires)

#### Filtre par effect size
`Effect size` filtre les nœuds selon une valeur d’affichage propre à la page. TSUMUGI prend la valeur absolue de la taille d’effet IMPC, applique `log1p`, puis remet les valeurs du phénotype cible à l’échelle de 1–100. C’est une aide au classement dans la page, pas la taille d’effet brute, et elle ne se compare pas entre pages de phénotype.
Les effect sizes manquants sont sérialisés dans JSONL avec la valeur JSON standard `null`, restent sémantiquement manquants au lieu d’être convertis en zéro et leurs nœuds sont affichés en blanc.
> Masqué pour les phénotypes binaires (ex. [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); liste binaire [ici](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) ou l’entrée d’un seul gène.

#### Spécifier le génotype
- `Homo` (homozygote)  
- `Hetero` (hétérozygote)  
- `Hemi` (hémizygote)

#### Spécifier le sexe
- `Female`
- `Male`

#### Spécifier le stade de vie
- `Embryo`
- `Early` (0–16 semaines)
- `Interval` (17–48 semaines)
- `Late` (49+ semaines)

### Panneau de marquage
#### Affichage des modules
Le panneau de droite permet de choisir la définition et le module visible. Les contours des modules peuvent être masqués sans supprimer de gènes ni d'arêtes du réseau.

#### Highlight: Phenotype
Met en évidence les gènes selon leur annotation phénotypique. Les variantes de métadonnées d’un même phénotype sont regroupées en une option. Lorsque Human Disease et au moins un phénotype se chevauchent sur un gène, les catégories sont représentées par des anneaux concentriques.

#### Highlight: Human Disease
Met en évidence les gènes KO portant des annotations de modèles de maladie dans l’IMPC Disease Models Portal. Cette annotation indique une similarité de modèle et n’établit pas à elle seule une relation causale entre gène et maladie chez l’humain.

#### Search: Specific Gene
Recherche de gènes dans le réseau.

#### Layout & Display
Ajuste mise en page, taille de police, épaisseur d’arêtes, répulsion (Cose).

#### Export
Exporte en PNG, JPG, SVG, CSV ou GraphML. Les cadres de module peuvent être inclus dans les fichiers PNG, JPG et SVG. Le CSV contient l'affectation active aux modules Similarity ou Top-level MP et les listes de phénotypes; GraphML est compatible Cytoscape.

# 🛠 Interface en ligne de commande

Le CLI TSUMUGI permet d'utiliser localement les dernières données IMPC, avec des filtres et sorties plus fines que l'outil web.

## Fonctionnalités

- Recalculer avec `statistical-results-ALL.csv.gz` IMPC (optionnel `mp.obo`, `impc_phenodigm.csv`).  
- Filtrer selon les annotations MP significatives ou les mesures associées non significatives.
- Filtrer par liste de gènes (séparée par virgules ou fichier texte).  
- Sorties: GraphML (`tsumugi build-graphml`), bundle webapp hors ligne (`tsumugi build-webapp`).

## Installation

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Prêt quand `tsumugi --version` affiche la version.

## Commandes disponibles

- `tsumugi run`: recalculer le réseau à partir des données IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: filtrer des paires ou des gènes selon les annotations MP significatives ou les mesures associées non significatives
- `tsumugi count --pairwise/--genewise (--min/--max)`: filtrer par nombre de phénotypes (paires/gènes)  
- `tsumugi score (--min/--max)`: filtrer par score de similarité (paires)  
- `tsumugi genes --keep/--drop`: conserver/retirer via liste de gènes (virgules ou fichier texte)  
- `tsumugi life-stage --keep/--drop`: filtrer par stade de vie (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: filtrer par sexe (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: filtrer par zygosité (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: générer GraphML (Cytoscape, etc.)  
- `tsumugi build-webapp`: générer les assets web TSUMUGI (HTML/CSS/JS locaux)

> [!NOTE]
> Toutes les sous-commandes de filtrage écrivent du JSONL sur STDOUT.  
> Redirigez avec `>` pour enregistrer dans un fichier.

> [!IMPORTANT]
> Toutes les commandes sauf `tsumugi run` nécessitent `pairwise_similarity_annotations.jsonl.gz` ou `genewise_phenotype_annotations.jsonl.gz`.
> Les deux fichiers peuvent être téléchargés depuis la [page d’accueil de TSUMUGI](https://larc-tsukuba.github.io/tsumugi/).

## Utilisation

### Recalculer à partir des données IMPC (`tsumugi run`)
Si `--mp_obo` est omis, TSUMUGI utilise le `data-version: releases/2025-08-27/mp.obo` fourni.  
Si `--impc_phenodigm` est omis, il utilise le fichier récupéré le 2025-10-01 depuis l'[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Sorties: `./tsumugi-output` contient les annotations genewise (genewise_phenotype_annotations.jsonl.gz), les similarités pairwise (pairwise_similarity_annotations.jsonl.gz) et les assets de visualisation (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> Le dossier `TSUMUGI-webapp` inclut des scripts de lancement par OS; double-cliquez pour ouvrir l'app locale:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filtrer par terme MP (`tsumugi mp --include/--exclude`)
Extraire les paires de gènes (ou gènes) qui incluent les phénotypes d'intérêt, ou celles mesurées sans anomalie significative.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Inclure les gènes/paires qui possèdent le terme MP spécifié (descendants inclus).

#### `-e MP_ID`, `--exclude MP_ID`
Renvoyer les gènes/paires mesurés pour le terme MP (descendants inclus) sans anomalie significative. `-a/--genewise_annotations` requis.

> [!CAUTION]
> Un enregistrement non significatif ne prouve ni que l’animal est normal ni que le phénotype est absent. Il indique seulement que la mesure associée n’a pas produit d’annotation anormale significative dans cette condition.

#### `-g`, `--genewise`
Filtrer au niveau gène. Lit `genewise_phenotype_annotations.jsonl(.gz)`. Avec `--genewise`, indiquez `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filtrer au niveau paire. Cible `pairwise_similarity_annotations.jsonl(.gz)`. Si `--in` est omis, lecture depuis STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Chemin vers l'ontologie Mammalian Phenotype (mp.obo). Si omis, utilise `data/mp.obo` fourni.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Chemin vers les annotations genewise (JSONL/.gz). Requis pour `--exclude`; à indiquer aussi avec `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

#### `--life_stage LIFE_STAGE`
Filtre additionnel par stade de vie. Valeurs: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Filtre additionnel par dimorphisme sexuel. Utilisez les valeurs des annotations (ex.: `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Filtre additionnel par zygosité. Valeurs: `Homo`, `Hetero`, `Hemi`.

```bash
# Extraire uniquement les paires contenant MP:0001146 (abnormal testis morphology) ou des termes descendants (ex. MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Extraire les paires où MP:0001146 et les termes descendants ont été mesurés sans anomalie significative
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

# Extraire les annotations significatives au niveau du gène contenant MP:0001146 (descendants inclus)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Extraire les gènes mesurés pour MP:0001146 (descendants inclus) sans anomalie significative
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Les termes MP descendants de l'ID spécifié sont également pris en charge.**  
> Par exemple, si vous indiquez `MP:0001146 (abnormal testis morphology)`, les termes descendants comme `MP:0004849 (abnormal testis size)` sont aussi pris en compte.

### Filtrer par nombre de phénotypes (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filtrer des gènes ou paires par nombre de phénotypes. Au moins `--min` ou `--max` est requis.

#### `-g`, `--genewise`
Filtre par nombre de phénotypes significatifs par gène. Requiert `-a/--genewise_annotations` avec `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filtre par nombre de phénotypes partagés par paire. Si `--in` est omis, lecture depuis STDIN.

#### `--min MIN`, `--max MAX`
Bornes basse/haute du nombre de phénotypes. Une seule borne suffit pour un filtrage unilatéral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Chemin vers les annotations genewise (JSONL/.gz). Requis avec `--genewise`.

- Phénotypes partagés par paire:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Phénotypes par gène (genewise requis):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
```

`--min` ou `--max` seul est accepté.

### Filtrer par score de similarité (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filtre les paires selon `phenotype_similarity_score` (0–100). Au moins `--min` ou `--max` est requis.

#### `--min MIN`, `--max MAX`
Bornes basse/haute du score. Une seule borne suffit pour un filtrage unilatéral.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

`--min` ou `--max` seul est accepté.

### Filtrer par liste de gènes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Conserver uniquement les paires contenant les gènes spécifiés dans un fichier texte.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Supprimer les paires contenant les gènes spécifiés dans un fichier texte.

#### `-g`, `--genewise`
Filtrer par symboles de gènes fournis par l'utilisateur.

#### `-p`, `--pairwise`
Filtrer par paires de gènes fournies par l'utilisateur.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

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

### Filtrer par stade de vie (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Conserver uniquement le stade de vie spécifié (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Supprimer le stade de vie spécifié.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Filtrer par sexe (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Conserver uniquement le sexe spécifié (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Supprimer le sexe spécifié.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Filtrer par zygosité (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Conserver uniquement la zygosité spécifiée (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Supprimer la zygosité spécifiée.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### Export GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Chemin vers les annotations genewise (JSONL/.gz). Requis.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Chemin vers les annotations pairwise (JSONL/.gz). Si omis, lecture depuis STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Chemin vers les annotations genewise (JSONL/.gz). Requis.

#### `-o OUT`, `--out OUT`
Répertoire de sortie du bundle webapp (HTML/CSS/JS + données réseau). Ne pas fournir un nom de fichier avec extension.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

Le CLI prend en charge STDIN/STDOUT, vous pouvez chaîner les commandes:  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 Calcul des groupes de gènes phénotypiquement similaires

## Source de données

Nous utilisons le jeu de données IMPC [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Détails des colonnes: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Prétraitement

TSUMUGI considère un `mp_term_id` IMPC non vide comme une annotation IMPC de phénotype anormal. Il conserve également les mesures associées sans annotation anormale significative pour les requêtes d’exclusion tenant compte de la présence d’une mesure.
Pour les mesures non significatives, chaque terme non racine le plus spécifique de `intermediate_mp_term_id`, ontologiquement incomparable aux autres termes retenus, est émis dans un enregistrement distinct. Les mesures associées uniquement à `MP:0000001` ou à aucun terme MP valide sont omises, car elles ne permettent pas de requête spécifique à un phénotype.

- Convertit la zygosité en `Homo`, `Hetero` ou `Hemi`.
- Attribue `Female` lorsque seule `female_ko_effect_p_value` est ≤ 0.0001 et `Male` lorsque seule `male_ko_effect_p_value` est ≤ 0.0001; sinon, attribue `None`.
- Utilise la valeur absolue de la taille d’effet. Les valeurs manquantes restent manquantes et sont sérialisées en `null` dans JSON.

## Similarité phénotypique

TSUMUGI applique la formule de score originale de PhenoDigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) pour comparer les profils phénotypiques des gènes de souris KO de l'IMPC au sein de Mammalian Phenotype Ontology.

> [!NOTE]
> TSUMUGI utilise la formule de score de PhenoDigm, mais n'exécute pas le pipeline interespèces HPO-MP/ZP OWLSim original. Il compare les annotations MP des gènes de souris KO de l'IMPC.

### 1. Définition de la similarité des paires de termes MP

* Construire l'ontologie MP et calculer l'Information Content (IC) à partir des annotations IMPC significatives:
   `IC(term) = -log2(|annotations propagées au terme| / |toutes les annotations significatives|)`
   Chaque annotation directe est propagée au terme MP annoté et à tous ses ancêtres.

* Pour chaque paire de termes MP, trouver les ancêtres communs ayant l'IC dérivé des annotations le plus élevé. En cas d'égalité, sélectionner de manière déterministe le candidat ayant le moins de descendants transitifs dans l'ontologie MP, puis l'identifiant de terme MP le plus petit dans l'ordre lexicographique. L'IC du MICA sélectionné est la similarité de Resnik. Ce départage ne modifie ni le score de similarité ni le schéma de sortie.
   Les candidats ex æquo ont le même score numérique de paire de termes, mais l’étiquette MICA choisie peut modifier le nombre de contextes partagés et donc l’éligibilité à l’affichage.

* Pour deux termes MP, calculer l'indice de Jaccard de leurs ensembles d'attributs inférés, définis comme le terme lui-même plus tous ses ancêtres.

* Définir la similarité de paires de termes MP comme `sqrt(Resnik * Jaccard)`.

### 2. Matrice de similarité des paires de gènes

* Pour chaque paire de gènes, construire une matrice de similarité terme MP × terme MP à partir des scores des paires de termes.

* Un MICA n’est enregistré dans `phenotype_shared_annotations` que si la zygosité, le stade de vie et l’étiquette de sexe concordent. Ces métadonnées ne pondèrent pas le score PhenoDigm.

### 3. Mise à l’échelle Phenodigm

* Appliquer la mise à l'échelle maximum/moyenne de PhenoDigm pour normaliser la similarité de chaque paire de gènes de souris KO à 0–100:
   Calculer le maximum et la moyenne des best matches observés, puis normaliser par le score optimal symétrique de self match des deux gènes.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Si le dénominateur est 0, le score est 0.

Le score obtenu mesure la similarité des profils phénotypiques. Ce n’est ni une P-value, ni une taille d’effet, ni une affinité de liaison, ni la preuve d’une interaction causale entre les gènes.

---

# ✉️ Contact
- Formulaire : https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues : https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Citation

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

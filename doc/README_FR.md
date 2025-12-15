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
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** est un outil web utilisant les données de phénotype de souris KO de l’[IMPC](https://www.mousephenotype.org/) pour **extraire et visualiser des modules géniques basés sur la similarité phénotypique**.  
Outil accessible à tous en ligne 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

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
> Aucun gène similaire : `No similar phenotypes were found among the entered genes.`  
> Plus de 200 : `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Télécharger les données brutes
TSUMUGI publie des JSONL compressés en gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Symbole génétique (ex. "1110059G10Rik")  
- Marker accession ID (ex. "MGI:1913452")  
- Nom/ID de phénotype (ex. "fused joints", "MP:0000137")  
- Effect size (ex. 0.0, 1.324)  
- Significativité (True/false)  
- Zygosité ("Homo", "Hetero", "Hemi")  
- Stade de vie ("Embryo", "Early", "Interval", "Late")  
- Dimorphisme sexuel ("", "Male", "Female")  
- Annotation de maladie (ex. [] ou "Premature Ovarian Failure 18")

Exemple :
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Paire de gènes (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` : métadonnées par phénotype (stade, zygosité, sexe)  
- `phenotype_similarity_score` : score Resnik→Phenodigm (0–100)

Exemple :
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Réseau

La page se met à jour et dessine automatiquement le réseau selon l’entrée.

> [!IMPORTANT]  
> Les paires de gènes avec **≥3 phénotypes anormaux partagés** et **similarité > 0.0** sont visualisées.

### Panneau réseau
**Nœuds** : gènes. Clic pour voir la liste des phénotypes anormaux observés; glisser pour repositionner.  
**Arêtes** : clic pour voir les phénotypes partagés.  
**Modules** encadrent des sous-réseaux de gènes. Clic pour lister les phénotypes des gènes du module; glisser pour repositionner et éviter les chevauchements.

### Panneau de contrôle
Réglez l’affichage réseau dans le panneau de gauche.

#### Filtre par similarité phénotypique
`Phenotypes similarity` fixe le seuil des arêtes via le score Resnik→Phenodigm.  
> Détails : 👉 [🔍 Calcul des groupes de gènes phénotypiquement similaires](#-calcul-des-groupes-de-gènes-phénotypiquement-similaires)

#### Filtre par sévérité phénotypique
`Phenotype severity` filtre les nœuds par effect size en KO; plus grand = impact plus fort.  
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
#### Highlight: Human Disease
Met en évidence les gènes liés aux maladies humaines (IMPC Disease Models Portal).

#### Search: Specific Gene
Recherche de gènes dans le réseau.

#### Layout & Display
Ajuste mise en page, taille de police, épaisseur d’arêtes, répulsion (Cose).

#### Export
Exporte en PNG/CSV/GraphML. CSV inclut les IDs de modules et les phénotypes; GraphML est compatible Cytoscape.

# 🛠 Interface en ligne de commande

Cette version ajoute le CLI pour actualiser avec les données IMPC, appliquer des filtres fins et exporter en GraphML ou webapp hors ligne.

- Recalculer avec `statistical-results-ALL.csv.gz` (optionnel `mp.obo`, `impc_phenodigm.csv`)  
- Filtrer par présence/absence de terme MP  
- Filtrer par liste de gènes (CSV ou fichier texte)  
- Sorties : GraphML (`tsumugi build-graphml`), webapp hors ligne (`tsumugi build-webapp`)

## Commandes disponibles
- `tsumugi run` : recalcul depuis les données IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)` : conserver/exclure des paires ou des gènes selon un terme MP  
- `tsumugi count --pairwise/--genewise (--min/--max)` : filtrer par nombre de phénotypes (paires/gènes)  
- `tsumugi score (--min/--max)`: filtrer par score de similarité (paires de gènes)
- `tsumugi genes --keep/--drop` : conserver/retirer via liste de gènes  
- `tsumugi life-stage --keep/--drop` : filtrer par stade de vie  
- `tsumugi sex --keep/--drop` : filtrer par sexe  
- `tsumugi zygosity --keep/--drop` : filtrer par zygosité  
- `tsumugi build-graphml` : générer GraphML  
- `tsumugi build-webapp` : générer les assets web TSUMUGI

## Installation
BioConda :
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI :
```bash
pip install tsumugi
```
Prêt quand `tsumugi --version` affiche la version.

## Exemples courants

### Recalculer avec les données IMPC (`tsumugi run`)
Sans `--mp_obo`, TSUMUGI utilise le `data-version: releases/2025-08-27/mp.obo` fourni.  
Sans `--impc_phenodigm`, il utilise le fichier récupéré le 2025-10-01 sur le [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Sorties : dans `./tsumugi-output`, JSONL genewise/pairwise et assets de visualisation (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` contient des scripts de lancement par OS; double-cliquez pour ouvrir l’app locale :  
> - Windows : `open_webapp_windows.bat`  
> - macOS : `open_webapp_mac.command`  
> - Linux : `open_webapp_linux.sh`

### Filtrer par terme MP (`tsumugi mp --include/--exclude`)
Extrayez uniquement les paires de gènes qui contiennent les phénotypes d’intérêt, ou les paires où ces phénotypes ont été mesurés sans montrer d’anomalie significative.

- `--pairwise` (par défaut si rien n’est défini) : sortie par paires. Utilisez `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise` : sortie par gène individuel. Utilisez `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (obligatoire avec `--exclude`, recommandé avec `--include`).

```bash
# Extraire uniquement les paires contenant MP:0001146 (abnormal testis morphology) ou des termes descendants (ex. MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extraire les paires où MP:0001146 et les termes descendants ont été mesurés sans anomalie significative
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extraire les annotations significatives au niveau du gène contenant MP:0001146 (descendants inclus)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Extraire les gènes mesurés pour MP:0001146 (descendants inclus) sans anomalie significative
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Les termes MP descendants de l’ID spécifié sont également pris en charge.**  
> Par exemple, si vous indiquez `MP:0001146 (abnormal testis morphology)`, les termes descendants comme `MP:0004849 (abnormal testis size)` sont aussi pris en compte.

### Filtrer par nombre de phénotypes (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- Phénotypes partagés par paire :
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Phénotypes par gène (genewise requis) :
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```


### Filtrer par score de similarité (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Filtre les paires de gènes selon `phenotype_similarity_score` (0–100). Au moins `--min` ou `--max` est requis.

#### `--min MIN`, `--max MAX`
Bornes basse/haute du score. Une seule borne suffit pour un filtrage unilatéral.

#### `--in IN`
Chemin vers les annotations pairwise (JSONL/.gz); si omis, lecture sur STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` ou `--max` seul est accepté.

### Liste de gènes (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Stade de vie / sexe / zygosité
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### Export GraphML / Webapp
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
```
Pipeline exemple : `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Calcul des groupes de gènes phénotypiquement similaires

## Source de données
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Colonnes : [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Prétraitement
Extraire les paires gène–phénotype avec P (`p_value`, `female_ko_effect_p_value` ou `male_ko_effect_p_value`) ≤ 0.0001.  
- Zygosité : `homo`, `hetero`, `hemi`  
- Sexe : `female`, `male`

## Similarité phénotypique
Resnik entre termes MP → échelle Phenodigm (0–100).

1. Construire l’ontologie MP, calculer l’IC :  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC du MICA; si pas d’ancêtre commun, 0.  
3. Pour chaque paire : matrice Resnik entre termes significatifs, pondérée par accord des métadonnées (zygosité/stade/sexe : 1.0/0.75/0.5/0.25); prendre max/moyenne réels.  
4. Obtenir max/moyenne théoriques via les IC, puis normaliser :  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   Si le dénominateur théorique est 0, mettre 0. Score 0–100 utilisé pour les téléchargements et le slider `Phenotypes similarity`.

# ✉️ Contact
- Formulaire : https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues : https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

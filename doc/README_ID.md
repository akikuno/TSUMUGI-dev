> ⚠️ Ini terjemahan yang dibuat AI; jika ragu, silakan lihat teks asli (README.md).  
> Asli: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** adalah alat web yang memakai data fenotipe tikus KO dari [IMPC](https://www.mousephenotype.org/) untuk **mengekstrak dan memvisualisasikan modul gen berdasarkan kesamaan fenotipe**.  
Alat ini terbuka untuk semua pengguna secara daring 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI (紡ぎ)** berarti “menyulam kelompok gen pembentuk fenotipe”.

# 📖 Cara menggunakan TSUMUGI

TSUMUGI mendukung tiga jenis input:

### 1. Phenotype
Masukkan fenotipe yang diminati untuk mencari **gen yang KO-nya punya profil fenotipe mirip**.  
Nama fenotipe mengikuti [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Daftar fenotipe](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. Gene
Tentukan satu gen untuk mencari **gen lain dengan fenotipe KO serupa**.  
Simbol mengikuti [MGI](http://www.informatics.jax.org/).  
👉 [Daftar gen](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. Gene List
Tempel beberapa gen (satu per baris) untuk mencari **di dalam daftar itu**.  
> [!CAUTION]  
> Jika tidak ada yang mirip: `No similar phenotypes were found among the entered genes.`  
> Jika lebih dari 200: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Unduh data mentah
TSUMUGI menyediakan file JSONL terkompresi gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Simbol gen (contoh "1110059G10Rik")  
- Marker accession ID (contoh "MGI:1913452")  
- Nama/ID fenotipe (contoh "fused joints", "MP:0000137")  
- Effect size (contoh 0.0, 1.324)  
- Signifikansi (True/false)  
- Zigositas ("Homo", "Hetero", "Hemi")  
- Tahap hidup ("Embryo", "Early", "Interval", "Late")  
- Dimorfisme seksual ("", "Male", "Female")  
- Anotasi penyakit (contoh [] atau "Premature Ovarian Failure 18")

Contoh:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Pasangan gen (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (tahap hidup, zigositas, perbedaan jenis kelamin) untuk fenotipe bersama  
- `phenotype_similarity_score`: skor Resnik→Phenodigm (0–100)

Contoh:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Jaringan

Halaman berpindah dan menggambar jaringan secara otomatis sesuai input.

> [!IMPORTANT]  
> Pairs dengan **≥3 fenotipe abnormal bersama** dan **similarity > 0.0** akan divisualkan.

### Panel jaringan
**Node** mewakili gen. Klik untuk melihat daftar fenotipe abnormal; seret untuk memindahkan.  
**Edge** klik untuk melihat detail fenotipe bersama.

### Panel kontrol
Menyesuaikan tampilan jaringan di panel kiri.

#### Filter kesamaan fenotipe
`Phenotypes similarity` mengatur ambang edge berdasar skor Resnik→Phenodigm.  
> Cara hitung: 👉 [🔍 Cara kami menghitung kesamaan fenotipe](#-how-we-calculate-phenotypically-similar-genes)

#### Filter keparahan fenotipe
`Phenotype severity` memfilter node berdasar effect size pada KO. Nilai lebih besar berarti dampak lebih kuat.  
> Disembunyikan untuk fenotipe biner (mis. [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); daftar biner [di sini](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) atau input satu gen.

#### Tentukan genotype
- `Homo`
- `Hetero`
- `Hemi`

#### Tentukan jenis kelamin
- `Female`
- `Male`

#### Tentukan tahap hidup
- `Embryo`
- `Early` (0–16 minggu)
- `Interval` (17–48 minggu)
- `Late` (49+ minggu)

### Panel markup
#### Highlight: Human Disease
Sorot gen terkait penyakit (data IMPC Disease Models Portal).

#### Search: Specific Gene
Cari nama gen dalam jaringan.

#### Layout & Display
Atur tata letak, ukuran font, ketebalan edge, repulsi node (Cose).

#### Export
Ekspor PNG/CSV/GraphML. CSV memuat ID modul dan daftar fenotipe; GraphML kompatibel dengan Cytoscape.

# 🛠 Edisi Command-Line

Rilis ini menambah CLI: unduh pembaruan IMPC terbaru, jalankan sendiri, filter lebih bebas, dan ekspor GraphML atau webapp offline.

- Hitung ulang dengan IMPC `statistical-results-ALL.csv.gz` (opsional `mp.obo`, `impc_phenodigm.csv`)  
- Filter keberadaan/ketiadaan istilah MP  
- Filter daftar gen (CSV atau file teks)  
- Output: GraphML (`tsumugi build-graphml`), bundel webapp offline (`tsumugi build-webapp`)

## Perintah yang tersedia
- `tsumugi run`: hitung ulang dari data IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: sertakan/keluarkan pasangan atau gen terkait istilah MP  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: filter jumlah fenotipe (pairwise/genewise)  
- `tsumugi genes --keep/--drop`: simpan/hapus via daftar gen  
- `tsumugi life-stage --keep/--drop`: filter tahap hidup  
- `tsumugi sex --keep/--drop`: filter jenis kelamin  
- `tsumugi zygosity --keep/--drop`: filter zigositas  
- `tsumugi build-graphml`: buat GraphML  
- `tsumugi build-webapp`: buat aset webapp TSUMUGI

## Instalasi
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
Siap jika `tsumugi --version` tampil.

## Contoh umum (per perintah)

### 1. Hitung ulang dari data IMPC (`tsumugi run`)
Jika `--mp_obo` dilewati, gunakan bawaan `data-version: releases/2025-08-27/mp.obo`.  
Jika `--impc_phenodigm` dilewati, gunakan file yang diambil 2025-10-01 dari [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Keluaran: `./tsumugi-output` berisi genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz, dan aset visualisasi (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` menyertakan skrip peluncur per-OS; klik ganda untuk membuka webapp lokal:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. Filter istilah MP (`tsumugi mp --include/--exclude`)
Ambil hanya pasangan gen yang mengandung fenotipe yang diminati, atau pasangan di mana fenotipe tersebut sudah diukur tetapi tidak menunjukkan kelainan yang signifikan.

- `--pairwise` (default jika tidak ditentukan): keluaran per pasangan gen. Gunakan `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: keluaran per gen. Gunakan `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (wajib untuk `--exclude`, dianjurkan untuk `--include`).

```bash
# Ambil hanya pasangan yang mencakup MP:0001146 (abnormal testis morphology) atau istilah turunannya (mis. MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Ambil pasangan di mana MP:0001146 dan istilah turunannya diukur namun tidak menunjukkan kelainan signifikan
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Ambil anotasi signifikan per gen yang memuat MP:0001146 (termasuk turunan)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Ambil gen yang diukur untuk MP:0001146 (termasuk turunan) namun tidak signifikan
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Istilah MP turunan dari ID yang ditentukan juga diproses.**  
> Misalnya, jika Anda menentukan `MP:0001146 (abnormal testis morphology)`, istilah turunan seperti `MP:0004849 (abnormal testis size)` juga akan dihitung.

### 3. Filter jumlah fenotipe (`tsumugi n-phenos`)
- Fenotipe bersama per pasangan:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Fenotipe per gen (butuh genewise):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```

### 4. Filter dengan daftar gen (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. Tahap hidup / jenis kelamin / zigositas
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### 6. Ekspor GraphML / Webapp
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
Pipeline: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cara kami menghitung kesamaan fenotipe

## Sumber data
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Kolom: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Pra-pemrosesan
Ambil pasangan gen–fenotipe dengan P ≤ 0.0001 (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`).  
- Zigositas: `homo`, `hetero`, `hemi`  
- Jenis kelamin: `female`, `male`

## Kesamaan fenotipik
Hitung **Resnik** antar istilah MP dan skala ke **Phenodigm (0–100)** untuk pasangan gen.

1. Bangun ontologi MP, hitung IC:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC nenek moyang bersama paling informatif (MICA); jika tidak ada, 0.  
3. Untuk setiap pasangan gen: matriks Resnik antar istilah signifikan, bobot kecocokan zigositas/tahap hidup/jenis kelamin (1.0/0.75/0.5/0.25); ambil max dan mean aktual.  
4. Dapatkan max/mean teoretis dari IC istilah, lalu normalisasi:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   Jika penyebut teoretis 0, setel 0. Skor 0–100 dipakai di unduhan dan slider `Phenotypes similarity`.

# ✉️ Kontak
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

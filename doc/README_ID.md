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

### Phenotype
Masukkan fenotipe yang diminati untuk mencari **gen yang KO-nya punya profil fenotipe mirip**.  
Nama fenotipe mengikuti [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Daftar fenotipe](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gene
Tentukan satu gen untuk mencari **gen lain dengan fenotipe KO serupa**.  
Simbol mengikuti [MGI](http://www.informatics.jax.org/).  
👉 [Daftar gen](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Gene List
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
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Pasangan gen (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (tahap hidup, zigositas, perbedaan jenis kelamin) untuk fenotipe bersama  
- `phenotype_similarity_score`: skor Resnik→Phenodigm (0–100)

Contoh:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Jaringan

Halaman berpindah dan menggambar jaringan secara otomatis sesuai input.

> [!IMPORTANT]  
> Pairs dengan **≥3 fenotipe abnormal bersama** dan **similarity > 0.0** akan divisualkan.

### Panel jaringan
**Node** mewakili gen. Klik untuk melihat daftar fenotipe abnormal; seret untuk memindahkan.  
**Edge** klik untuk melihat detail fenotipe bersama.  
**Module** menggambarkan sub-jaringan gen. Klik modul untuk melihat fenotipe gen di dalamnya; seret modul agar tidak saling tumpang tindih.

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

# 🛠 Antarmuka Baris Perintah

CLI TSUMUGI memungkinkan penggunaan data IMPC terbaru secara lokal, dengan filter dan output yang lebih rinci dibandingkan versi web.

## Fitur

- Hitung ulang dengan `statistical-results-ALL.csv.gz` IMPC (opsional `mp.obo`, `impc_phenodigm.csv`).  
- Filter berdasarkan ada/tidaknya istilah MP.  
- Filter berdasarkan daftar gen (dipisah koma atau file teks).  
- Output: GraphML (`tsumugi build-graphml`), bundle webapp offline (`tsumugi build-webapp`).

## Instalasi

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Siap digunakan saat `tsumugi --version` menampilkan versinya.

## Perintah yang tersedia

- `tsumugi run`: hitung ulang jaringan dari data IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: filter pasangan gen atau gen yang mengandung/tidak menunjukkan istilah MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: filter berdasarkan jumlah fenotipe (pairwise/genewise)  
- `tsumugi score (--min/--max)`: filter berdasarkan skor kemiripan (pairwise)  
- `tsumugi genes --keep/--drop`: pertahankan/hapus berdasarkan daftar gen (koma atau file teks)  
- `tsumugi life-stage --keep/--drop`: filter berdasarkan tahap kehidupan (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: filter berdasarkan jenis kelamin (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: filter berdasarkan zigositas (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: buat GraphML (Cytoscape, dll.)  
- `tsumugi build-webapp`: buat aset web TSUMUGI (HTML/CSS/JS lokal)

> [!NOTE]
> Semua subcommand filter mengalirkan JSONL ke STDOUT.  
> Gunakan `>` untuk menyimpan ke file.

> [!IMPORTANT]
> Semua perintah kecuali `tsumugi run` memerlukan `pairwise_similarity_annotation.jsonl.gz` atau `genewise_phenotype_annotation.jsonl.gz`.
> Kedua file dapat diunduh dari [halaman utama TSUMUGI](https://larc-tsukuba.github.io/tsumugi/).

## Cara pakai

### Hitung ulang dari data IMPC (`tsumugi run`)
Jika `--mp_obo` dihilangkan, TSUMUGI menggunakan `data-version: releases/2025-08-27/mp.obo` bawaan.  
Jika `--impc_phenodigm` dihilangkan, TSUMUGI menggunakan file yang diambil pada 2025-10-01 dari [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Output: `./tsumugi-output` berisi anotasi genewise (genewise_phenotype_annotations.jsonl.gz), data kemiripan pairwise (pairwise_similarity_annotations.jsonl.gz), dan aset visualisasi (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> Direktori `TSUMUGI-webapp` menyertakan skrip peluncuran per OS; klik dua kali untuk membuka webapp lokal:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filter berdasarkan istilah MP (`tsumugi mp --include/--exclude`)
Ekstrak pasangan gen (atau gen) yang memiliki fenotipe target, atau pasangan yang diukur namun tidak menunjukkan anomali signifikan.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Sertakan gen/pasangan gen yang memiliki istilah MP yang ditentukan (termasuk turunan).

#### `-e MP_ID`, `--exclude MP_ID`
Kembalikan gen/pasangan gen yang diukur untuk istilah MP (termasuk turunan) tetapi tidak menunjukkan fenotipe signifikan. Memerlukan `-a/--genewise_annotations`.

#### `-g`, `--genewise`
Filter pada level gen. Membaca `genewise_phenotype_annotations.jsonl(.gz)`. Saat menggunakan `--genewise`, sertakan `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filter pada level pasangan gen. Target `pairwise_similarity_annotations.jsonl(.gz)`. Jika `--in` dihilangkan, membaca dari STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Path ke ontologi Mammalian Phenotype (mp.obo). Jika dihilangkan, gunakan `data/mp.obo` bawaan.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path ke file anotasi genewise (JSONL/.gz). Wajib untuk `--exclude`; sertakan juga saat `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

#### `--life_stage LIFE_STAGE`
Filter tambahan berdasarkan tahap kehidupan. Nilai: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Filter tambahan berdasarkan dimorfisme seksual. Gunakan nilai yang ada di anotasi (mis., `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Filter tambahan berdasarkan zigositas. Nilai: `Homo`, `Hetero`, `Hemi`.

```bash
# Hanya ekstrak pasangan gen yang mencakup MP:0001146 (abnormal testis morphology) atau istilah turunan (mis., MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Ekstrak pasangan yang MP:0001146 dan turunannya diukur tanpa anomali signifikan
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Ekstrak anotasi signifikan tingkat gen yang mengandung MP:0001146 (turunan termasuk)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Ekstrak gen yang diukur untuk MP:0001146 (turunan termasuk) tanpa anomali signifikan
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Istilah MP turunan dari ID yang ditentukan juga ikut dipertimbangkan.**  
> Misalnya, jika Anda menentukan `MP:0001146 (abnormal testis morphology)`, istilah turunan seperti `MP:0004849 (abnormal testis size)` juga dihitung.

### Filter berdasarkan jumlah fenotipe (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filter gen atau pasangan gen berdasarkan jumlah fenotipe. Minimal `--min` atau `--max` wajib.

#### `-g`, `--genewise`
Filter berdasarkan jumlah fenotipe signifikan per gen. Memerlukan `-a/--genewise_annotations` dengan `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filter berdasarkan jumlah fenotipe bersama per pasangan. Jika `--in` dihilangkan, membaca dari STDIN.

#### `--min MIN`, `--max MAX`
Batas bawah/atas jumlah fenotipe. Satu batas saja cukup untuk filter satu sisi.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path ke file anotasi genewise (JSONL/.gz). Wajib dengan `--genewise`.

- Fenotipe bersama per pasangan:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Fenotipe per gen (genewise wajib):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

`--min` atau `--max` saja juga bisa.

### Filter berdasarkan skor kemiripan (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filter pasangan gen berdasarkan `phenotype_similarity_score` (0–100). Minimal `--min` atau `--max` wajib.

#### `--min MIN`, `--max MAX`
Batas bawah/atas skor. Satu batas saja cukup untuk filter satu sisi.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

`--min` atau `--max` saja juga bisa.

### Filter berdasarkan daftar gen (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Pertahankan hanya pasangan yang mengandung gen tertentu dari file teks.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Hapus pasangan yang mengandung gen tertentu dari file teks.

#### `-g`, `--genewise`
Filter berdasarkan simbol gen yang diberikan pengguna.

#### `-p`, `--pairwise`
Filter berdasarkan pasangan gen yang diberikan pengguna.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

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

### Filter berdasarkan tahap kehidupan (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Pertahankan hanya tahap kehidupan yang ditentukan (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Hapus tahap kehidupan yang ditentukan.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Filter berdasarkan jenis kelamin (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Pertahankan hanya jenis kelamin yang ditentukan (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Hapus jenis kelamin yang ditentukan.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Filter berdasarkan zigositas (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Pertahankan hanya zigositas yang ditentukan (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Hapus zigositas yang ditentukan.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### Ekspor GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path ke file anotasi genewise (JSONL/.gz). Wajib.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path ke file anotasi pairwise (JSONL/.gz). Jika dihilangkan, membaca dari STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path ke file anotasi genewise (JSONL/.gz). Wajib.

#### `-o OUT`, `--out OUT`
Direktori output untuk bundle webapp (HTML/CSS/JS + data jaringan). Jangan berikan nama file dengan ekstensi.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

CLI mendukung STDIN/STDOUT, sehingga Anda bisa merangkai perintah:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cara kami menghitung kesamaan fenotipe

## Sumber data

Kami menggunakan dataset IMPC [Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`.  
Kolom dataset: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Pra-pemrosesan

Ekstrak pasangan gen–fenotipe dengan P-value pada tikus KO (`p_value`, `female_ko_effect_p_value`, atau `male_ko_effect_p_value`) ≤ 0.0001.  
- Anotasikan fenotipe spesifik genotipe sebagai `homo`, `hetero`, atau `hemi`.  
- Anotasikan fenotipe spesifik jenis kelamin sebagai `female` atau `male`.

## Kesamaan fenotipe

TSUMUGI mengadopsi pendekatan mirip Phenodigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)).  

> [!NOTE]
> Perbedaan dengan Phenodigm asli adalah sebagai berikut.  
> 1. **Istilah di bawah persentil IC ke-5 ditetapkan ke IC=0, sehingga fenotipe yang terlalu umum (misalnya embryo phenotype) tidak dievaluasi.**
> 2. **Kami menerapkan pembobotan berdasarkan kecocokan metadata: genotipe, tahap kehidupan, dan jenis kelamin.**

### 1. Definisi kesamaan pasangan istilah MP

* Bangun ontologi MP dan hitung Information Content (IC) untuk setiap istilah:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   Istilah di bawah persentil IC ke-5 ditetapkan ke IC=0.

* Untuk setiap pasangan istilah MP, temukan nenek moyang umum paling spesifik (MICA) dan gunakan IC-nya sebagai kesamaan Resnik.  

* Untuk dua istilah MP, hitung indeks Jaccard dari himpunan nenek moyangnya.  

* Definisikan kesamaan pasangan istilah MP sebagai `sqrt(Resnik * Jaccard)`.

### 2. Pembobotan berdasarkan kesesuaian metadata fenotipe

* Terapkan bobot berdasarkan metadata fenotipe: genotipe, tahap kehidupan, dan jenis kelamin.

* Untuk setiap pasangan gen, buat matriks kesamaan istilah MP × istilah MP.  

* Kalikan dengan bobot 0.2, 0.5, 0.75, 1.0 untuk 0, 1, 2, 3 kecocokan genotipe/tahap kehidupan/jenis kelamin.

### 3. Penskalaan Phenodigm

* Terapkan penskalaan tipe Phenodigm untuk menormalkan kesamaan fenotipe tiap tikus KO ke 0–100:  
   Hitung maksimum/rata-rata teramati, lalu normalisasi dengan maksimum/rata-rata teoretis.  
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Jika penyebut 0, skor ditetapkan ke 0.

---

# ✉️ Kontak
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

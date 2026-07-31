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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** adalah alat web yang memakai data fenotipe tikus KO dari [IMPC](https://www.mousephenotype.org/) untuk **mengekstrak dan memvisualisasikan modul gen berdasarkan kesamaan fenotipe**.  
Alat ini terbuka untuk semua pengguna secara daring 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Dokumentasi ini menjelaskan perilaku **TSUMUGI v1.1.1** saat ini. Aplikasi web publik menggunakan data IMPC **Release 24.0**.

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
> Jika tidak ditemukan gen serupa: `No similar phenotypes were found among the entered genes.`
> Gene List menerima paling banyak 200 gen tersedia yang berbeda. Duplikat dan baris kosong dihapus sebelum penghitungan; simbol yang tidak tersedia dilaporkan dan dikeluarkan. Daftar dengan 201 atau lebih gen tersedia ditolak sebelum data jaringan dimuat.

### 📥 Unduh data mentah
TSUMUGI menyediakan file JSONL terkompresi gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Simbol gen (contoh "1110059G10Rik")  
- Marker accession ID (contoh "MGI:1913452")  
- Nama/ID fenotipe (contoh "fused joints", "MP:0000137")  
- Effect size (`number` atau `null`; contoh 0.0, 1.324)
- Penanda signifikansi (`true` untuk anotasi fenotipe abnormal IMPC; `false` untuk pengukuran terpetakan tanpa abnormalitas signifikan)
- Zigositas ("Homo", "Hetero", "Hemi")  
- Tahap hidup ("Embryo", "Early", "Interval", "Late")  
- Dimorfisme seksual (`None`, `Male`, `Female`)
- Anotasi penyakit (contoh [] atau "Premature Ovarian Failure 18")

Contoh:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Pasangan gen (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (konteks MICA dengan metadata yang cocok: istilah MP, tahap hidup, zigositas, dan label jenis kelamin)
- `phenotype_similarity_score` (skor Phenodigm, 0–100)

Contoh:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## Catatan interpretasi

- **Konteks bersama:** Setiap item `phenotype_shared_annotations` adalah leluhur bersama paling informatif (MICA) dari dua anotasi MP signifikan dengan label zigositas, tahap hidup, dan jenis kelamin yang sama. Ini tidak selalu berarti kedua gen memiliki istilah MP daun yang sama sebagai anotasi langsung. MICA yang sama dapat muncul sebagai konteks terpisah bila metadatanya berbeda.
- **Aturan tampilan:** Halaman Gene dan Phenotype menampilkan pasangan dengan sedikitnya tiga konteks fenotipe abnormal bersama dan skor kesamaan di atas 0. Gene List memerlukan sedikitnya satu konteks bersama di antara gen yang dimasukkan. Ini adalah aturan tampilan, bukan kriteria signifikansi statistik.
- **Tampilan kesamaan:** `phenotype_similarity_score` yang didistribusikan adalah skor Phenodigm 0–100. Aplikasi web menskalakan ulang nilai yang tersedia pada setiap jaringan menjadi 1–100; nilai slider dan tooltip ant halaman bukan skala absolut yang dapat dibandingkan.
- **Tampilan effect size:** TSUMUGI mengambil nilai absolut effect size IMPC, menerapkan `log1p`, lalu menskalakan nilai fenotipe target menjadi 1–100. Nilai ini hanya membantu pemeringkatan dalam halaman, bukan effect size mentah, dan tidak dapat dibandingkan langsung ant halaman fenotipe. Nilai yang hilang tetap berupa JSON `null` dan node ditampilkan putih.
- **Modul:** Modul adalah kelompok visual, bukan bukti jalur molekuler atau kompleks protein. `Similarity` memakai komponen terhubung dan `Top-level MP` memakai kelompok berbasis ontologi; modul soft/fuzzy pada halaman Gene memungkinkan keanggotaan ganda. Filter jumlah node modul hanya membatasi modul yang ditampilkan.
- **Label jenis kelamin:** `Female` berarti hanya P-value efek KO betina yang ≤ 0.0001; `Male` berarti hal yang sama untuk efek KO jantan. Kedua opsi saling eksklusif di antarmuka dan tidak menggantikan uji formal interaksi jenis kelamin×genotipe.
- **Sorotan fenotipe:** Varian metadata dari fenotipe yang sama digabung menjadi satu opsi. Jika Human Disease dan satu atau lebih sorotan fenotipe bertumpang tindih pada sebuah gen, kategorinya ditampilkan sebagai cincin konsentris.
- **Sorotan penyakit:** Anotasi dari IMPC Disease Models Portal merupakan bukti kemiripan model dan tidak dengan sendirinya menetapkan hubungan kausal gen–penyakit pada manusia.
- **Catatan tidak signifikan:** Catatan ini mewakili pengukuran terpetakan tanpa anotasi abnormal signifikan pada kondisi tersebut. Catatan ini tidak membuktikan normalitas atau ketiadaan fenotipe; `disease_annotation` tetap kosong.
- **Makna skor:** Skor TSUMUGI bukan P-value, effect size, afinitas ikatan, atau bukti interaksi gen kausal.

# 🌐 Jaringan

Halaman berpindah dan menggambar jaringan secara otomatis sesuai input.

> [!IMPORTANT]
> Halaman Gene dan Phenotype menampilkan pasangan dengan sedikitnya tiga konteks fenotipe abnormal bersama dan skor kesamaan di atas 0; Gene List memerlukan sedikitnya satu konteks bersama di antara gen yang dimasukkan. Ini adalah aturan tampilan, bukan kriteria signifikansi statistik.

### Panel jaringan
**Node** mewakili gen. Klik untuk melihat daftar fenotipe abnormal; seret untuk memindahkan.  
**Edge** klik untuk melihat detail fenotipe bersama.  
**Module** menggambarkan sub-jaringan gen. Klik modul untuk melihat fenotipe gen di dalamnya; seret modul agar tidak saling tumpang tindih.
Halaman Gene menggunakan modul Top-level MP soft/fuzzy, sehingga satu gen dapat berada dalam beberapa modul. Halaman Phenotype dan Gene List dapat beralih antara modul `Similarity` berbasis komponen terhubung dan modul `Top-level MP`.

### Panel kontrol
Menyesuaikan tampilan jaringan di panel kiri.

#### Filter kesamaan fenotipe
`Phenotypes similarity` memfilter edge berdasarkan nilai kesamaan yang ditampilkan. `phenotype_similarity_score` yang didistribusikan berkisar 0–100, tetapi setiap jaringan yang ditampilkan diskalakan ulang menjadi 1–100; nilai dari halaman berbeda tidak dapat dibandingkan langsung.
> Cara hitung: 👉 [🔍 Cara kami menghitung kesamaan fenotipe](#-how-we-calculate-phenotypically-similar-genes)

#### Filter effect size
`Effect size` memfilter node berdasarkan nilai tampilan khusus halaman. TSUMUGI mengambil nilai absolut effect size IMPC, menerapkan `log1p`, lalu menskalakan nilai fenotipe target menjadi 1–100. Ini adalah alat pemeringkatan dalam halaman, bukan effect size mentah, dan tidak dapat dibandingkan ant halaman fenotipe.
Effect size yang hilang diserialisasi dalam JSONL sebagai JSON standar `null`, tetap bermakna sebagai nilai hilang alih-alih diubah menjadi nol, dan node terkait ditampilkan berwarna putih.
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
#### Tampilan modul
Definisi modul dan modul yang terlihat dapat dipilih di panel kanan. Batas modul dapat disembunyikan tanpa menghapus gen atau edge dari jaringan.

#### Highlight: Phenotype
Menyorot gen berdasarkan anotasi fenotipe. Varian metadata dari fenotipe yang sama digabung menjadi satu opsi. Jika Human Disease dan sedikitnya satu sorotan fenotipe bertumpang tindih pada sebuah gen, kategorinya ditampilkan sebagai cincin konsentris.

#### Highlight: Human Disease
Menyorot gen KO yang memiliki anotasi model penyakit di IMPC Disease Models Portal. Anotasi ini menunjukkan kemiripan model dan tidak dengan sendirinya menetapkan hubungan kausal gen–penyakit pada manusia.

#### Search: Specific Gene
Cari nama gen dalam jaringan.

#### Layout & Display
Atur tata letak, ukuran font, ketebalan edge, repulsi node (Cose).

#### Export
Ekspor PNG, JPG, SVG, CSV, atau GraphML. Bingkai modul dapat disertakan dalam PNG, JPG, dan SVG. CSV memuat penetapan modul Similarity atau Top-level MP yang aktif beserta daftar fenotipe; GraphML kompatibel dengan Cytoscape.

# 🛠 Antarmuka Baris Perintah

CLI TSUMUGI memungkinkan penggunaan data IMPC terbaru secara lokal, dengan filter dan output yang lebih rinci dibandingkan versi web.

## Fitur

- Hitung ulang dengan `statistical-results-ALL.csv.gz` IMPC (opsional `mp.obo`, `impc_phenodigm.csv`).  
- Filter berdasarkan anotasi MP signifikan atau pengukuran terpetakan yang tidak signifikan.
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
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: filter pasangan gen atau gen berdasarkan anotasi MP signifikan atau pengukuran terpetakan yang tidak signifikan
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
> Semua perintah kecuali `tsumugi run` memerlukan `pairwise_similarity_annotations.jsonl.gz` atau `genewise_phenotype_annotations.jsonl.gz`.
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
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Sertakan gen/pasangan gen yang memiliki istilah MP yang ditentukan (termasuk turunan).

#### `-e MP_ID`, `--exclude MP_ID`
Kembalikan gen/pasangan gen yang diukur untuk istilah MP (termasuk turunan) tetapi tidak menunjukkan fenotipe signifikan. Memerlukan `-a/--genewise_annotations`.

> [!CAUTION]
> Catatan tidak signifikan tidak membuktikan bahwa hewan normal atau fenotipe tidak ada. Catatan ini hanya menyatakan bahwa pengukuran terpetakan tidak menghasilkan anotasi abnormal signifikan pada kondisi tersebut.

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
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Ekstrak pasangan yang MP:0001146 dan turunannya diukur tanpa anomali signifikan
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

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
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
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
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
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

tsumugi genes --genewise --keep genes.txt   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

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
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
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
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

CLI mendukung STDIN/STDOUT, sehingga Anda bisa merangkai perintah:  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 Cara kami menghitung kesamaan fenotipe

## Sumber data

Kami menggunakan dataset IMPC [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Kolom dataset: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Pra-pemrosesan

TSUMUGI memperlakukan `mp_term_id` IMPC yang tidak kosong sebagai anotasi fenotipe abnormal IMPC. Pengukuran terpetakan tanpa anotasi abnormal signifikan juga dipertahankan untuk kueri pengecualian yang mempertimbangkan apakah pengukuran dilakukan.
Untuk pengukuran tidak signifikan, setiap istilah non-root paling spesifik dalam `intermediate_mp_term_id` yang tidak dapat dibandingkan secara ontologis dengan istilah terpilih lainnya dikeluarkan sebagai rekaman terpisah. Pengukuran yang hanya dipetakan ke `MP:0000001` atau tidak memiliki istilah MP valid tidak dikeluarkan karena tidak mendukung kueri khusus fenotipe.

- Zigositas diubah menjadi `Homo`, `Hetero`, atau `Hemi`.
- `Female` diberikan jika hanya `female_ko_effect_p_value` yang ≤ 0.0001, dan `Male` jika hanya `male_ko_effect_p_value` yang ≤ 0.0001; selain itu diberikan `None`.
- Nilai absolut effect size digunakan. Nilai yang hilang tetap hilang dan diserialisasi sebagai `null` dalam JSON.

## Kesamaan fenotipe

TSUMUGI menerapkan rumus skor asli PhenoDigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) untuk membandingkan profil fenotipe gen tikus KO IMPC di dalam Mammalian Phenotype Ontology.

> [!NOTE]
> TSUMUGI menggunakan rumus skor PhenoDigm, tetapi tidak menjalankan pipeline lintas spesies HPO-MP/ZP OWLSim asli. TSUMUGI membandingkan anotasi MP dari gen tikus KO IMPC.

### 1. Definisi kesamaan pasangan istilah MP

* Bangun ontologi MP dan hitung Information Content (IC) dari anotasi IMPC yang signifikan:
   `IC(term) = -log2(|anotasi yang dipropagasikan ke istilah| / |semua anotasi signifikan|)`
   Setiap anotasi langsung dipropagasikan ke istilah MP yang dianotasi dan seluruh leluhurnya.

* Untuk setiap pasangan istilah MP, cari leluhur bersama dengan IC berbasis anotasi tertinggi. Jika seri, pilih secara deterministik kandidat dengan keturunan transitif paling sedikit dalam ontologi MP, lalu ID istilah MP yang paling kecil secara leksikografis. IC MICA yang dipilih menjadi kesamaan Resnik. Tie-break ini tidak mengubah skor kesamaan atau skema output.
   Kandidat yang seri memiliki skor numerik pasangan istilah yang sama, tetapi label MICA yang dipilih dapat mengubah jumlah konteks bersama dan akibatnya kelayakan untuk ditampilkan.

* Untuk dua istilah MP, hitung indeks Jaccard dari himpunan atribut terinferensi, yang terdiri dari istilah itu sendiri dan semua leluhurnya.

* Definisikan kesamaan pasangan istilah MP sebagai `sqrt(Resnik * Jaccard)`.

### 2. Matriks kesamaan pasangan gen

* Untuk setiap pasangan gen, buat matriks kesamaan istilah MP × istilah MP dari skor pasangan istilah.

* MICA hanya dicatat dalam `phenotype_shared_annotations` jika zigositas, tahap hidup, dan label jenis kelamin cocok. Metadata ini tidak membobot skor PhenoDigm.

### 3. Penskalaan Phenodigm

* Terapkan penskalaan maksimum/rata-rata PhenoDigm untuk menormalkan kesamaan setiap pasangan gen tikus KO ke 0–100:
   Hitung maksimum dan rata-rata best match yang teramati, lalu normalisasi dengan skor optimal self match simetris dari kedua gen.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Jika penyebut 0, skor ditetapkan ke 0.

Skor yang dihasilkan mengukur kesamaan profil fenotipe. Skor ini bukan P-value, effect size, afinitas ikatan, atau bukti interaksi kausal antar gen.

---

# ✉️ Kontak
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Sitasi

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

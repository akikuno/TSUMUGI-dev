> ⚠️ Đây là bản dịch do AI sinh ra; nếu có điểm chưa rõ, hãy xem bản gốc (README.md).  
> Bản gốc: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** là công cụ web dùng dữ liệu KO chuột của [IMPC](https://www.mousephenotype.org/) để **trích xuất và trực quan hóa mô-đun gen dựa trên độ tương đồng biểu hiện**.  
Mở cho mọi người sử dụng trực tuyến 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Tài liệu này mô tả hoạt động hiện tại của **TSUMUGI v1.1.1**. Ứng dụng web công khai sử dụng dữ liệu IMPC **Release 24.0**.

**TSUMUGI (紡ぎ)** mang ý nghĩa “dệt các nhóm gen tạo nên kiểu hình”.

# 📖 Cách dùng TSUMUGI

TSUMUGI hỗ trợ ba kiểu nhập.

### Kiểu hình (Phenotype)
Nhập kiểu hình quan tâm để tìm **các gen có hồ sơ kiểu hình KO tương tự**.  
Tên kiểu hình dựa trên [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Danh sách kiểu hình](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gen (Gene)
Chỉ định một gen để tìm **các gen khác có kiểu hình KO tương tự**.  
Theo ký hiệu [MGI](http://www.informatics.jax.org/).  
👉 [Danh sách gen](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Danh sách gen (Gene List)
Nhiều gen (mỗi dòng một gen) để tìm **trong danh sách đó**.  
> [!CAUTION]  
> Không tìm thấy: `No similar phenotypes were found among the entered genes.`  
> Nếu mạng được tạo có từ 200 gen trở lên: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Tải dữ liệu thô
TSUMUGI cung cấp file JSONL nén gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Ký hiệu gen (ví dụ "1110059G10Rik")  
- Marker accession ID (ví dụ "MGI:1913452")  
- Tên/ID kiểu hình (ví dụ "fused joints", "MP:0000137")  
- Effect size (`number` hoặc `null`; ví dụ 0.0, 1.324)
- Ý nghĩa thống kê (True/false)  
- Zygosity ("Homo", "Hetero", "Hemi")  
- Giai đoạn sống ("Embryo", "Early", "Interval", "Late")  
- Khác biệt giới tính ("", "Male", "Female")  
- Chú thích bệnh (ví dụ [] hoặc "Premature Ovarian Failure 18")

Ví dụ:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Cặp gen (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (giai đoạn sống, zygosity, khác biệt giới tính) cho các kiểu hình chung  
- `phenotype_similarity_score`: điểm Resnik→Phenodigm (0–100)

Ví dụ:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Mạng

Trang chuyển và vẽ mạng tự động theo đầu vào.

> [!IMPORTANT]  
> Minh họa các cặp gen có **≥3 kiểu hình bất thường chung** và **độ tương đồng > 0.0**.

### Bảng mạng
**Nút**: gen. Nhấp để xem danh sách kiểu hình bất thường; kéo để sắp xếp.  
**Cạnh**: nhấp để xem chi tiết kiểu hình chung.  
**Module** bao quanh các mạng con gen. Nhấp để liệt kê kiểu hình của các gen trong module; kéo module để di chuyển và tránh chồng lấp.
Trang Gene sử dụng module Top-level MP soft/fuzzy, vì vậy một gen có thể thuộc nhiều module. Trang Phenotype và Gene List có thể chuyển giữa module `Similarity` dựa trên thành phần liên thông và module `Top-level MP`.

### Bảng điều khiển
Điều chỉnh hiển thị mạng ở bảng trái.

#### Lọc theo độ tương đồng kiểu hình
`Phenotypes similarity` đặt ngưỡng cạnh dựa trên điểm Resnik→Phenodigm.  
> Cách tính: 👉 [🔍 Cách tính nhóm gen tương đồng kiểu hình](#-cách-tính-nhóm-gen-tương-đồng-kiểu-hình)

#### Lọc theo effect size
`Effect size` lọc nút theo độ lớn của effect size từ IMPC khi có dữ liệu.
Effect size bị thiếu được tuần tự hóa trong JSONL thành giá trị JSON chuẩn `null`, vẫn mang ngữ nghĩa là giá trị thiếu thay vì chuyển thành 0, và các nút tương ứng được hiển thị màu trắng.
> Ẩn cho kiểu hình nhị phân (ví dụ [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); danh sách nhị phân [tại đây](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) hoặc khi nhập một gen.

#### Chỉ định kiểu gen
- `Homo`
- `Hetero`
- `Hemi`

#### Chỉ định giới tính
- `Female`
- `Male`

#### Chỉ định giai đoạn sống
- `Embryo`
- `Early` (0–16 tuần)
- `Interval` (17–48 tuần)
- `Late` (49+ tuần)

### Bảng đánh dấu
#### Hiển thị module
Chọn định nghĩa module và module hiển thị trong bảng bên phải. Có thể ẩn đường viền module mà không loại bỏ gen hoặc cạnh khỏi mạng.

#### Highlight: Human Disease
Tô sáng gen liên quan bệnh (dữ liệu IMPC Disease Models Portal).

#### Search: Specific Gene
Tìm tên gen trong mạng.

#### Layout & Display
Điều chỉnh bố cục, cỡ chữ, độ dày cạnh, lực đẩy nút (Cose).

#### Export
Xuất PNG, JPG, SVG, CSV hoặc GraphML. Có thể đưa khung module vào PNG, JPG và SVG. CSV ghi nhận phép gán module Similarity hoặc Top-level MP đang hoạt động cùng danh sách kiểu hình; GraphML tương thích Cytoscape.

# 🛠 Giao diện dòng lệnh

CLI của TSUMUGI cho phép dùng dữ liệu IMPC mới nhất tải về cục bộ, với bộ lọc và đầu ra chi tiết hơn so với bản web.

## Tính năng

- Tính lại bằng `statistical-results-ALL.csv.gz` của IMPC (tùy chọn `mp.obo`, `impc_phenodigm.csv`).  
- Lọc theo có/không có thuật ngữ MP.  
- Lọc theo danh sách gene (ngăn cách bằng dấu phẩy hoặc file text).  
- Đầu ra: GraphML (`tsumugi build-graphml`), gói webapp offline (`tsumugi build-webapp`).

## Cài đặt

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Sẵn sàng khi `tsumugi --version` hiển thị phiên bản.

## Lệnh có sẵn

- `tsumugi run`: tính lại mạng từ dữ liệu IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: lọc cặp gene hoặc gene có/không có thuật ngữ MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: lọc theo số lượng phenotype (pairwise/genewise)  
- `tsumugi score (--min/--max)`: lọc theo điểm tương đồng (pairwise)  
- `tsumugi genes --keep/--drop`: giữ/bỏ theo danh sách gene (dấu phẩy hoặc file text)  
- `tsumugi life-stage --keep/--drop`: lọc theo giai đoạn sống (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: lọc theo giới tính (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: lọc theo kiểu hợp tử (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: tạo GraphML (Cytoscape, v.v.)  
- `tsumugi build-webapp`: tạo tài nguyên web TSUMUGI (HTML/CSS/JS cục bộ)

> [!NOTE]
> Tất cả các subcommand lọc đều xuất JSONL ra STDOUT.  
> Dùng `>` để ghi ra file.

> [!IMPORTANT]
> Tất cả lệnh, trừ `tsumugi run`, yêu cầu `pairwise_similarity_annotations.jsonl.gz` hoặc `genewise_phenotype_annotations.jsonl.gz`.
> Cả hai file đều có thể tải từ [trang chủ TSUMUGI](https://larc-tsukuba.github.io/tsumugi/).

## Cách dùng

### Tính lại từ dữ liệu IMPC (`tsumugi run`)
Nếu bỏ `--mp_obo`, TSUMUGI dùng `data-version: releases/2025-08-27/mp.obo` đi kèm.  
Nếu bỏ `--impc_phenodigm`, TSUMUGI dùng file lấy ngày 2025-10-01 từ [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Đầu ra: `./tsumugi-output` chứa chú giải genewise (genewise_phenotype_annotations.jsonl.gz), dữ liệu tương đồng pairwise (pairwise_similarity_annotations.jsonl.gz) và tài nguyên trực quan (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> Thư mục `TSUMUGI-webapp` có script mở theo hệ điều hành; nhấp đúp để mở webapp cục bộ:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Lọc theo thuật ngữ MP (`tsumugi mp --include/--exclude`)
Trích xuất các cặp gene (hoặc gene) có phenotype quan tâm, hoặc các cặp đã đo nhưng không có bất thường đáng kể.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Bao gồm gene/cặp gene có thuật ngữ MP chỉ định (tính cả hậu duệ).

#### `-e MP_ID`, `--exclude MP_ID`
Trả về gene/cặp gene đã đo cho thuật ngữ MP (tính cả hậu duệ) nhưng không có phenotype đáng kể. Yêu cầu `-a/--genewise_annotations`.

#### `-g`, `--genewise`
Lọc ở mức gene. Đọc `genewise_phenotype_annotations.jsonl(.gz)`. Khi dùng `--genewise`, hãy chỉ định `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Lọc ở mức cặp gene. Dùng `pairwise_similarity_annotations.jsonl(.gz)`. Nếu bỏ `--in`, đọc từ STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Đường dẫn tới ontology Mammalian Phenotype (mp.obo). Nếu bỏ, dùng `data/mp.obo` đi kèm.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Đường dẫn tới file genewise (JSONL/.gz). Bắt buộc với `--exclude`; cũng dùng với `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

#### `--life_stage LIFE_STAGE`
Bộ lọc thêm theo giai đoạn sống. Giá trị: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Bộ lọc thêm theo dimorphism giới tính. Dùng giá trị trong annotation (ví dụ: `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Bộ lọc thêm theo zygosity. Giá trị: `Homo`, `Hetero`, `Hemi`.

```bash
# Chỉ trích xuất các cặp gene có MP:0001146 (abnormal testis morphology) hoặc hậu duệ (ví dụ: MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Trích xuất các cặp mà MP:0001146 và hậu duệ được đo nhưng không có bất thường đáng kể
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

# Trích xuất annotation có ý nghĩa ở mức gene chứa MP:0001146 (tính cả hậu duệ)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Trích xuất gene đã đo cho MP:0001146 (tính cả hậu duệ) nhưng không có bất thường đáng kể
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Các thuật ngữ MP hậu duệ của ID chỉ định cũng được tính.**  
> Ví dụ, nếu chỉ định `MP:0001146 (abnormal testis morphology)`, các thuật ngữ hậu duệ như `MP:0004849 (abnormal testis size)` cũng được tính.

### Lọc theo số lượng phenotype (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Lọc gene hoặc cặp gene theo số lượng phenotype. Cần ít nhất `--min` hoặc `--max`.

#### `-g`, `--genewise`
Lọc theo số phenotype có ý nghĩa trên mỗi gene. Cần `-a/--genewise_annotations` với `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Lọc theo số phenotype chung trên mỗi cặp. Nếu bỏ `--in`, đọc từ STDIN.

#### `--min MIN`, `--max MAX`
Ngưỡng dưới/trên cho số lượng phenotype. Chỉ một ngưỡng cũng đủ cho lọc một phía.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Đường dẫn tới file genewise (JSONL/.gz). Bắt buộc khi dùng `--genewise`.

- Phenotype chung theo cặp:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Phenotype theo gene (cần genewise):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
```

Có thể chỉ dùng `--min` hoặc `--max`.

### Lọc theo điểm tương đồng (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Lọc cặp gene theo `phenotype_similarity_score` (0–100). Cần ít nhất `--min` hoặc `--max`.

#### `--min MIN`, `--max MAX`
Ngưỡng dưới/trên của điểm số. Chỉ một ngưỡng cũng đủ cho lọc một phía.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

Có thể chỉ dùng `--min` hoặc `--max`.

### Lọc theo danh sách gene (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Chỉ giữ các cặp chứa gene chỉ định trong file text.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Loại bỏ các cặp chứa gene chỉ định trong file text.

#### `-g`, `--genewise`
Lọc theo symbol gene do người dùng cung cấp.

#### `-p`, `--pairwise`
Lọc theo cặp gene do người dùng cung cấp.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

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

### Lọc theo giai đoạn sống (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Chỉ giữ giai đoạn sống chỉ định (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Loại bỏ giai đoạn sống chỉ định.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Lọc theo giới tính (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Chỉ giữ giới tính chỉ định (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Loại bỏ giới tính chỉ định.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Lọc theo zygosity (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Chỉ giữ zygosity chỉ định (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Loại bỏ zygosity chỉ định.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### Xuất GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Đường dẫn tới file genewise (JSONL/.gz). Bắt buộc.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Đường dẫn tới file pairwise (JSONL/.gz). Nếu bỏ, đọc từ STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Đường dẫn tới file genewise (JSONL/.gz). Bắt buộc.

#### `-o OUT`, `--out OUT`
Thư mục đầu ra cho bundle webapp (HTML/CSS/JS + dữ liệu mạng). Không dùng tên file có đuôi mở rộng.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

CLI hỗ trợ STDIN/STDOUT, vì vậy bạn có thể nối lệnh:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cách tính nhóm gen tương đồng kiểu hình

## Nguồn dữ liệu

Chúng tôi dùng bộ dữ liệu IMPC [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Thông tin cột dữ liệu: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Tiền xử lý

Trích xuất các cặp gene–kiểu hình có P-value ở chuột KO (`p_value`, `female_ko_effect_p_value` hoặc `male_ko_effect_p_value`) ≤ 0.0001.  
- Gắn nhãn kiểu hình đặc hiệu kiểu gen là `homo`, `hetero` hoặc `hemi`.  
- Gắn nhãn kiểu hình đặc hiệu giới tính là `female` hoặc `male`.

## Độ tương đồng kiểu hình

TSUMUGI áp dụng công thức chấm điểm gốc của PhenoDigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) để so sánh hồ sơ kiểu hình của gen chuột KO IMPC trong Mammalian Phenotype Ontology.

> [!NOTE]
> TSUMUGI dùng công thức chấm điểm PhenoDigm nhưng không chạy pipeline HPO-MP/ZP OWLSim liên loài gốc. Công cụ so sánh annotation MP của các gen chuột KO IMPC.

### 1. Định nghĩa độ tương đồng cặp thuật ngữ MP

* Xây dựng ontology MP và tính Information Content (IC) từ các annotation IMPC có ý nghĩa:
   `IC(term) = -log2(|annotation được lan truyền tới thuật ngữ| / |tất cả annotation có ý nghĩa|)`
   Mỗi annotation trực tiếp được lan truyền tới thuật ngữ MP được gán và tất cả tổ tiên của nó.

* Với mỗi cặp thuật ngữ MP, tìm các tổ tiên chung có IC dựa trên annotation cao nhất. Nếu đồng hạng, chọn xác định ứng viên có ít hậu duệ bắc cầu nhất trong ontology MP, sau đó chọn ID thuật ngữ MP nhỏ nhất theo thứ tự từ điển. IC của MICA được chọn là độ tương đồng Resnik. Cách phá hòa này không thay đổi điểm tương đồng hoặc schema đầu ra.

* Với hai thuật ngữ MP, tính chỉ số Jaccard của các tập thuộc tính suy ra, được định nghĩa là chính thuật ngữ đó cùng tất cả tổ tiên.

* Định nghĩa độ tương đồng cặp thuật ngữ MP là `sqrt(Resnik * Jaccard)`.

### 2. Ma trận độ tương đồng cặp gen

* Với mỗi cặp gen, tạo ma trận độ tương đồng thuật ngữ MP × thuật ngữ MP từ điểm của các cặp thuật ngữ.

* Metadata kiểu gen, giai đoạn sống và giới tính được giữ trong annotation kiểu hình chung nhưng không dùng để đặt trọng số cho điểm PhenoDigm.

### 3. Chuẩn hóa Phenodigm

* Áp dụng chuẩn hóa maximum/average của PhenoDigm để đưa độ tương đồng của từng cặp gen chuột KO về 0–100:
   Tính maximum và mean của best match quan sát được, rồi chuẩn hóa bằng điểm optimal self match đối xứng của hai gen.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Nếu mẫu số bằng 0, điểm được đặt về 0.

---

# ✉️ Liên hệ
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Trích dẫn

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  

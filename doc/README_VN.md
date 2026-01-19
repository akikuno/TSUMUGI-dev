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
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** là công cụ web dùng dữ liệu KO chuột của [IMPC](https://www.mousephenotype.org/) để **trích xuất và trực quan hóa mô-đun gen dựa trên độ tương đồng biểu hiện**.  
Mở cho mọi người sử dụng trực tuyến 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

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
> Trên 200: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Tải dữ liệu thô
TSUMUGI cung cấp file JSONL nén gzip.

#### `genewise_phenotype_annotations.jsonl.gz`
- Ký hiệu gen (ví dụ "1110059G10Rik")  
- Marker accession ID (ví dụ "MGI:1913452")  
- Tên/ID kiểu hình (ví dụ "fused joints", "MP:0000137")  
- Effect size (ví dụ 0.0, 1.324)  
- Ý nghĩa thống kê (True/false)  
- Zygosity ("Homo", "Hetero", "Hemi")  
- Giai đoạn sống ("Embryo", "Early", "Interval", "Late")  
- Khác biệt giới tính ("", "Male", "Female")  
- Chú thích bệnh (ví dụ [] hoặc "Premature Ovarian Failure 18")

Ví dụ:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Cặp gen (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: metadata (giai đoạn sống, zygosity, khác biệt giới tính) cho các kiểu hình chung  
- `phenotype_similarity_score`: điểm Resnik→Phenodigm (0–100)

Ví dụ:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Mạng

Trang chuyển và vẽ mạng tự động theo đầu vào.

> [!IMPORTANT]  
> Minh họa các cặp gen có **≥3 kiểu hình bất thường chung** và **độ tương đồng > 0.0**.

### Bảng mạng
**Nút**: gen. Nhấp để xem danh sách kiểu hình bất thường; kéo để sắp xếp.  
**Cạnh**: nhấp để xem chi tiết kiểu hình chung.  
**Module** bao quanh các mạng con gen. Nhấp để liệt kê kiểu hình của các gen trong module; kéo module để di chuyển và tránh chồng lấp.

### Bảng điều khiển
Điều chỉnh hiển thị mạng ở bảng trái.

#### Lọc theo độ tương đồng kiểu hình
`Phenotypes similarity` đặt ngưỡng cạnh dựa trên điểm Resnik→Phenodigm.  
> Cách tính: 👉 [🔍 Cách tính nhóm gen tương đồng kiểu hình](#-cách-tính-nhóm-gen-tương-đồng-kiểu-hình)

#### Lọc theo mức độ nghiêm trọng
`Phenotype severity` lọc nút theo effect size (mức độ nghiêm trọng ở KO). Giá trị lớn hơn = ảnh hưởng mạnh hơn.  
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
#### Highlight: Human Disease
Tô sáng gen liên quan bệnh (dữ liệu IMPC Disease Models Portal).

#### Search: Specific Gene
Tìm tên gen trong mạng.

#### Layout & Display
Điều chỉnh bố cục, cỡ chữ, độ dày cạnh, lực đẩy nút (Cose).

#### Export
Xuất PNG/CSV/GraphML. CSV có ID mô-đun và danh sách kiểu hình; GraphML tương thích Cytoscape.

# 🛠 Phiên bản dòng lệnh

Phát hành này thêm CLI: tự tải dữ liệu IMPC mới, chạy lại TSUMUGI, lọc linh hoạt, xuất GraphML hoặc webapp offline.

- Tính lại với IMPC `statistical-results-ALL.csv.gz` (tùy chọn `mp.obo`, `impc_phenodigm.csv`)  
- Lọc theo có/không có thuật ngữ MP  
- Lọc theo danh sách gen (CSV hoặc tệp văn bản)  
- Đầu ra: GraphML (`tsumugi build-graphml`), gói webapp offline (`tsumugi build-webapp`)

## Lệnh khả dụng
- `tsumugi run`: tính lại mạng từ dữ liệu IMPC  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: lọc cặp gen hoặc từng gen theo thuật ngữ MP  
- `tsumugi count --pairwise/--genewise (--min/--max)`: lọc theo số kiểu hình (cặp/gen)  
- `tsumugi score (--min/--max)`: lọc theo điểm tương đồng kiểu hình (cặp gen)
- `tsumugi genes --keep/--drop`: giữ/bỏ theo danh sách gen  
- `tsumugi life-stage --keep/--drop`: lọc theo giai đoạn sống  
- `tsumugi sex --keep/--drop`: lọc theo giới tính  
- `tsumugi zygosity --keep/--drop`: lọc theo zygosity  
- `tsumugi build-graphml`: tạo GraphML  
- `tsumugi build-webapp`: tạo asset webapp TSUMUGI

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

## Ví dụ thường dùng

### Tính lại từ dữ liệu IMPC (`tsumugi run`)
Nếu bỏ `--mp_obo`, dùng `data-version: releases/2025-08-27/mp.obo` kèm theo.  
Nếu bỏ `--impc_phenodigm`, dùng file lấy ngày 01/10/2025 từ [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Đầu ra: `./tsumugi-output` chứa genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz và gói webapp (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> `TSUMUGI-webapp` bao gồm script khởi động theo OS; nhấp đúp để mở webapp cục bộ:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Lọc theo thuật ngữ MP (`tsumugi mp --include/--exclude`)
Chỉ trích xuất các cặp gen chứa kiểu hình quan tâm, hoặc các cặp đã đo các kiểu hình đó nhưng không có bất thường đáng kể.

- `--pairwise` (mặc định nếu không đặt): xuất theo cặp gen. Dùng `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: xuất theo từng gen. Dùng `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (bắt buộc với `--exclude`, khuyến nghị với `--include`).

```bash
# Chỉ lấy các cặp bao gồm MP:0001146 (abnormal testis morphology) hoặc các thuật ngữ hậu duệ (ví dụ: MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Lấy các cặp đã đo MP:0001146 và các thuật ngữ hậu duệ nhưng không ghi nhận bất thường đáng kể
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Lấy các chú giải có ý nghĩa ở mức gen chứa MP:0001146 (bao gồm thuật ngữ hậu duệ)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Lấy các gen đã đo MP:0001146 (bao gồm thuật ngữ hậu duệ) nhưng không ghi nhận bất thường đáng kể
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Các thuật ngữ MP hậu duệ của ID được chỉ định cũng được xử lý.**  
> Ví dụ, khi chỉ định `MP:0001146 (abnormal testis morphology)`, các thuật ngữ hậu duệ như `MP:0004849 (abnormal testis size)` cũng được tính đến.

### Lọc theo số kiểu hình (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- Kiểu hình chung mỗi cặp:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Kiểu hình mỗi gen (cần genewise):
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` hoặc `--max` có thể dùng riêng.


### Lọc theo điểm tương đồng (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Lọc cặp gen theo `phenotype_similarity_score` (0–100). Cần ít nhất một trong `--min` hoặc `--max`.

#### `--min MIN`, `--max MAX`
Giới hạn dưới/trên của điểm. Có thể dùng một trong hai để lọc một phía.

#### `--in IN`
Đường dẫn tới file anotations pairwise (JSONL/.gz); nếu bỏ qua sẽ đọc từ STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` hoặc `--max` dùng riêng cũng được.

### Lọc theo danh sách gen (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Giai đoạn sống / giới tính / zygosity
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### Xuất GraphML / webapp
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
```
Pipeline mẫu: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Cách tính nhóm gen tương đồng kiểu hình

## Nguồn dữ liệu
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Trường thông tin: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Tiền xử lý
Chọn cặp gen–kiểu hình có P ≤ 0.0001 (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`).  
- Zygosity: `homo`, `hetero`, `hemi`  
- Giới tính: `female`, `male`

## Độ tương đồng kiểu hình
TSUMUGI hiện theo cách tiếp cận gần với Phenodigm. Chúng tôi tính độ tương đồng **Resnik** giữa các thuật ngữ MP và độ tương đồng **Jaccard** giữa các tập tổ tiên, rồi kết hợp bằng **trung bình hình học**. Khác biệt chính so với Phenodigm gốc là thêm trọng số metadata (zygosity, life stage, sexual dimorphism) khi tổng hợp.

1. Xây dựng ontology MP và tính IC:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   Các thuật ngữ dưới phân vị 5 của IC được đặt về 0.
2. Với mỗi cặp thuật ngữ MP, tìm tổ tiên chung cụ thể nhất (MICA) và dùng IC của nó làm Resnik.  
   Tính chỉ số Jaccard trên các tập tổ tiên.  
   Độ tương đồng thuật ngữ = `sqrt(Resnik * Jaccard)`.
3. Với mỗi cặp gen, xây dựng ma trận thuật ngữ×thuật ngữ và áp dụng trọng số metadata.  
   Mức khớp zygosity/giai đoạn sống/dị hình giới tính cho trọng số 0.25/0.5/0.75/1.0 ứng với 0/1/2/3 khớp.
4. Áp dụng chuẩn hóa kiểu Phenodigm về 0–100:  
   Dùng max theo hàng/cột để lấy max và mean thực tế.  
   Chuẩn hóa theo max/mean lý thuyết dựa trên IC và tính  
   `Score = 100 * (normalized_max + normalized_mean) / 2`.  
   Nếu mẫu số lý thuyết bằng 0, đặt về 0.

# ✉️ Liên hệ
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose

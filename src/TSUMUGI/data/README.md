# Bundled data provenance

This directory contains the reference data used when the corresponding
`tsumugi run` option is omitted. The IMPC statistical-results input is not
bundled and must be supplied by the user.

## Data inventory

| File | Version or snapshot | Retrieved | Source | Purpose |
| --- | --- | --- | --- | --- |
| `mp.obo` | `data-version: releases/2026-07-22/mp.obo`; upstream modified 2026-08-10 12:00:57 UTC | 2026-08-13 | [OBO Foundry PURL](https://purl.obolibrary.org/obo/mp.obo) | MP term names, ancestry, and information-content calculations |
| `impc_phenodigm.csv` | Portal content updated 2025-05-15 | 2025-10-01 | [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/) | Mouse-model to human-disease similarity annotations |
| `mgi/MGI_GenePheno.rpt` | Upstream modified 2026-08-10 12:00:37 UTC | 2026-08-13 16:29:04 JST | [MGI report](https://www.informatics.jax.org/downloads/reports/MGI_GenePheno.rpt) | Marker, genotype, strain, and abnormal MP annotations |
| `mgi/MGI_PhenotypicAllele.rpt` | Upstream modified 2026-08-10 12:00:55 UTC | 2026-08-13 16:29:04 JST | [MGI report](https://www.informatics.jax.org/downloads/reports/MGI_PhenotypicAllele.rpt) | Allele type and molecular-mutation classification used for strict LOF selection |
| `mgi/MGI_Pheno_Sex.rpt` | Upstream modified 2026-08-10 12:00:54 UTC | 2026-08-13 16:29:04 JST | [MGI report](https://www.informatics.jax.org/downloads/reports/MGI_Pheno_Sex.rpt) | Sex-specific phenotype annotations |

The MGI snapshot is the official report set available when the files were
retrieved. MGI reports do not carry a release number, so the upstream
`Last-Modified` time and local SHA-256 digest identify the exact snapshot.
Machine-readable provenance is stored in
[`mgi/input-provenance.json`](mgi/input-provenance.json).

## Integrity checks

| File | SHA-256 |
| --- | --- |
| `mp.obo` | `5206452e73771e241837f905b708804f228f422a1575340b3e489e46bc52bf56` |
| `impc_phenodigm.csv` | `6cf5e48fa7455a67d760e44c292eae2e8337cbb12bfcc98f9bffd439886336b1` |
| `mgi/MGI_GenePheno.rpt` | `a80836cc0a4496a80b8750ea5ac7013618cf17359b89ce6c9638a89e46b7cf8b` |
| `mgi/MGI_PhenotypicAllele.rpt` | `b1a6cf6514bb6e4dbd4fca975809fb504c7ba5354a7a073259aa3b9dbd5aead0` |
| `mgi/MGI_Pheno_Sex.rpt` | `774c20c48ae0ead6802a74dc554b69d730c4bee69af3759af36db0ff54a8744b` |

## External runtime input

`tsumugi run` requires an IMPC Release 24.0
`statistical-results-ALL.csv.gz` file. Download it from the
[IMPC Release 24.0 results directory](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results/statistical-results-ALL.csv.gz).
The default MGI-integrated pipeline requires the `strain_name` column in this
file. The IMPC input is kept external because it is substantially larger than
the bundled reference files.

## Updating bundled data

When replacing a bundled file, update this inventory and its SHA-256 digest in
the same change. For an MGI update, replace all three reports together and also
record the retrieval time, upstream `Last-Modified` time, and digest in
`mgi/input-provenance.json`. Validate the complete report set before release.

## Licensing and attribution

The MP ontology and MGI reports are provided by Mouse Genome Informatics at The
Jackson Laboratory. MGI data and annotations are distributed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/);
see the [MGI copyright and warranty notice](https://www.informatics.jax.org/mgihome/other/copyright.shtml).
Refer to the linked IMPC and Disease Models Portal sites for their terms and
attribution requirements.

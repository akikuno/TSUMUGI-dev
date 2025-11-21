<!-- TEMPLATE
# v0.0.0 (yyyy-mm-dd)
## 💥 Breaking
## 📝 Documentation
## 🚀 Performance
## 🌟 New Features
## 🐛 Bug Fixes
## 🔧 Maintenance
## ⛔️ Deprecated
## 🖼️ User Interface
+ COMMIT_MESSAGE  
  Issue: [#XXX](https://github.com/akikuno/TSUMUGI-dev/issues/XXX)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/XXX)]  
-->

<!-- = TODO ====
- [x] 遺伝子aが検索リストに出てこない #86
- [x] Enable the exclusion or extraction of specific phenotypes from the network #36
-->

<!-- ############################################################ # -->

## v0.5.0 (2025-11-22)

## 🌟 New Features

- CLI tooling suite added for offline/pipe-friendly workflows:  
  - `tsumugi run` (main pipeline)  
  - `tsumugi mp --include/--exclude`  
  - `tsumugi n-phenos --pairwise --min --max`  
  - `tsumugi n-phenos --genewise --min --max`  
  - `tsumugi genes --keep --drop`  
  - `tsumugi life-stage --keep --drop`  
  - `tsumugi sex --keep --drop`  
  - `tsumugi zygosity --keep --drop`  
  - `tsumugi build-webapp`  
  - `tsumugi build-graphml`

## 📝 Documentation

- README updated with CLI option descriptions and multilingual links (Japanese, Korean, Simplified/Traditional Chinese, Hindi, Indonesian, Vietnamese, Spanish, French, German, Portuguese).


-------------------------------------------------------------

# Past Releases

<!-- =============================================================
<details>
<summary> v0.X.X (2025-MM-DD) </summary>

</details>
============================================================= -->

<details>
<summary> v0.4.0 (2025-11-12) </summary>

## 💥 Breaking

+ Adopted the Phenodigm/Resnik similarity pipeline so phenotype matching now respects the hierarchical structure of MPO instead of relying on plain Jaccard overlap.  
  Issue: [#71](https://github.com/akikuno/TSUMUGI-dev/issues/71)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/648f2787e3bd705ad921346d8e594a7eb3219eaf)]  

+ Surface common ancestor MP terms on KO mouse edges, filtering out low-information matches to highlight meaningful shared phenotypes.  
  Issue: [#118](https://github.com/akikuno/TSUMUGI-dev/issues/118)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/547506a5762769e6aa698d47f50ce35150869540)]  

+ Pre-compute degree and betweenness centrality for every node and expose slider-based filters to spotlight highly connected genes.  
  Issue: [#108](https://github.com/akikuno/TSUMUGI-dev/issues/108)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/9c7b443bdd7960c3a6a1168ee3b8da392fb517b2)]  


## 🌟 New Features

+ Expanded the phenotype similarity and severity scales from 0–10 to 1–100 so users get Phenodigm-level precision when scoring networks.  
  Issue: [#119](https://github.com/akikuno/TSUMUGI-dev/issues/119)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/91309d636ecaf285aeaaeca9320408b23bb1a3db)]  

+ Added a JPEG export mode alongside the existing PNG and SVG download options for Cytoscape.js views.  
  Issue: [#117](https://github.com/akikuno/TSUMUGI-dev/issues/117)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/637183d5f35b0e89bb369c0069e5b375ecfa6e35)]  

+ Normalized degree and betweenness scores by phenotype count and introduced an optional log-scale transform to curb hub bias.  
  Issue: [#113](https://github.com/akikuno/TSUMUGI-dev/issues/113)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/00e9157c3a16a3d65c6bb2774c83848150d60a32)]  

+ Delivered Cytoscape Desktop–compatible GraphML exports (nodes and edges) for seamless round-tripping between the web app and local analyses.  
  Issue: [#92](https://github.com/akikuno/TSUMUGI-dev/issues/92)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/3c8bf960f4e648f3eda4d5f7d540abe823116c8b)]  


## 🐛 Bug Fixes

+ Recompute centrality metrics whenever filters change so node sizes and values stay in sync with the visible subnetwork.  
  Issue: [#112](https://github.com/akikuno/TSUMUGI-dev/issues/112)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/14a3124042e6aa2318bfc0792403424931efc23a)]  

+ Fix gene search bug for single character input  
  Issue: [#86](https://github.com/akikuno/TSUMUGI-dev/issues/86)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/04060df136c36b04c08a47cba5b510f58f0f6f6e)]  


## 🖼️ User Interface

+ Add Phenotype Severity and Similarity Scores to Network Tooltips  
  Issue: [#107](https://github.com/akikuno/TSUMUGI-dev/issues/107)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/pull/107)]  

+ Improve Network Visualization for Gene Symbol Pages  
  Issue: [#105](https://github.com/akikuno/TSUMUGI-dev/issues/105)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/pull/105)]  

+ Provide in-product tooltips and an info icon that explain phenotype metrics directly within the interface.  
  Issue: [#100](https://github.com/akikuno/TSUMUGI-dev/issues/100)  

+ Allow tooltips to be repositioned via touch interactions so tablet users can keep data in view.  
  Issue: [#97](https://github.com/akikuno/TSUMUGI-dev/issues/97)  

</details>


<details>
<summary> v0.3.2 (2025-06-23) </summary>

## 💥 Breaking Changes

+ **Updated to support IMPC Release 23.0**  
  Upgraded the underlying dataset to the latest IMPC Release 23.0 for improved data coverage and accuracy.  
  Issue: [#88](https://github.com/akikuno/TSUMUGI-dev/issues/88)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/e0dbbfce604394e66c2d71049560e42f41030947)]

## 🌟 New Features

+ **Human disease gene highlighting**  
  Added functionality to highlight genes associated with human diseases, enabling researchers to identify disease-relevant gene modules within phenotypic networks. The feature uses Phenodigm algorithm to establish mouse-human disease relationships.  
  Issue: [#87](https://github.com/akikuno/TSUMUGI-dev/issues/87)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/cb1033e0fde11a8cbfd98b3fa34731e2f929c0c0)]  
  Thanks to @kinari-labwork for contributing to this issue!

## 🖼️ User Interface

+ **Enhanced footer layout**  
  Redesigned the footer to better emphasize documentation and inquiry options, improving user access to help resources.  
  Issue: [#98](https://github.com/akikuno/TSUMUGI-dev/issues/98)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/aad5dde6e6db184401b16f14acbebf5fa22ffa94)]

+ **Unified mobile control panel**  
  Consolidated the previously split left/right control panels into a single, unified panel view on mobile devices for improved usability and screen space utilization.  
  Issue: [#89](https://github.com/akikuno/TSUMUGI-dev/issues/89)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/73da4c4774062f836ff187ad7e2b1494bbf203c6)]

+ **Dynamic header font sizing**  
  Implemented responsive header font sizing that automatically adjusts on mobile devices to ensure text displays properly within a single line, preventing layout issues.  
  Issue: [#93](https://github.com/akikuno/TSUMUGI-dev/issues/93)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/ab26c11232ffa56ed316a8658403b5a767756a8f)]

## 🐛 Bug Fixes

+ **Fixed mobile toggle button visibility**  
  Resolved an issue where the toggle close button was not appearing on mobile devices, restoring proper navigation functionality.  
  Issue: [#94](https://github.com/akikuno/TSUMUGI-dev/issues/94)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/73da4c4774062f836ff187ad7e2b1494bbf203c6)]

+ **Optimized network rendering performance**  
  Implemented a performance optimization by limiting the maximum number of displayed nodes to 150 (reduced from 200) to prevent rendering delays and ensure smooth user experience with large networks.  
  Issue: [#103](https://github.com/akikuno/TSUMUGI-dev/issues/103)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/515f23cd0c9d8687b07a0cc8a38e6bdb0f102a44)]

+ **Improved gene symbol page visualization**  
  Modified gene symbol pages to display only nodes that are directly connected to the target gene, reducing visual clutter and focusing on relevant gene relationships.  
  Issue: [#104](https://github.com/akikuno/TSUMUGI-dev/issues/104)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/bc710476f7c53d7a3e112b9d76afaba83d7dbede)]

## 🔧 Maintenance

+ **Enhanced raw data distribution**  
  Added version tags to `TSUMUGI_raw_data` filenames and expanded format support to include both CSV and Parquet formats, improving data accessibility and compatibility with different analysis tools.  
  Issues: [#95](https://github.com/akikuno/TSUMUGI-dev/issues/95), [#96](https://github.com/akikuno/TSUMUGI-dev/issues/96)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/22a5ad079c4f353c12b2316629981e3677cc8e94)]

+ **Streamlined deployment workflow**  
  Consolidated the separate testing and production deployment notebooks into a single, unified deployment file, simplifying the release process and reducing maintenance overhead.  
  Issue: [#101](https://github.com/akikuno/TSUMUGI-dev/issues/101)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/66076a91458a0482e32bc1eba420092fcba4cab7)]


</details>


<details>
<summary> v0.3.1 (2025-04-22) </summary>

## 🖼️ User Interface

- The user-specified phenotype is now always displayed, regardless of filter settings  
  Issue [#80](https://github.com/akikuno/TSUMUGI-dev/issues/80)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/4195f75481040696fed366ab3f69b1742c233477)]

- Added TSUMUGI version information and a contact form to the footer  
  Issue [#79](https://github.com/akikuno/TSUMUGI-dev/issues/79)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/4704544d9cbc2cf040f83c8f827c144501a76e73)]

## 🐛 Bug Fixes

- Ensured that all nodes and edges related to the target phenotype are properly displayed  
  Issue [#54](https://github.com/akikuno/TSUMUGI-dev/issues/54)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/1f08e851bf1e9009d754cc5f5727f23c9f0901cb)]

- To prevent nodes from disappearing when adjusting the slider, the row with the largest absolute effect size (between Homo and Hetero) is now selected  
  Issue [#72](https://github.com/akikuno/TSUMUGI-dev/issues/72)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/c5ed96555d5ed7aaf27778a35979b5938c2b4263)]

- `edgeMin` is now defined as the minimum edge size among edges connected to the target gene, similar to the `edgeMax` logic  
  Issue [#74](https://github.com/akikuno/TSUMUGI-dev/issues/74)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/3fe449af554a382f3f6b4e3fd76fd0714c61adc0)]

- Nodes that do not contain the user-specified phenotype are now excluded from display  
  Issue [#54](https://github.com/akikuno/TSUMUGI-dev/issues/54)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/1f08e851bf1e9009d754cc5f5727f23c9f0901cb)]

- Only edges between nodes that share two or more phenotypes are now visualized  
  Issue [#81](https://github.com/akikuno/TSUMUGI-dev/issues/81)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/d6dc99c4afa4cc2617b3bbb92d7685e2ff9a9f85)]

- Fixed an issue where duplicate phenotypes were shown in tooltips  
  Issue [#82](https://github.com/akikuno/TSUMUGI-dev/issues/82)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/f5ad91efbd5fdf774b6655e7bdfbf80bddbbedef)]

## 🔧 Maintenance

- Improved visibility in gene search by automatically centering and zooming in on the corresponding node  
  Issue [#78](https://github.com/akikuno/TSUMUGI-dev/issues/78)  
  [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/bbc6f00c6d6586a838003b7cfd2570a06ef2fd10)]

</details>

<details>
<summary> v0.3.0 (2025-04-19) </summary>

## 💥 Breaking

+ Annotate the four life stages: Embryo, Early, Interval, and Late. Issue [#20](https://github.com/akikuno/TSUMUGI-dev/issues/20).
  + [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/176847d10cee4d8b97d621df0c33f103a8ca185f)]
  + [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/af287d8ae1867d9863c015d143a6dcade586b970)]

+ Set thresholds for visualization considering similarity. Issue [#77](https://github.com/akikuno/TSUMUGI-dev/issues/77). [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/db661bb643df5772ad313ace24bb7063780920fc)].
  + Thanks to @aki2274 for reporting this issue!

+ Rename the header name `cluster` to `module` in the exported CSV. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/98ca5c486ae0825a6a027ca0497b3fe3ea170d73)].

## 📝 Documentation

+ Add documentation on how to load the last column (`List of shared phenotypes`) in `TSUMUGI_raw_data.csv.gz` as `list[str]`. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/bda251fa4630e220172f2046cb7702ef684c03bc)].

+ Add documentation of life stage. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/c0f4ae662fcca66d07a41c8d9a6d486432a7a78c)].


## 🖼️ User Interface

+ Organize the control panel. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/a755abe926ba72fc76895633a87a41dc62cc53e7)]

</details>

<details>
<summary> v0.2.2 (2025-04-11) </summary>

## 🖼️ User Interface

- Add support for smartphone operation.  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/4b5ad78846fbbcca05d7626c900c7afa42360eab)

- Redesign the control panel for improved usability.  
  Issue: [#65](https://github.com/akikuno/TSUMUGI-dev/issues/65)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/ae7a9c1f80e2591a44a108605858258aebd5aea8)

## 📝 Documentation

- Publish a complete list of currently available phenotypes and genes.  
  Issue: [#34](https://github.com/akikuno/TSUMUGI-dev/issues/34)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/faa2b42eee54446d72c3c47acf9cdf6b04b5685c)

## 🔧 Maintenance

- Use `inherit` for tab button text color to ensure consistent appearance and prevent default blue styling on macOS.  
  Issue: [#67](https://github.com/akikuno/TSUMUGI-dev/issues/67)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/354b82cbb3200d164d5ff74878c5be74b8face07)

- Unify HTML templates for better maintainability.  
  Issue: [#68](https://github.com/akikuno/TSUMUGI-dev/issues/68)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/pull/70)

- Unify JavaScript templates to reduce redundancy.  
  Issue: [#69](https://github.com/akikuno/TSUMUGI-dev/issues/69)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/pull/73)

## 🐛 Bug Fixes

- Adjust the severity slider behavior to always keep at least one gene pair visible, even at minimum or maximum values.  
  Issue: [#72](https://github.com/akikuno/TSUMUGI-dev/issues/72)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/ce38b815c65db3a7e4c80191160fdd0aaa980944)

- Change the link button font color from blue to black (#333) on macOS for consistent styling.  
  Issue: [#67](https://github.com/akikuno/TSUMUGI-dev/issues/67)  
  [Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/5242c14be4bb41ec3f6b67a0357759922ae5add0)

</details>



<details>
<summary> v0.2.1 (2025-03-27) </summary>


## 📝 Documentation

+ Add documentation (README.md and README_JP.md). Issue [#60](https://github.com/akikuno/TSUMUGI-dev/issues/60) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/pull/66)]

## 🌟 New Features

+ Add a Google Form to allow anyone to submit inquiries. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/2db865949eb63716e8243ae0f998da6f45110731)]

+ Add a search box for a gene symbol in the network Issue. [#30](https://github.com/akikuno/TSUMUGI-dev/issues/30) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/afa6a262cbae45bca77426698fa1ea04ffa9214e)]
## 🐛 Bug Fixes

+ Modified to ensure that the Submit button is definitely disabled when the input is empty. Issue: [#61](https://github.com/akikuno/TSUMUGI-dev/issues/61) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/06641db2d7d1acacc97237a1515403394ef17283)]

+ Phenotypes for which no phenotype-similar gene groups were detected have been removed from `available_mp_terms.json` to prevent them from being selected. Issue: [#58](https://github.com/akikuno/TSUMUGI-dev/issues/58) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/31712b028108f1b1daf696f873f95c447deb118e)]

+ Fixed a bug where target genes disappeared when increasing the slider threshold in "Gene". Issue: [#63](https://github.com/akikuno/TSUMUGI-dev/issues/63) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/8fa8f8539351e598abf6d888293a4cd1b15b1ba0)]


## 🖼️ User Interface

+ Improve the visibility of the top page tab. Issue: [#59](https://github.com/akikuno/TSUMUGI-dev/issues/59) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/9d9ea23cadbe1883983e78efe3702ff7a69efe33)]

</details>


<details>
<summary> v0.2.0 (2025-03-21) </summary>

- Allow users to input their intended gene lists. Issue #42 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/a6850985c98941e7fbb3b992226eb7c755c6e7b2)]

## 🐛 Bug Fixes

+ Fix a bug where gene links led to [Page Not Found](https://www.mousephenotype.org/data/genes). Issue: #53 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/fdacb58db89cf99c84a597cc85e0919152c4d2fa)]

## 🔧 Maintenance

+ Use the latest IMPC [Release-22.1 (2024-12-11)](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-22.1/)

</details>

<details>
<summary> v0.1.5 (2025-03-18) </summary>

## 🔧 Maintenance

- The previously separated `phenotypeForm` and `geneForm` have been unified. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/a07aa8a47540f6e6bd54ca2bbaa6f3cb315b0e79)]

- For code reusability, the function has been moved to an external module.
  - Add `data_loader.js`. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/2898ab252606f78a01266fd324df3ca8fe045c90)]

## 🖼️ User Interface

- `searchForm` has been repositioned at the top and made scrollable when necessary to prevent it from being cut off on smaller screens. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/ab9ec38553be0dcd17c7dc9ae8c301ed1e5f48ab)]

- Make the favicon display correctly in Firefox. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/4b336a91b4d7c81403770a69d2a40ec0bb21407a)]

</details>
<!-- ============================================================= -->


<details>
<summary> v0.1.4 (2025-03-03) </summary>

## 🐛 Bug Fixes

- Fix to show sliders for phenotype severity. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/311a708d9da6fe8947bda1e4ca1fba29dc0df428)]

## 🔧 Maintenance

- Ensure that the line endings of the raw data are LF. Issue: #50 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/e70752a95c26f79b34699850163eb8ff9920bb7e)]

- For code reusability, the function has been moved to an external module.
  - Add `tooltips.js`, `value_scaler.js`, and `exporter.js`. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/250adf33792eac77d1a08c0ab5f84da3cf827571)]
  - Add `components.js`. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/20c1910630cf13b42555d32c2b5349f156809725)]
  - Add `filteres.js`.

</details>


<details>
<summary> v0.1.3 (2025-02-27) </summary>

## 💥 Breaking

- Change URL from [LARC server](https://www.md.tsukuba.ac.jp/LabAnimalResCNT/TSUMUGI/) to [Github Pages](https://larc-tsukuba.github.io/tsumugi/). Issue: [#49](https://github.com/akikuno/TSUMUGI-dev/issues/49) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/c434cf09b778f4cc33bdb31bed6da9a52461a53f)]

## 🌟 New Features

- Add checkbox of genotype and sex specificity. Issue: [#22](https://github.com/akikuno/TSUMUGI-dev/issues/22) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/d165390dfc2022bf4b55a49051f939c884a4c2c0)]

- Add `Download raw data` button for re-use of the TSUMUGI data. Issue: [#47](https://github.com/akikuno/TSUMUGI-dev/issues/47) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/d4f89f191a3e7edca4123307044149a54b2d0434)]

## 🖼️ User Interface

- Modify the slider text and numbers to be displayed in a single column. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/f08ddd42691819dd28b821f4b9dc836c5184c066)]

- Hide the Phenotype severity slider if the phenotype is binary (all effect sizes are 1). Issue [#46](https://github.com/akikuno/TSUMUGI-dev/issues/46) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/5d5d6a9ba7462fcb31ed746e01de503917577089)]

## 🔧 Maintenanc

- Add a function to manage the completion of data retrieval. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/ac15868ee42703256c5721954f4cc3bb7dcb7d07)]

- Download Raw data from CloudFlare R2 repository. Issue: [#47](https://github.com/akikuno/TSUMUGI-dev/issues/47) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/d5b38d2069b559888b37acd5dbd5660972dd7230)]

- Use a directory structure that separates Data and Frontend. Issue: [#48](https://github.com/akikuno/TSUMUGI-dev/issues/48) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/1f7a2e5a70e6a4b7177a7b591adac8e4de5c16bd)]


</details>


<details>
<summary> v0.1.2 (2025-01-27) </summary>

## 🌟 New Features

+ Specify Homo, Hetero, or Hemi for each phenotype. Issue: #38 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/b8cc572bc94da4796e53f8783fb4d1e862de3bf3)]

+ Indicate whether each phenotype is male- or female-specific. Issue: #22 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/42187872c7b1feae2bc6b4b0495a316cb9fbae00)]

## 🖼️ User Interface

+ Setting up OGP Issue: #40 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/2bf3c993642963ca39f3e8dd4a2d25ea1c7b3f32)]

## 🐛 Bug Fixes

+ The number of nodes was set to 200 (arbitrary) because too many nodes would make rendering impossible. Issue: #45 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/0212b6077fda7940f24b9e771a99f5b075c2fb21)]. Many thanks to Dr. Hayate Suzuki (University of Tsukuba) for reporting this issue!


 ## 🔧 Maintenance

+ Compress JSON files with Gzip to reduce server usage. Issue: #24 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/e1efc726b9beb5b4dc5dd2d6b785f1e9bf24c1ce)]

</details>


<details>
<summary>v0.1.1 (2024-12-04)</summary>

## 💥 Breaking

+ Use updated release of IMPC v22.0. Issue: #33 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/1bbb56f05bcc47fef21b0e3004f3fb283f425373)]

## 🖼️ User Interface

+ Change the placeholder of TSUMUGI. Issue: #32 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/5a1bc947321d5ccb781598fa2ec14731709536e8)]

+ Change "Similarity of accessory phenotypes" and "Severity of target phenotype" to "Phenotypes similarity" and "Phenotype severity". Issue: #35 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/48ffcb470c2ab6d77b9b5074ef3cbbb2a1726abd)]

## 🔧 Maintenance

+ Decompose Cytoscape's Tooltip handler into functions for each element. [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/6482e5ba1cdc7861cb4b24663ea538588df651a7)]

+ Change the directory name from `web` to `TSUMUGI` Issue: #31 [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/64266cbf323ae78ff969fd5d4484691cfa8e0c63)]

</details>

<details>
<summary> v0.1.0 (2024-11-16) </summary>
+ Genes of interest can now be selected. Issue: #11
</details>

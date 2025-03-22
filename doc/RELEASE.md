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
+ commitMessage. Issue: #XX [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/xxxxx)]
-->

<!-- ## TODO -->

<!--
- ドキュメントの整備 #60
- いま利用できる表現型および遺伝子の全リストを公開する #34
- Edgeの太さがすべて同じに見える #27
- 類似度のフィルターをなだらかに段階的にしたい #29
-->

<!-- ############################################################# # -->

# v0.2.1 (2025-04-DD) in Development

<!-- + Add documentation (README.md and README_JP.md). Issue [#60](https://github.com/akikuno/TSUMUGI-dev/issues/60) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/xxxxx)] -->

## 🐛 Bug Fixes

+ Fix a bug: The Submit button could be pressed even when the input was empty Issue: [#61](https://github.com/akikuno/TSUMUGI-dev/issues/61) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/06641db2d7d1acacc97237a1515403394ef17283)]

## 🖼️ User Interface

+ Improve the visibility of the top page tab. Issue: [#59](https://github.com/akikuno/TSUMUGI-dev/issues/59) [[Commit Detail](https://github.com/akikuno/TSUMUGI-dev/commit/9d9ea23cadbe1883983e78efe3702ff7a69efe33)]

<!-- ############################################################# # -->



-------------------------------------------------------------

# Past Releases

<!-- ============================================================= -->
<!-- <details>
<summary> v0.X.X (2025-MM-DD) </summary>

</details> -->
<!-- ============================================================= -->


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

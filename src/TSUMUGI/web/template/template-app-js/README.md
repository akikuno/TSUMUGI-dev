## filterByNodeColorAndEdgeSize_phenotype.js

- For binary phenotypes, remove `nodeSliderValues = nodeSlider.noUiSlider.get().map(parseFloat); // REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE`


## template_app.js

- XXX_NODE_COLOR_SLIDER
  - Insert `node_color_slider.js` when mode="non-binary-phenotype"
  - Remove it otherwise

- XXX_NODE_MIN_MAX
  - Insert `nodeMinMax.js` when mode="non-binary-phenotype"
  - Remove it otherwise

- XXX_EDGE_MIN_MAX
  - For gene-symbol mode, insert `edgeMinMax_for_genesymbol.js`
  - Otherwise replace with:
    `const edgeMin = Math.min(...edgeSizes); const edgeMax = Math.max(...edgeSizes);`

- XXX_FILTER_ELEMENTS
    - For phenotypes, insert `filterByNodeColorAndEdgeSize_phenotype.js`
    - For gene symbols, insert `filterByNodeColorAndEdgeSize_genesymbol.js`
    - For gene lists, insert `filterByNodeColorAndEdgeSize_genelist.js`

- XXX_ELEMENTS
    - For phenotypes, replace with `loadJSONGz("../../data/phenotype/XXX_NAME.json.gz")`
    - For gene symbols, replace with `loadJSONGz("../../data/genesymbol/XXX_NAME.json.gz")`
    - For gene lists, replace with `JSON.parse(localStorage.getItem("elements"))`

- XXX_TARGET_PHENOTYPE
  - Replace with mp_term_name_space for phenotypes
  - Use an empty string otherwise

- XXX_NAME
  - Phenotype: replace with mp_term_name_underscore
  - Gene: replace with genesymbol
  - Gene list: replace with "geneList"

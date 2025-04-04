## filterByNodeColorAndEdgeSize_phenotype.js

- バイナリ表現型のとき、`nodeSliderValues = nodeSlider.noUiSlider.get().map(parseFloat); // REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE`を削除


## template_app.html

- XXX_NODE_COLOR_SLIDER
  - mode="non-binary-phenotype"のとき、`node_color_slider.js`を挿入
  - それ以外は削除

- XXX_FILTER_ELEMENTS
    - 表現型のとき、`filterByNodeColorAndEdgeSize_phenotype.js`を挿入
    - 遺伝子シンボルのとき、`filterByNodeColorAndEdgeSize_genesymbol.js`を挿入
    - 遺伝子リストのとき、`filterByNodeColorAndEdgeSize_genelist.js`を挿入

- XXX_ELEMENTS
    - GeneListのときには`JSON.parse(localStorage.getItem("elements"))`で置換
    - それ以外は、`loadJSONGz("../../data/phenotype/XXX_NAME.json.gz")`で置換


- XXX_TARGET_PHENOTYPE
  - 表現型のとき、mp_term_name_spaceで置換
  - それ以外は""(空文字)

- XXX_NAME
  - 表現型：mp_term_name_underscoreで置換
  - 遺伝子名：genesymbolで置換
  - 遺伝子リスト: "geneList"で置換



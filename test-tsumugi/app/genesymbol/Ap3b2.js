import { exportGraphAsPNG, exportGraphAsCSV } from "../js/exporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showTooltip } from "../js/tooltips.js";
import { createSlider } from "../js/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/filters.js";
import { loadJSONGz, loadJSON } from "../js/data_loader.js";
import { setupGeneSearch } from "../js/searcher.js";

// ############################################################################
// Input handling
// ############################################################################


const url_elements = "../../data/genesymbol/Ap3b2.json.gz";
const url_map_symbol_to_id = "../../data/marker_symbol_accession_id.json";

const elements = loadJSONGz(url_elements);
const map_symbol_to_id = loadJSON(url_map_symbol_to_id);

// ############################################################################
// Cytoscape handling
// ############################################################################

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

const nodeMin = 0;
const nodeMax = 1;
const edgeMin = Math.min(...edgeSizes);

// ############################################################################
// edgeMaxの計算：
// node_color === 1 のノードに接続されたエッジの中で最大のedge_sizeを取得
// その値をedgeMaxとする
// その後、elementsのedge_sizeをedgeMaxを上限として調整
// ############################################################################

// node_color === 1 のノード(targetGene)を1つだけ取得
const targetGene = elements.find((ele) => ele.data.node_color === 1);

// targetGeneの ID (遺伝子シンボル)を取得
const targetGeneId = targetGene?.data?.id;

// targetGeneに接続されているエッジだけ抽出
const connectedEdges = elements.filter((ele) => ele.data.source === targetGeneId || ele.data.target === targetGeneId);

// そのエッジたちの edge_size を集めて最大値を取得
const edgeSizesTargetGene = connectedEdges
    .filter((edge) => edge.data.edge_size !== undefined)
    .map((edge) => edge.data.edge_size);

const edgeMax = Math.max(...edgeSizesTargetGene);

// elementsに含まれる全edge_sizeの最大値を、edgeMaxを上限とする
connectedEdges.forEach((edge) => {
    if (edge.data.edge_size > edgeMax) {
        edge.data.edge_size = edgeMax;
    }
});

// ############################################################################
// Cytoscapeの初期化
// ############################################################################

let currentLayout = "cose";

const nodeRepulsionMin = 1;
const nodeRepulsionMax = 10000;
const componentSpacingMin = 1;
const componentSpacingMax = 200;

let nodeRepulsionValue = scaleToOriginalRange(
    parseFloat(document.getElementById("nodeRepulsion-slider").value),
    nodeRepulsionMin,
    nodeRepulsionMax,
);
let componentSpacingValue = scaleToOriginalRange(
    parseFloat(document.getElementById("nodeRepulsion-slider").value),
    componentSpacingMin,
    componentSpacingMax,
);

function getLayoutOptions() {
    return {
        name: currentLayout,
        nodeRepulsion: nodeRepulsionValue,
        componentSpacing: componentSpacingValue,
    };
}

const cy = cytoscape({
    container: document.querySelector(".cy"),
    elements: elements,
    style: [
        {
            selector: "node",
            style: {
                label: "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": "20px",
                width: 15,
                height: 15,
                "background-color": function (ele) {
                    const color_value = scaleValue(ele.data("node_color"), nodeMin, nodeMax, 1, 10);
                    return getColorForValue(color_value);
                },
            },
        },
        {
            selector: "edge",
            style: {
                "curve-style": "bezier",
                "text-rotation": "autorotate",
                width: function (ele) {
                    return scaleValue(ele.data("edge_size"), edgeMin, edgeMax, 0.5, 2);
                },
            },
        },
    ],
    layout: getLayoutOptions(),
});

// ############################################################################
// Visualization handling
// ############################################################################

// --------------------------------------------------------
// Network layout dropdown
// --------------------------------------------------------

document.getElementById("layout-dropdown").addEventListener("change", function () {
    currentLayout = this.value;
    cy.layout({ name: currentLayout }).run();
});

// =============================================================================
// スライダーによる初期化とフィルター関数
// =============================================================================

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

function filterElements() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. edge_size条件を満たすエッジを取得
    const visibleEdges = cy.edges().filter((edge) => {
        const edgeSize = edge.data("edge_size");
        return edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue;
    });

    // 2. 条件を満たしたエッジ＋そのエッジに接続しているノードたちを取得
    const candidateElements = visibleEdges.union(visibleEdges.connectedNodes());

    // 3. 連結成分を取得
    const components = candidateElements.components();

    // 4. 一旦すべて非表示にしてから…
    cy.elements().forEach((ele) => ele.style("display", "none"));

    // 5. node_color === 1 を含むクラスタだけ表示
    components.forEach((comp) => {
        const hasColor1 = comp.nodes().some((node) => node.data("node_color") === 1);
        if (hasColor1) {
            comp.nodes().forEach((node) => node.style("display", "element"));
            comp.edges().forEach((edge) => edge.style("display", "element"));
        }
    });

    // 6. レイアウト再適用
    cy.layout(getLayoutOptions()).run();
}

// --------------------------------------------------------
// Initialization of the Slider for Phenotypes similarity
// --------------------------------------------------------
const edgeSlider = document.getElementById("filter-edge-slider");
noUiSlider.create(edgeSlider, { start: [1, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

// --------------------------------------------------------
// Update the slider values when the sliders are moved
// --------------------------------------------------------

edgeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("edge-size-value").textContent = intValues.join(" - ");
    filterElements();
});

// ############################################################################
// 遺伝型・正特異的フィルタリング関数
// ############################################################################

let target_phenotype = "";

// フィルタリング関数のラッパー
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, target_phenotype, cy, filterElements);
}

// フォーム変更時にフィルタリング関数を実行
document.getElementById("genotype-filter-form").addEventListener("change", applyFiltering);
document.getElementById("sex-filter-form").addEventListener("change", applyFiltering);

// ############################################################################
// Cytoscape's visualization setting
// ############################################################################

// --------------------------------------------------------
// 遺伝子名検索
// --------------------------------------------------------

setupGeneSearch({ cy });

// --------------------------------------------------------
// Slider for Font size
// --------------------------------------------------------

createSlider("font-size-slider", 20, 1, 50, 1, (intValues) => {
    document.getElementById("font-size-value").textContent = intValues;
    cy.style()
        .selector("node")
        .style("font-size", intValues + "px")
        .update();
});

// --------------------------------------------------------
// Slider for Edge width
// --------------------------------------------------------

createSlider("edge-width-slider", 5, 1, 10, 1, (intValues) => {
    document.getElementById("edge-width-value").textContent = intValues;
    cy.style()
        .selector("edge")
        .style("width", function (ele) {
            return scaleValue(ele.data("edge_size"), edgeMin, edgeMax, 0.5, 2) * intValues;
        })
        .update();
});

// --------------------------------------------------------
// Slider for Node repulsion
// --------------------------------------------------------

createSlider("nodeRepulsion-slider", 5, 1, 10, 1, (intValues) => {
    nodeRepulsionValue = scaleToOriginalRange(intValues, nodeRepulsionMin, nodeRepulsionMax);
    componentSpacingValue = scaleToOriginalRange(intValues, componentSpacingMin, componentSpacingMax);
    document.getElementById("node-repulsion-value").textContent = intValues;
    cy.layout(getLayoutOptions()).run();
});

// ############################################################################
// Tooltip handling
// ############################################################################

// Show tooltip on tap
cy.on("tap", "node, edge", function (event) {
    showTooltip(event, cy, map_symbol_to_id);
});

// Hide tooltip when tapping on background
cy.on("tap", function (event) {
    if (event.target === cy) {
        removeTooltips();
    }
});

// ############################################################################
// Exporter
// ############################################################################

const file_name = "TSUMUGI_Ap3b2";

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

document.getElementById("export-png").addEventListener("click", function () {
    exportGraphAsPNG(cy, file_name);
});

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

document.getElementById("export-csv").addEventListener("click", function () {
    exportGraphAsCSV(cy, file_name);
});

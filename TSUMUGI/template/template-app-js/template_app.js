import { exportGraphAsPNG, exportGraphAsCSV } from "../js/exporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showTooltip } from "../js/tooltips.js";
import { calculateConnectedComponents } from "../js/components.js";
import { createSlider } from "../js/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/filters.js";
import { loadJSONGz, loadJSON } from "../js/data_loader.js";
import { setupGeneSearch } from "../js/searcher.js";

// ############################################################################
// Input handler
// ############################################################################

// REMOVE_FROM_THIS_LINE

// const elements = [
//     { data: { id: 'Nanog', label: 'Nanog', annotation: ['hoge', 'hooo'], node_color: 50, } },
//     { data: { id: 'Pou5f1', label: 'Pou5f1', annotation: 'fuga', node_color: 100, } },
//     { data: { id: 'Sox2', label: 'Sox2', annotation: 'foo', node_color: 3, } },
//     { data: { source: 'Nanog', target: 'Pou5f1', annotation: ['Foo', 'FooBar'], edge_size: 5 } },
//     { data: { source: 'Nanog', target: 'Sox2', annotation: 'FooBar', edge_size: 1 } },
//     { data: { source: 'Sox2', target: 'Pou5f1', annotation: 'FooBar', edge_size: 10 } },
// ];

// const map_symbol_to_id = { 'Nanog': 'MGI:97281', 'Pou5f1': 'MGI:1352748', 'Sox2': 'MGI:96217' };

// REMOVE_TO_THIS_LINE

const elements = XXX_ELEMENTS;
const map_symbol_to_id = loadJSON("../../data/marker_symbol_accession_id.json");

// ############################################################################
// Cytoscape Elements handler
// ############################################################################

let nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
let nodeMin = Math.min(...nodeSizes);
let nodeMax = Math.max(...nodeSizes);

XXX_NODE_MIN_MAX

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);
const edgeMin = Math.min(...edgeSizes);
XXX_EDGE_MAX

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
// Control panel handler
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
// Edge size slider for Phenotypes similarity
// --------------------------------------------------------

// Initialization of the Edge size slider
const edgeSlider = document.getElementById("filter-edge-slider");
noUiSlider.create(edgeSlider, { start: [1, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

XXX_NODE_COLOR_INITIALIZATION

// Update the slider values when the sliders are moved
edgeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("edge-size-value").textContent = intValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});

XXX_NODE_COLOR_UPDATE

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE

// =============================================================================
// 遺伝型・正特異的フィルタリング関数
// =============================================================================

let target_phenotype = "XXX_TARGET_PHENOTYPE";

// フィルタリング関数のラッパー
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, target_phenotype, cy, filterByNodeColorAndEdgeSize);
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

const file_name = "TSUMUGI_XXX_NAME";

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

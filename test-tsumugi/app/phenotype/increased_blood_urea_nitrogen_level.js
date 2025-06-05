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
//     { data: { id: 'Nanog', label: 'Nanog', phenotype: ['hoge', 'hooo'], node_color: 50, } },
//     { data: { id: 'Pou5f1', label: 'Pou5f1', phenotype: 'fuga', node_color: 100, } },
//     { data: { id: 'Sox2', label: 'Sox2', phenotype: 'foo', node_color: 3, } },
//     { data: { source: 'Nanog', target: 'Pou5f1', phenotype: ['Foo', 'FooBar'], edge_size: 5 } },
//     { data: { source: 'Nanog', target: 'Sox2', phenotype: 'FooBar', edge_size: 1 } },
//     { data: { source: 'Sox2', target: 'Pou5f1', phenotype: 'FooBar', edge_size: 10 } },
// ];

// const map_symbol_to_id = { 'Nanog': 'MGI:97281', 'Pou5f1': 'MGI:1352748', 'Sox2': 'MGI:96217' };

// REMOVE_TO_THIS_LINE

const elements = loadJSONGz("../../data/phenotype/increased_blood_urea_nitrogen_level.json.gz");
const map_symbol_to_id = loadJSON("../../data/marker_symbol_accession_id.json");

// ############################################################################
// Cytoscape Elements handler
// ############################################################################

let nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
let nodeMin = Math.min(...nodeSizes);
let nodeMax = Math.max(...nodeSizes);

// ==========================================================
// スライダーを上限値・下限値に合わせても、最低１つの遺伝子ペアが可視化できるようにする. Issue #72
// ==========================================================

// Step 1: node_color を ID にマップし、ランクをつける
const nodeColorMap = new Map();
elements.forEach((ele) => {
    if (ele.data.node_color !== undefined && ele.data.id !== undefined) {
        nodeColorMap.set(ele.data.id, ele.data.node_color);
    }
});

// ランク付け
const sortedNodeColors = [...new Set([...nodeColorMap.values()])].sort((a, b) => a - b);
const nodeColorToRank = new Map();
sortedNodeColors.forEach((val, idx) => {
    nodeColorToRank.set(val, idx + 1); // ランクは1スタート
});

// Step 2: エッジごとに source/target のランク合計と、元の値を保存
const edgeRankPairs = [];

elements.forEach((ele) => {
    if (ele.data.source && ele.data.target) {
        const sourceVal = nodeColorMap.get(ele.data.source);
        const targetVal = nodeColorMap.get(ele.data.target);

        if (sourceVal !== undefined && targetVal !== undefined) {
            const sourceRank = nodeColorToRank.get(sourceVal);
            const targetRank = nodeColorToRank.get(targetVal);
            const rankSum = sourceRank + targetRank;

            edgeRankPairs.push({
                rankSum: rankSum,
                minVal: Math.min(sourceVal, targetVal),
                maxVal: Math.max(sourceVal, targetVal),
            });
        }
    }
});

// Step 3: 最小スコアのペアの max → nodeMin、最大スコアのペアの min → nodeMax
const minRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum < b.rankSum ? a : b));
const maxRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum > b.rankSum ? a : b));

nodeMin = minRankEdge.maxVal;
nodeMax = maxRankEdge.minVal;

// Step 4: node_color を min/max にクリップ
elements.forEach((ele) => {
    if (ele.data.node_color !== undefined) {
        if (ele.data.node_color <= nodeMin) {
            ele.data.node_color = nodeMin;
        } else if (ele.data.node_color >= nodeMax) {
            ele.data.node_color = nodeMax;
        }
    }
});

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);

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

// Initialization of the Node color slider
const nodeSlider = document.getElementById("filter-node-slider");
noUiSlider.create(nodeSlider, { start: [1, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

// Update the slider values when the sliders are moved
edgeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("edge-size-value").textContent = intValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});

// Update the slider values when the sliders are moved
nodeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("node-color-value").textContent = intValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

function filterByNodeColorAndEdgeSize() {
    let nodeSliderValues = [1, 10];
    nodeSliderValues = nodeSlider.noUiSlider.get().map(parseFloat); // REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE

    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

    const nodeMinValue = scaleToOriginalRange(nodeSliderValues[0], nodeMin, nodeMax);
    const nodeMaxValue = scaleToOriginalRange(nodeSliderValues[1], nodeMin, nodeMax);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. node_color 範囲に基づきノードを表示/非表示
    cy.nodes().forEach((node) => {
        const nodeColor = node.data("node_color");
        const isVisible = nodeColor >= nodeMinValue && nodeColor <= nodeMaxValue;
        node.style("display", isVisible ? "element" : "none");
    });

    // 2. edge_size + 表現型数の条件でエッジを表示/非表示
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sharedPhenotypes = edge.data("phenotype") || [];
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";

        const isVisible =
            sourceVisible &&
            targetVisible &&
            edgeSize >= edgeMinValue &&
            edgeSize <= edgeMaxValue &&
            sharedPhenotypes.length >= 2; // 2つ以上の表現型を持つエッジのみ表示

        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. 孤立ノードを非表示
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 4. レイアウト再適用
    cy.layout(getLayoutOptions()).run();
}

// =============================================================================
// 遺伝型・性差・ライフステージ特異的フィルタリング関数
// =============================================================================

let target_phenotype = "increased blood urea nitrogen level";

// フィルタリング関数のラッパー
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterByNodeColorAndEdgeSize);
}

// フォーム変更時にフィルタリング関数を実行
document.getElementById("genotype-filter-form").addEventListener("change", applyFiltering);
document.getElementById("sex-filter-form").addEventListener("change", applyFiltering);
document.getElementById("lifestage-filter-form").addEventListener("change", applyFiltering);
document.getElementById("human-disease-filter-form").addEventListener("change", applyFiltering);

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

const layoutDropdown = document.getElementById("layout-dropdown");
const nodeRepulsionContainer = document.getElementById("node-repulsion-container");

function updateNodeRepulsionVisibility() {
    const selectedLayout = layoutDropdown.value;
    nodeRepulsionContainer.style.display = selectedLayout === "cose" ? "block" : "none";
}

updateNodeRepulsionVisibility();
layoutDropdown.addEventListener("change", updateNodeRepulsionVisibility);

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
    showTooltip(event, cy, map_symbol_to_id, target_phenotype);
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

const file_name = "TSUMUGI_increased_blood_urea_nitrogen_level";

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

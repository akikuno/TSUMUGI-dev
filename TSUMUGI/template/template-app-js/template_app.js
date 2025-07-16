import { exportGraphAsPNG, exportGraphAsCSV, exportGraphAsGraphML } from "../js/exporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showTooltip } from "../js/tooltips.js";
import { calculateConnectedComponents } from "../js/components.js";
import { createSlider } from "../js/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/filters.js";
import { loadJSONGz, loadJSON } from "../js/data_loader.js";
import { setupGeneSearch } from "../js/gene_searcher.js";
import { highlightDiseaseAnnotation } from "../js/highlighter.js";
import { setupPhenotypeSearch } from "../js/phenotype_searcher.js";
import { initializeCentralitySystem, recalculateCentrality } from "../js/centrality.js";

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

const elements = XXX_ELEMENTS;
const map_symbol_to_id = loadJSON("../../data/marker_symbol_accession_id.json");

// ############################################################################
// Cytoscape Elements handler
// ############################################################################

let nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
let nodeColorMin = Math.min(...nodeSizes);  // 色表示用の元の範囲
let nodeColorMax = Math.max(...nodeSizes);  // 色表示用の元の範囲

// フィルタリング用の範囲（元の値をコピー）
let nodeMin = nodeColorMin;
let nodeMax = nodeColorMax;

XXX_NODE_MIN_MAX

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

XXX_EDGE_MIN_MAX

// ############################################################################
// Cytoscapeの初期化
// ############################################################################

let currentLayout = "cose";

const nodeRepulsionMin = 1;
const nodeRepulsionMax = 10000;
const componentSpacingMin = 1;
const componentSpacingMax = 200;

// Use different defaults for gene symbol pages only
const isGeneSymbolPage = "XXX_ELEMENTS".includes("genesymbol");
const defaultNodeRepulsion = isGeneSymbolPage ? 8 : 5;

let nodeRepulsionValue = scaleToOriginalRange(
    defaultNodeRepulsion,
    nodeRepulsionMin,
    nodeRepulsionMax,
);

let componentSpacingValue = scaleToOriginalRange(
    defaultNodeRepulsion,
    componentSpacingMin,
    componentSpacingMax,
);

function getLayoutOptions() {
    const baseOptions = {
        name: currentLayout,
        nodeRepulsion: nodeRepulsionValue,
        componentSpacing: componentSpacingValue,
    };

    // Add enhanced options for COSE layout to prevent hairball effect (gene symbol pages only)
    if (currentLayout === "cose" && isGeneSymbolPage) {
        return {
            ...baseOptions,
            idealEdgeLength: 100,           // Increase ideal edge length for better spacing
            nodeOverlap: 20,                // Increase to prevent node overlap
            padding: 30,                    // Add padding around the layout
            animate: true,                  // Enable animation for better visual feedback
            animationDuration: 500,         // Animation duration in ms
            gravity: -1.2,                  // Negative gravity to push nodes apart
            numIter: 1500,                  // More iterations for better layout
            initialTemp: 200,               // Higher initial temperature for better spreading
            coolingFactor: 0.95,            // Slower cooling for better results
            minTemp: 1.0,                   // Minimum temperature threshold
            edgeElasticity: 100,            // Edge elasticity for better edge distribution
        };
    }

    return baseOptions;
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
                "font-size": isGeneSymbolPage ? "10px" : "20px",
                width: 15,
                height: 15,
                "background-color": function (ele) {
                    const originalColor = ele.data("original_node_color") || ele.data("node_color");
                    const color_value = scaleValue(originalColor, nodeColorMin, nodeColorMax, 1, 10);
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
        {
            selector: ".disease-highlight", // 疾患ハイライト用クラス
            style: {
                "border-width": 5,
                "border-color": "#fc4c00",
            },
        },
        {
            selector: ".gene-highlight", // 遺伝子検索ハイライト用クラス
            style: {
                "color": "#006400",
                "font-weight": "bold",
            },
        },
        {
            selector: ".phenotype-highlight", // 表現型ハイライト用クラス
            style: {
                "border-width": 5,
                "border-color": "#3FA7D6",
            },
        },
    ],
    layout: getLayoutOptions(),
});


// ★ デバッグ用：cyをグローバルに公開
window.cy = cy;

// ★ モバイル対応：Cytoscapeの表示問題を修正
function handleMobileResize() {
    if (cy) {
        // モバイルでのレイアウト変更後にCytoscapeを再描画
        setTimeout(() => {
            cy.resize();
            cy.fit();
            cy.center();
        }, 300);
    }
}

// モバイルでの初期化完了後にCytoscapeを調整
setTimeout(() => {
    if (window.innerWidth <= 600) {
        cy.resize();
        cy.fit();
        cy.center();
    }
}, 500);

// ウィンドウリサイズ時の対応
window.addEventListener('resize', handleMobileResize);

// オリエンテーション変更時の対応（モバイル）
window.addEventListener('orientationchange', () => {
    setTimeout(handleMobileResize, 500);
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
// Set default to 5 for gene symbol pages, 1 for others
const defaultPhenotypeSimMin = isGeneSymbolPage ? 5 : 1;
noUiSlider.create(edgeSlider, { start: [defaultPhenotypeSimMin, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

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
// 遺伝型・性差・ライフステージ特異的フィルタリング関数
// =============================================================================

let target_phenotype = "XXX_PHENOTYPE";

// フィルタリング関数のラッパー
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterByNodeColorAndEdgeSize);
    // フィルタリング後にCentrality値を再計算
    if (typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
}

// フォーム変更時にフィルタリング関数を実行
document.getElementById("genotype-filter-form").addEventListener("change", applyFiltering);
document.getElementById("sex-filter-form").addEventListener("change", applyFiltering);
document.getElementById("lifestage-filter-form").addEventListener("change", applyFiltering);

// =============================================================================	
// ヒト疾患ハイライト	
// =============================================================================	
highlightDiseaseAnnotation({ cy });

// ############################################################################
// Cytoscape's visualization setting
// ############################################################################

// --------------------------------------------------------
// 遺伝子名検索
// --------------------------------------------------------

setupGeneSearch({ cy });

// =============================================================================
// 表現型ハイライト（検索機能付き）
// =============================================================================
setupPhenotypeSearch({ cy, elements });

// --------------------------------------------------------
// Slider for Font size
// --------------------------------------------------------

createSlider("font-size-slider", isGeneSymbolPage ? 10 : 20, 1, 50, 1, (intValues) => {
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
            return scaleValue(ele.data("edge_size"), edgeMin, edgeMax, 0.5, 2) * (intValues * 0.4);
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

createSlider("nodeRepulsion-slider", defaultNodeRepulsion, 1, 10, 1, (intValues) => {
    nodeRepulsionValue = scaleToOriginalRange(intValues, nodeRepulsionMin, nodeRepulsionMax);
    componentSpacingValue = scaleToOriginalRange(intValues, componentSpacingMin, componentSpacingMax);
    document.getElementById("node-repulsion-value").textContent = intValues;
    cy.layout(getLayoutOptions()).run();
});

// ############################################################################
// Initialize centrality system
// ############################################################################

// Initialize centrality system with dependencies
initializeCentralitySystem(cy, createSlider);

// Make recalculateCentrality available globally for use in filters
window.recalculateCentrality = recalculateCentrality;

// ############################################################################
// Tooltip handling
// ############################################################################

// Show tooltip on tap
cy.on("tap", "node, edge", function (event) {
    showTooltip(event, cy, map_symbol_to_id, target_phenotype, nodeColorMin, nodeColorMax, edgeMin, edgeMax, nodeSizes);
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

// --------------------------------------------------------
// GraphML Exporter (Desktop Cytoscape Compatible)
// --------------------------------------------------------

document.getElementById("export-graphml").addEventListener("click", function () {
    exportGraphAsGraphML(cy, file_name);
});

// --------------------------------------------------------
// Mobile Export buttons
// --------------------------------------------------------

document.getElementById("export-png-mobile").addEventListener("click", function () {
    exportGraphAsPNG(cy, file_name);
});

document.getElementById("export-csv-mobile").addEventListener("click", function () {
    exportGraphAsCSV(cy, file_name);
});

document.getElementById("export-graphml-mobile").addEventListener("click", function () {
    exportGraphAsGraphML(cy, file_name);
});

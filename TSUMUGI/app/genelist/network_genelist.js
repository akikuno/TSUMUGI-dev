import { exportGraphAsPNG, exportGraphAsCSV } from "../js/exporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showTooltip } from "../js/tooltips.js";
import { calculateConnectedComponents } from "../js/components.js";
import { createSlider } from "../js/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/filters.js";
import { loadJSONGz, loadJSON } from "../js/data_loader.js";
import { setupGeneSearch } from "../js/searcher.js";
import { highlightDiseaseAnnotation } from "../js/highlighter.js";

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

const elements = JSON.parse(localStorage.getItem("elements"));
const map_symbol_to_id = loadJSON("../../data/marker_symbol_accession_id.json");

// ############################################################################
// Cytoscape Elements handler
// ############################################################################

let nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
let nodeColorMin = Math.min(...nodeSizes); // 色表示用の元の範囲
let nodeColorMax = Math.max(...nodeSizes); // 色表示用の元の範囲

// フィルタリング用の範囲（元の値をコピー）
let nodeMin = nodeColorMin;
let nodeMax = nodeColorMax;

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
                "border-width": 3,
                "border-color": "#fc4c00",
            },
        },
        {
            selector: ".gene-highlight", // 遺伝子検索ハイライト用クラス
            style: {
                color: "#028760",
                "font-weight": "bold",
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
        console.log("📱 Mobile device detected - applying mobile fixes");
        cy.resize();
        cy.fit();
        cy.center();
    }
}, 500);

// ウィンドウリサイズ時の対応
window.addEventListener("resize", handleMobileResize);

// オリエンテーション変更時の対応（モバイル）
window.addEventListener("orientationchange", () => {
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
noUiSlider.create(edgeSlider, { start: [1, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

// Update the slider values when the sliders are moved
edgeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("edge-size-value").textContent = intValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. 一旦すべてのノードを表示
    cy.nodes().forEach((node) => node.style("display", "element"));

    // 2. edge_size 条件に基づきエッジの表示/非表示を設定
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";
        const isVisible =
            sourceVisible &&
            targetVisible &&
            edgeSize >= Math.min(edgeMinValue, edgeMaxValue) &&
            edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. node_color === 1 を含むクラスタだけ残す
    const components = calculateConnectedComponents(cy);
    const validComponents = components.filter((comp) =>
        Object.keys(comp).some((label) => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        }),
    );

    // 4. 対象クラスタのノードとエッジを再表示
    validComponents.forEach((comp) => {
        Object.keys(comp).forEach((label) => {
            const node = cy.$(`node[label="${label}"]`);
            node.style("display", "element");
            node.connectedEdges().forEach((edge) => {
                const edgeSize = edge.data("edge_size");
                if (
                    edgeSize >= Math.min(edgeMinValue, edgeMaxValue) &&
                    edgeSize <= Math.max(edgeMinValue, edgeMaxValue)
                ) {
                    edge.style("display", "element");
                }
            });
        });
    });

    // 5. 孤立ノードを非表示にする
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 6. レイアウト再適用
    cy.layout(getLayoutOptions()).run();
}

// =============================================================================
// 遺伝型・性差・ライフステージ特異的フィルタリング関数
// =============================================================================

let target_phenotype = "";

// フィルタリング関数のラッパー
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterByNodeColorAndEdgeSize);
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

const file_name = "TSUMUGI_geneList";

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

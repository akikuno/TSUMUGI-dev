import { exportGraphAsPNG, exportGraphAsCSV } from "../js/exporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showTooltip } from "../js/tooltips.js";
import { calculateConnectedComponents } from "../js/components.js";
import { createSlider } from "../js/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/filters.js";
import { loadJSONGz, loadJSON } from "../js/data_loader.js";

// ############################################################################
// Input handling
// ############################################################################

// localStorage からデータを取得
const elements = JSON.parse(localStorage.getItem("elements"));

// REMOVE_FROM_THIS_LINE
const url_map_symbol_to_id =
    "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/1481158ce41ef5165be3c0e17d4b83b6d265b783/gist_marker_symbol_accession_id.json";
// REMOVE_TO_THIS_LINE

/* REMOVE_THIS_LINE
const url_map_symbol_to_id = "../../data/marker_symbol_accession_id.json";
REMOVE_THIS_LINE */

const map_symbol_to_id = loadJSON(url_map_symbol_to_id);

// ############################################################################
// Cytoscape handling
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

const nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

const nodeMin = Math.min(...nodeSizes);
const nodeMax = Math.max(...nodeSizes);
const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);

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

    // すべてのノードを一旦表示状態にする
    cy.nodes().forEach(node => node.style("display", "element"));

    // edge_sizeの範囲でエッジをフィルターし、表示/非表示を設定
    cy.edges().forEach(edge => {
        const edgeSize = edge.data("edge_size");
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";

        const isEdgeVisible = (
            sourceVisible &&
            targetVisible &&
            edgeSize >= edgeMinValue &&
            edgeSize <= edgeMaxValue
        );

        edge.style("display", isEdgeVisible ? "element" : "none");
    });

    // calculateConnectedComponentsを利用して連結成分を取得
    const connected_component = calculateConnectedComponents(cy);


    // 連結成分を取得し、node_color === 1 を含むものだけ残す
    const connectedComponents = calculateConnectedComponents(cy);
    const componentsWithColor1 = connectedComponents.filter(component =>
        Object.keys(component).some(label => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        })
    );

    // 残すべきコンポーネント内のノードと、edge_size条件を満たすエッジを再表示
    componentsWithColor1.forEach(component => {
        Object.keys(component).forEach(label => {
            const node = cy.$(`node[label="${label}"]`);
            node.style("display", "element");

            node.connectedEdges().forEach(edge => {
                const edgeSize = edge.data("edge_size");
                if (edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue) {
                    edge.style("display", "element");
                }
            });
        });
    });

    // 接続エッジがすべて非表示のノードは非表示にする（孤立ノードの除去）
    cy.nodes().forEach(node => {
        const visibleEdges = node.connectedEdges().filter(edge => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // フィルタ後のレイアウトを再適用
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

const input = document.getElementById("gene-search");
const suggestionsList = document.getElementById("suggestions");

let geneLabels = [];

cy.ready(() => {
    geneLabels = cy.nodes().map(node => node.data("label"));
});

// 入力ごとに候補を表示
input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    suggestionsList.innerHTML = "";

    if (!query) {
        suggestionsList.hidden = true;
        return;
    }

    const matched = geneLabels.filter(label => label.toLowerCase().includes(query)).slice(0, 10);
    if (matched.length === 0) {
        suggestionsList.hidden = true;
        return;
    }

    matched.forEach(label => {
        const li = document.createElement("li");
        li.textContent = label;
        li.addEventListener("mousedown", () => {
            input.value = label;
            suggestionsList.hidden = true;
        });
        suggestionsList.appendChild(li);
    });

    suggestionsList.hidden = false;
});

// 入力欄からフォーカスを外したら非表示
input.addEventListener("blur", () => {
    setTimeout(() => {
        suggestionsList.hidden = true;
    }, 100);
});


document.getElementById("search-button").addEventListener("click", () => {
    const query = document.getElementById("gene-search").value.trim().toLowerCase();

    // すべてのノードのハイライトをリセット
    cy.nodes().forEach(node => {
        node.style("border-width", 0);
        node.style("border-color", "transparent");
    });

    // 遺伝子名でノードを検索し、見つけたらハイライト
    const matchedNode = cy.nodes().filter(node => node.data("label").toLowerCase() === query);
    if (matchedNode.length > 0) {
        matchedNode.style("border-width", 2);
        matchedNode.style("border-color", "#e66900");
        cy.center(matchedNode);
        cy.animate({
            center: { eles: matchedNode },
            duration: 500
        });
    } else {
        alert("Gene not found in the network.");
    }
});

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

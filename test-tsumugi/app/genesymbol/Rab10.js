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


const url_elements = "../../data/genesymbol/Rab10.json.gz";
const url_map_symbol_to_id = "../../data/marker_symbol_accession_id.json";

const elements = loadJSONGz(url_elements);
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
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(parseFloat);

    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    cy.nodes().forEach(function (node) {
        node.style("display", "element");
    });

    // Filter edges based on size
    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data("edge_size");
        const sourceNode = cy.getElementById(edge.data("source"));
        const targetNode = cy.getElementById(edge.data("target"));

        if (
            sourceNode.style("display") === "element" &&
            targetNode.style("display") === "element" &&
            edgeSize >= edgeMinValue &&
            edgeSize <= edgeMaxValue
        ) {
            edge.style("display", "element");
        } else {
            edge.style("display", "none");
        }
    });

    // calculateConnectedComponentsを利用して連結成分を取得
    const connected_component = calculateConnectedComponents(cy);

    // node_colorが1のノードを含む連結成分のみを選択
    const componentsWithNodeColor1 = connected_component.filter((component) => {
        return Object.keys(component).some((nodeLabel) => {
            const node = cy.$(`node[label="${nodeLabel}"]`);
            return node.data("node_color") === 1;
        });
    });

    // すべてのノードとエッジを一旦非表示にする
    cy.nodes().style("display", "none");
    cy.edges().style("display", "none");

    // node_colorが1のノードを含む連結成分のみ表示
    componentsWithNodeColor1.forEach((component) => {
        Object.keys(component).forEach((nodeLabel) => {
            const node = cy.$(`node[label="${nodeLabel}"]`);
            node.style("display", "element");
            node.connectedEdges().style("display", "element");
        });
    });

    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (connectedEdges.length === 0) {
            node.style("display", "none"); // Hide node if no connected edges
        }
    });

    // Reapply layout after filtering
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

const file_name = "TSUMUGI_Rab10";

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

import { exportGraphAsPNG, exportGraphAsJPG, exportGraphAsCSV, exportGraphAsGraphML } from "../js/export/graphExporter.js";
import { scaleToOriginalRange, scaleValue, getColorForValue } from "../js/graph/valueScaler.js";
import { initInfoTooltips, removeTooltips, showTooltip } from "../js/ui/tooltips.js";
import { calculateConnectedComponents } from "../js/graph/components.js";
import { createSlider } from "../js/ui/slider.js";
import { filterElementsByGenotypeAndSex } from "../js/graph/filters.js";
import { loadJSON } from "../js/data/dataLoader.js";
import { setupGeneSearch } from "../js/search/geneSearcher.js";
import { highlightDiseaseAnnotation } from "../js/graph/highlighter.js";
import { setupPhenotypeSearch } from "../js/search/phenotypeSearcher.js";
import { initDynamicFontSize } from "../js/ui/dynamicFontSize.js";
import { initMobilePanel } from "../js/ui/mobilePanel.js";

// Initialize DOM-dependent UI helpers.
initInfoTooltips();
initDynamicFontSize();
initMobilePanel();

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

// const mapSymbolToId = { 'Nanog': 'MGI:97281', 'Pou5f1': 'MGI:1352748', 'Sox2': 'MGI:96217' };

// REMOVE_TO_THIS_LINE

const elements = JSON.parse(localStorage.getItem("elements"));
const mapSymbolToId = loadJSON("../../data/marker_symbol_accession_id.json");

// ############################################################################
// Cytoscape Elements handler
// ############################################################################

const nodeColorValues = elements
    .filter((ele) => ele.data.node_color !== undefined)
    .map((ele) => ele.data.node_color);
const nodeColorMin = Math.min(...nodeColorValues); // Range used for color styling
const nodeColorMax = Math.max(...nodeColorValues); // Range used for color styling

// Copy the original range so filtering can adjust independently
let nodeMin = nodeColorMin;
let nodeMax = nodeColorMax;

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);

// ############################################################################
// Initialize Cytoscape
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
                    const color_value = scaleValue(originalColor, nodeColorMin, nodeColorMax, 1, 100);
                    return getColorForValue(color_value, 1, 100);
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
            selector: ".disease-highlight", // Class used for disease highlighting
            style: {
                "border-width": 3,
                "border-color": "#fc4c00",
            },
        },
        {
            selector: ".gene-highlight", // Class used when highlighting gene search hits
            style: {
                color: "#028760",
                "font-weight": "bold",
            },
        },
        {
            selector: ".phenotype-highlight", // Class used for phenotype search highlighting
            style: {
                "border-width": 3,
                "border-color": "#28a745",
            },
        },
    ],
    layout: getLayoutOptions(),
});

// * Expose cy globally for debugging convenience
window.cy = cy;

// * Improve Cytoscape rendering on mobile devices
function handleMobileResize() {
    if (cy) {
        // Re-render Cytoscape after layout tweaks on mobile
        setTimeout(() => {
            cy.resize();
            cy.fit();
            cy.center();
        }, 300);
    }
}

// Adjust Cytoscape once initialization finishes on mobile
setTimeout(() => {
    if (window.innerWidth <= 600) {
        cy.resize();
        cy.fit();
        cy.center();
    }
}, 500);

// Handle browser resize events
window.addEventListener("resize", handleMobileResize);

// Handle orientation changes on mobile
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
// Slider initialization and filtering helpers
// =============================================================================

// --------------------------------------------------------
// Edge size slider for Phenotypes similarity
// --------------------------------------------------------

// Initialization of the Edge size slider
const edgeSlider = document.getElementById("filter-edge-slider");
noUiSlider.create(edgeSlider, { start: [1, 100], connect: true, range: { min: 1, max: 100 }, step: 1 });

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
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax, 1, 100);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax, 1, 100);

    // 1. Start by showing every node
    cy.nodes().forEach((node) => node.style("display", "element"));

    // 2. Show or hide edges according to the edge_size range
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

    // 3. Keep only the connected components that contain a node with node_color === 1
    const components = calculateConnectedComponents(cy);
    const validComponents = components.filter((comp) =>
        Object.keys(comp).some((label) => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        }),
    );

    // 4. Re-display nodes and edges for the retained components
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

    // 5. Hide isolated nodes
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 6. Re-run the layout
    cy.layout(getLayoutOptions()).run();

    // 7. Refresh the phenotype list so only visible genes remain
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
}

// =============================================================================
// Genotype, sex, and life-stage specific filtering
// =============================================================================

let targetPhenotype = "";

// Wrapper function that applies the filters
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, targetPhenotype, filterByNodeColorAndEdgeSize);
}

// Reapply filters whenever the form values change
document.getElementById("genotype-filter-form").addEventListener("change", applyFiltering);
document.getElementById("sex-filter-form").addEventListener("change", applyFiltering);
document.getElementById("lifestage-filter-form").addEventListener("change", applyFiltering);

// =============================================================================
// Highlight human disease annotations
// =============================================================================
highlightDiseaseAnnotation({ cy });

// ############################################################################
// Cytoscape's visualization setting
// ############################################################################

// --------------------------------------------------------
// Gene name search
// --------------------------------------------------------

setupGeneSearch({ cy });

// =============================================================================
// Phenotype highlighting (with search support)
// =============================================================================
setupPhenotypeSearch({ cy, elements });

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
    showTooltip(event, cy, mapSymbolToId, targetPhenotype, { nodeColorValues });
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

const fileName = "TSUMUGI_geneList";

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

const exportPngButton = document.getElementById("export-png");
if (exportPngButton) {
    exportPngButton.addEventListener("click", function () {
        exportGraphAsPNG(cy, fileName);
    });
}

const exportJpgButton = document.getElementById("export-jpg");
if (exportJpgButton) {
    exportJpgButton.addEventListener("click", function () {
        exportGraphAsJPG(cy, fileName);
    });
}

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

const exportCsvButton = document.getElementById("export-csv");
if (exportCsvButton) {
    exportCsvButton.addEventListener("click", function () {
        exportGraphAsCSV(cy, fileName);
    });
}

// --------------------------------------------------------
// GraphML Exporter (Desktop Cytoscape Compatible)
// --------------------------------------------------------

const exportGraphmlButton = document.getElementById("export-graphml");
if (exportGraphmlButton) {
    exportGraphmlButton.addEventListener("click", function () {
        exportGraphAsGraphML(cy, fileName);
    });
}

import { exportGraphAsPNG, exportGraphAsJPG, exportGraphAsCSV, exportGraphAsGraphML } from "../js/exporter.js";
import { scaleToOriginalRange, getColorForValue } from "../js/value_scaler.js";
import { removeTooltips, showSubnetworkTooltip, showTooltip } from "../js/tooltips.js";
import { getOrderedComponents } from "../js/components.js";
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
let nodeColorMin = Math.min(...nodeSizes);  // Range used for color styling
let nodeColorMax = Math.max(...nodeSizes);  // Range used for color styling

// Copy the original range so filtering can adjust independently
let nodeMin = nodeColorMin;
let nodeMax = nodeColorMax;

XXX_NODE_MIN_MAX

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);

XXX_EDGE_MIN_MAX

function mapEdgeSizeToWidth(edgeSize) {
    if (edgeMax === edgeMin) {
        return 1.5;
    }
    const normalized = (edgeSize - edgeMin) / (edgeMax - edgeMin);
    return 0.5 + normalized * 1.5;
}

// ############################################################################
// Initialize Cytoscape
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
            idealEdgeLength: 100,
            nodeOverlap: 20,
            padding: 30,
            animate: true,
            animationDuration: 500,
            gravity: -1.2,
            numIter: 1500,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0,
            edgeElasticity: 100,
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
                    return getColorForValue(originalColor, nodeColorMin, nodeColorMax);
                },
            },
        },
        {
            selector: "edge",
            style: {
                "curve-style": "bezier",
                "text-rotation": "autorotate",
                width: function (ele) {
                    return mapEdgeSizeToWidth(ele.data("edge_size"));
                },
            },
        },
        {
            selector: ".disease-highlight", // Class used for disease highlighting
            style: {
                "border-width": 5,
                "border-color": "#fc4c00",
            },
        },
        {
            selector: ".gene-highlight", // Class used when highlighting gene search hits
            style: {
                "color": "#006400",
                "font-weight": "bold",
            },
        },
        {
            selector: ".phenotype-highlight", // Class used for phenotype search highlighting
            style: {
                "border-width": 5,
                "border-color": "#3FA7D6",
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
window.addEventListener('resize', handleMobileResize);

// Handle orientation changes on mobile
window.addEventListener('orientationchange', () => {
    setTimeout(handleMobileResize, 500);
});

// ############################################################################
// Module（連結成分）フレーム＆ツールチップ
// ############################################################################

const subnetworkOverlay = createSubnetworkOverlay();
let subnetworkMeta = [];
let isFrameUpdateQueued = false;
let subnetworkDragState = null;

function createSubnetworkOverlay() {
    const cyContainer = document.querySelector(".cy");
    const overlay = document.createElement("div");
    overlay.classList.add("subnetwork-overlay");
    cyContainer.appendChild(overlay);
    return overlay;
}

function summarizeEdgePhenotypes(component) {
    const counts = new Map();
    component
        .edges()
        .filter((edge) => edge.visible())
        .forEach((edge) => {
            const phenotypes = Array.isArray(edge.data("phenotype"))
                ? edge.data("phenotype")
                : edge.data("phenotype")
                    ? [edge.data("phenotype")]
                    : [];
            phenotypes.forEach((name) => {
                counts.set(name, (counts.get(name) || 0) + 1);
            });
        });

    return [...counts.entries()].sort((a, b) => {
        if (b[1] === a[1]) {
            return a[0].localeCompare(b[0]);
        }
        return b[1] - a[1];
    });
}

function updateSubnetworkFrames() {
    if (!subnetworkOverlay) return;
    subnetworkOverlay.innerHTML = "";
    subnetworkMeta = [];

    const visibleComponents = getOrderedComponents(cy);
    const padding = 16;
    const containerWidth = cy.width();
    const containerHeight = cy.height();

    visibleComponents.forEach((component, idx) => {
        if (component.nodes().length === 0) return;
        const bbox = component.renderedBoundingBox({ includeOverlays: false, includeLabels: true });
        if (!bbox || !Number.isFinite(bbox.x1) || !Number.isFinite(bbox.y1)) {
            return;
        }

        const left = Math.max(0, bbox.x1 - padding);
        const top = Math.max(0, bbox.y1 - padding);
        const width = Math.min(containerWidth - left, bbox.w + padding * 2);
        const height = Math.min(containerHeight - top, bbox.h + padding * 2);

        if (width <= 0 || height <= 0) return;

        const frame = document.createElement("div");
        frame.classList.add("subnetwork-frame");
        frame.dataset.componentId = String(idx + 1);
        frame.style.left = `${left}px`;
        frame.style.top = `${top}px`;
        frame.style.width = `${width}px`;
        frame.style.height = `${height}px`;

        const label = document.createElement("div");
        label.classList.add("subnetwork-frame__label");
        label.textContent = `Module ${idx + 1}`;
        label.dataset.componentId = String(idx + 1);
        frame.appendChild(label);

        subnetworkOverlay.appendChild(frame);
        attachFrameDragHandlers(frame, label);

        const summary = summarizeEdgePhenotypes(component);
        subnetworkMeta.push({
            id: idx + 1,
            bbox: { x1: left, y1: top, x2: left + width, y2: top + height },
            phenotypes: summary,
            nodes: component.nodes(),
        });
    });
}

function scheduleSubnetworkFrameUpdate() {
    if (isFrameUpdateQueued) return;
    isFrameUpdateQueued = true;
    requestAnimationFrame(() => {
        updateSubnetworkFrames();
        isFrameUpdateQueued = false;
    });
}

function findComponentByPosition(renderedPos) {
    return subnetworkMeta.find(
        (component) =>
            renderedPos.x >= component.bbox.x1 &&
            renderedPos.x <= component.bbox.x2 &&
            renderedPos.y >= component.bbox.y1 &&
            renderedPos.y <= component.bbox.y2,
    );
}

function pointerToRenderedPos(evt) {
    const containerRect = document.querySelector(".cy").getBoundingClientRect();
    if (evt.touches && evt.touches.length > 0) {
        return {
            x: evt.touches[0].clientX - containerRect.left,
            y: evt.touches[0].clientY - containerRect.top,
        };
    }
    return {
        x: evt.clientX - containerRect.left,
        y: evt.clientY - containerRect.top,
    };
}

function startFrameDrag(evt) {
    const compId = Number(evt.currentTarget.dataset.componentId);
    const component = subnetworkMeta.find((c) => c.id === compId);
    if (!component) return;

    evt.preventDefault();
    evt.stopPropagation();

    const nodes = component.nodes.filter((n) => n.visible());
    const startRendered = pointerToRenderedPos(evt);
    subnetworkDragState = {
        componentId: compId,
        startRendered,
        zoom: cy.zoom(),
        nodes: nodes.map((n) => ({ node: n, pos: { ...n.position() } })),
    };

    document.addEventListener("mousemove", onFrameDragMove);
    document.addEventListener("touchmove", onFrameDragMove, { passive: false });
    document.addEventListener("mouseup", endFrameDrag);
    document.addEventListener("touchend", endFrameDrag);
}

function onFrameDragMove(evt) {
    if (!subnetworkDragState) return;
    if (evt.cancelable) {
        evt.preventDefault();
    }

    const currentRendered = pointerToRenderedPos(evt);
    const dxRendered = currentRendered.x - subnetworkDragState.startRendered.x;
    const dyRendered = currentRendered.y - subnetworkDragState.startRendered.y;
    const zoom = subnetworkDragState.zoom || 1;
    const dx = dxRendered / zoom;
    const dy = dyRendered / zoom;

    subnetworkDragState.nodes.forEach(({ node, pos }) => {
        node.position({ x: pos.x + dx, y: pos.y + dy });
    });

    scheduleSubnetworkFrameUpdate();
}

function endFrameDrag() {
    subnetworkDragState = null;
    document.removeEventListener("mousemove", onFrameDragMove);
    document.removeEventListener("touchmove", onFrameDragMove);
    document.removeEventListener("mouseup", endFrameDrag);
    document.removeEventListener("touchend", endFrameDrag);
}

function attachFrameDragHandlers(frame, handleElement = frame) {
    const handle = handleElement;
    handle.addEventListener("mousedown", startFrameDrag);
    handle.addEventListener("touchstart", startFrameDrag, { passive: false });
    handle.addEventListener("click", (evt) => {
        const compId = Number((evt.currentTarget || frame).dataset.componentId);
        const component = subnetworkMeta.find((c) => c.id === compId);
        if (!component) return;
        const renderedPos = pointerToRenderedPos(evt);
        showSubnetworkTooltip({ component, renderedPos });
    });
}

cy.on("layoutstop zoom pan", scheduleSubnetworkFrameUpdate);
window.addEventListener("resize", scheduleSubnetworkFrameUpdate);
scheduleSubnetworkFrameUpdate();


// ############################################################################
// Control panel handler
// ############################################################################

// --------------------------------------------------------
// Network layout dropdown
// --------------------------------------------------------
document.getElementById("layout-dropdown").addEventListener("change", function () {
    currentLayout = this.value;
    cy.layout(getLayoutOptions()).run();
});

// =============================================================================
// Slider initialization and filtering helpers
// =============================================================================

// --------------------------------------------------------
// Edge size slider for Phenotypes similarity
// --------------------------------------------------------

// Initialization of the Edge size slider
const edgeSlider = document.getElementById("filter-edge-slider");
const EDGE_SLIDER_MIN = 1;
const EDGE_SLIDER_MAX = 100;
let edgeSliderRangeMin = EDGE_SLIDER_MIN;
let edgeSliderRangeMax = EDGE_SLIDER_MAX;
let edgeSliderStartMin = EDGE_SLIDER_MIN;
let edgeSliderStartMax = EDGE_SLIDER_MAX;

if (isGeneSymbolPage) {
    edgeSliderRangeMin = edgeMin;
    edgeSliderRangeMax = edgeMax === edgeMin ? edgeMin + 1 : edgeMax;
    edgeSliderStartMin = edgeSliderRangeMin;
    edgeSliderStartMax = edgeSliderRangeMax;
}

noUiSlider.create(edgeSlider, {
    start: [edgeSliderStartMin, edgeSliderStartMax],
    connect: true,
    range: { min: edgeSliderRangeMin, max: edgeSliderRangeMax },
    step: 1,
});

XXX_NODE_COLOR_INITIALIZATION

// Update the slider values when the sliders are moved
edgeSlider.noUiSlider.on("update", function (values) {
    const formattedValues = values.map((value) => Math.round(Number(value)));
    document.getElementById("edge-size-value").textContent = formattedValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});

XXX_NODE_COLOR_UPDATE

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE

// =============================================================================
// Genotype, sex, and life-stage specific filtering
// =============================================================================

let target_phenotype = "XXX_PHENOTYPE";

// Wrapper function that applies the filters
function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterByNodeColorAndEdgeSize);
    // Recalculate centrality after filtering
    if (typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
}

// Trigger filtering when any form value changes
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
            const baseWidth = mapEdgeSizeToWidth(ele.data("edge_size"));
            return baseWidth * (intValues * 0.4);
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

// 背景をタップしたときにModuleのツールチップを表示/非表示
cy.on("tap", function (event) {
    if (event.target !== cy) {
        return;
    }

    const renderedPos = event.renderedPosition || event.position || { x: 0, y: 0 };
    const component = findComponentByPosition(renderedPos);
    if (component) {
        showSubnetworkTooltip({ component, renderedPos });
    } else {
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

const exportPngButton = document.getElementById("export-png");
if (exportPngButton) {
    exportPngButton.addEventListener("click", function () {
        exportGraphAsPNG(cy, file_name);
    });
}

const exportJpgButton = document.getElementById("export-jpg");
if (exportJpgButton) {
    exportJpgButton.addEventListener("click", function () {
        exportGraphAsJPG(cy, file_name);
    });
}

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

const exportCsvButton = document.getElementById("export-csv");
if (exportCsvButton) {
    exportCsvButton.addEventListener("click", function () {
        exportGraphAsCSV(cy, file_name);
    });
}

// --------------------------------------------------------
// GraphML Exporter (Desktop Cytoscape Compatible)
// --------------------------------------------------------

const exportGraphmlButton = document.getElementById("export-graphml");
if (exportGraphmlButton) {
    exportGraphmlButton.addEventListener("click", function () {
        exportGraphAsGraphML(cy, file_name);
    });
}

// --------------------------------------------------------
// Mobile Export buttons
// --------------------------------------------------------

const exportPngMobileButton = document.getElementById("export-png-mobile");
if (exportPngMobileButton) {
    exportPngMobileButton.addEventListener("click", function () {
        exportGraphAsPNG(cy, file_name);
    });
}

const exportJpgMobileButton = document.getElementById("export-jpg-mobile");
if (exportJpgMobileButton) {
    exportJpgMobileButton.addEventListener("click", function () {
        exportGraphAsJPG(cy, file_name);
    });
}

const exportCsvMobileButton = document.getElementById("export-csv-mobile");
if (exportCsvMobileButton) {
    exportCsvMobileButton.addEventListener("click", function () {
        exportGraphAsCSV(cy, file_name);
    });
}

const exportGraphmlMobileButton = document.getElementById("export-graphml-mobile");
if (exportGraphmlMobileButton) {
    exportGraphmlMobileButton.addEventListener("click", function () {
        exportGraphAsGraphML(cy, file_name);
    });
}

import { exportGraphAsPNG, exportGraphAsJPG, exportGraphAsCSV, exportGraphAsGraphML, exportGraphAsSVG } from "./js/export/graphExporter.js";
import { scaleToOriginalRange, getColorForValue } from "./js/graph/valueScaler.js";
import { initInfoTooltips, removeTooltips, showSubnetworkTooltip, showTooltip } from "./js/ui/tooltips.js";
import { getOrderedComponents, calculateConnectedComponents } from "./js/graph/components.js";
import { createSlider } from "./js/ui/slider.js";
import { filterElementsByGenotypeAndSex } from "./js/graph/filters.js";
import { loadJSON } from "./js/data/dataLoader.js";
import {
    applyNodeMinMax,
    getPageConfig,
    hidePhenotypeOnlySections,
    isBinaryPhenotypeElements,
    loadElementsForConfig,
    renderEmptyState,
    setPageTitle,
    setVersionLabel,
} from "./js/viewer/pageSetup.js";
import { createLayoutController } from "./js/graph/layoutController.js";
import { setupGeneSearch } from "./js/search/geneSearcher.js";
import { highlightDiseaseAnnotation } from "./js/graph/highlighter.js";
import { setupPhenotypeSearch } from "./js/search/phenotypeSearcher.js";
import { initializeCentralitySystem, recalculateCentrality } from "./js/graph/centrality.js";
import { initDynamicFontSize } from "./js/ui/dynamicFontSize.js";
import { initMobilePanel } from "./js/ui/mobilePanel.js";

if (window.cytoscape && window.cytoscapeSvg && typeof window.cytoscape.use === "function") {
    window.cytoscape.use(window.cytoscapeSvg);
}

const NODE_SLIDER_MIN = 1;
const NODE_SLIDER_MAX = 100;
const EDGE_SLIDER_MIN = 1;
const EDGE_SLIDER_MAX = 100;
const AUTO_ARRANGE_DELAY_MS = 150;
const AUTO_ARRANGE_LAYOUT_TIMEOUT_MS = 4000;
const AUTO_ARRANGE_REPULSION_TIMEOUT_MS = 2000;
const INITIAL_AUTO_ARRANGE_TIMEOUT_MS = 15000;
const INITIAL_ARRANGE_CLICK_DELAY_MS = 500;
const REPULSION_FINISH_EVENT = "tsumugi:repulsion:finish";

// Initialize UI helpers that only depend on DOM availability.
initInfoTooltips();
initDynamicFontSize();
initMobilePanel();

// Track which search mode is active in this viewer
const pageConfig = getPageConfig();
const isPhenotypePage = pageConfig.mode === "phenotype";
const isGeneSymbolPage = pageConfig.mode === "genesymbol";

setVersionLabel();

const mapSymbolToId = loadJSON("../data/marker_symbol_accession_id.json") || {};
const mapPhenotypeToId = loadJSON("../data/mp_term_id_lookup.json") || {};
setPageTitle(pageConfig, mapSymbolToId, mapPhenotypeToId);

const elements = loadElementsForConfig(pageConfig);
if (!elements || elements.length === 0) {
    renderEmptyState("No data found. Please check your input.");
    throw new Error("No elements available to render");
}

const isBinaryPhenotype = isPhenotypePage && isBinaryPhenotypeElements(elements);
hidePhenotypeOnlySections(isPhenotypePage && !isBinaryPhenotype);

// ############################################################################
// Input handler
// ############################################################################

const nodeColorValues = elements
    .filter((ele) => ele.data.node_color !== undefined)
    .map((ele) => ele.data.node_color);
const nodeColorMin = nodeColorValues.length ? Math.min(...nodeColorValues) : 0;
const nodeColorMax = nodeColorValues.length ? Math.max(...nodeColorValues) : 1;

let nodeMin = nodeColorMin;
let nodeMax = nodeColorMax;

if (isPhenotypePage) {
    const adjusted = applyNodeMinMax(elements, nodeColorMin, nodeColorMax);
    nodeMin = adjusted.nodeMin;
    nodeMax = adjusted.nodeMax;
}

const edgeSizes = elements.filter((ele) => ele.data.edge_size !== undefined).map((ele) => ele.data.edge_size);
const edgeMin = edgeSizes.length ? Math.min(...edgeSizes) : 0;
const edgeMax = edgeSizes.length ? Math.max(...edgeSizes) : 1;

const baseElements = JSON.parse(JSON.stringify(elements));

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

const defaultNodeRepulsion = 5;
const layoutController = createLayoutController({
    isGeneSymbolPage,
    defaultNodeRepulsion,
});

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
            selector: "node.dim-node",
            style: {
                opacity: 0.05,
            },
        },
        {
            selector: "edge.dim-edge",
            style: {
                opacity: 0.05,
            },
        },
        {
            selector: "node.focus-node",
            style: {
                opacity: 1,
            },
        },
        {
            selector: "edge.focus-edge",
            style: {
                opacity: 1,
            },
        },
        {
            selector: ".disease-highlight",
            style: {
                "border-width": 5,
                "border-color": "#fc4c00",
            },
        },
        {
            selector: ".gene-highlight",
            style: {
                "color": "#006400",
                "font-weight": "bold",
            },
        },
        {
            selector: ".phenotype-highlight",
            style: {
                "border-width": 5,
                "border-color": "#3FA7D6",
            },
        },
    ],
    layout: layoutController.getLayoutOptions(),
    userZoomingEnabled: true,
    zoomingEnabled: true,
    wheelSensitivity: 0.2,
});

window.cy = cy;
layoutController.attachCy(cy);
layoutController.registerInitialLayoutStop();
setupInitialAutoArrange();

const bodyContainer = document.querySelector(".body-container");
const leftPanelToggleButton = document.getElementById("toggle-left-panel");
const rightPanelToggleButton = document.getElementById("toggle-right-panel");

// Smooth wheel zoom on the Cytoscape canvas
const cyContainer = cy.container();
if (cyContainer) {
    cyContainer.addEventListener(
        "wheel",
        (event) => {
            event.preventDefault();
            const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
            const rect = cyContainer.getBoundingClientRect();
            const renderedPosition = {
                x: event.clientX - rect.left,
                y: event.clientY - rect.top,
            };
            const targetZoom = cy.zoom() * zoomFactor;
            const clampedZoom = Math.min(cy.maxZoom(), Math.max(cy.minZoom(), targetZoom));
            cy.zoom({ level: clampedZoom, renderedPosition });
            scheduleSubnetworkFrameUpdate();
        },
        { passive: false },
    );
}

function resetPanelStatesForMobile() {
    if (!bodyContainer) return;

    if (window.innerWidth <= 600) {
        const hadHiddenPanel =
            bodyContainer.classList.contains("left-panel-hidden") ||
            bodyContainer.classList.contains("right-panel-hidden");

        bodyContainer.classList.remove("left-panel-hidden", "right-panel-hidden");

        if (leftPanelToggleButton) {
            leftPanelToggleButton.classList.remove("collapsed");
            leftPanelToggleButton.setAttribute("aria-label", "Hide left panel");
        }

        if (rightPanelToggleButton) {
            rightPanelToggleButton.classList.remove("collapsed");
            rightPanelToggleButton.setAttribute("aria-label", "Hide right panel");
        }

        if (hadHiddenPanel) {
            refreshCyViewport();
        }
    }
}

function handleMobileResize() {
    resetPanelStatesForMobile();

    if (cy) {
        setTimeout(() => {
            refreshCyViewport();
        }, 300);
    }
}

setTimeout(() => {
    if (window.innerWidth <= 600) {
        resetPanelStatesForMobile();
        refreshCyViewport();
    }
}, 500);

window.addEventListener("resize", handleMobileResize);
window.addEventListener("orientationchange", () => {
    setTimeout(handleMobileResize, 500);
});

// ############################################################################
// Module (connected component) frames & tooltips
// ############################################################################

const subnetworkOverlay = createSubnetworkOverlay();
let subnetworkMeta = [];
let isFrameUpdateQueued = false;
let subnetworkDragState = null;
const COMPONENT_PADDING = 16;
const COMPONENT_MAX_ITER = 30;
const COMPONENT_FIT_PADDING = 40;

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

        const rawLeft = bbox.x1 - padding;
        const rawTop = bbox.y1 - padding;
        const rawRight = bbox.x1 + bbox.w + padding;
        const rawBottom = bbox.y1 + bbox.h + padding;

        const visibleLeft = Math.max(0, rawLeft);
        const visibleTop = Math.max(0, rawTop);
        const visibleRight = Math.min(containerWidth, rawRight);
        const visibleBottom = Math.min(containerHeight, rawBottom);

        const width = visibleRight - visibleLeft;
        const height = visibleBottom - visibleTop;

        if (width <= 0 || height <= 0) return;

        const frame = document.createElement("div");
        frame.classList.add("subnetwork-frame");
        frame.dataset.componentId = String(idx + 1);
        frame.style.left = `${visibleLeft}px`;
        frame.style.top = `${visibleTop}px`;
        frame.style.width = `${width}px`;
        frame.style.height = `${height}px`;

        const label = document.createElement("div");
        label.classList.add("subnetwork-frame__label");
        label.textContent = `Module ${idx + 1}`;
        label.dataset.componentId = String(idx + 1);
        frame.appendChild(label);

        const borders = ["top", "bottom", "left", "right"];
        borders.forEach((side) => {
            const border = document.createElement("div");
            border.classList.add("subnetwork-frame__border", `subnetwork-frame__border--${side}`);
            border.dataset.componentId = String(idx + 1);
            frame.appendChild(border);
            attachFrameDragHandlers(border, border);
        });

        subnetworkOverlay.appendChild(frame);
        attachFrameDragHandlers(frame, label);

        const summary = summarizeEdgePhenotypes(component);
        subnetworkMeta.push({
            id: idx + 1,
            bbox: { x1: visibleLeft, y1: visibleTop, x2: visibleLeft + width, y2: visibleTop + height },
            phenotypes: summary,
            nodes: component.nodes(),
        });
    });
}

function scheduleSubnetworkFrameUpdate(options = {}) {
    const { resolve = false, autoFit = false } = options;
    if (isFrameUpdateQueued) return;
    isFrameUpdateQueued = true;
    requestAnimationFrame(() => {
        if (resolve) {
            resolveComponentOverlaps();
        }
        updateSubnetworkFrames();
        if (autoFit) {
            fitVisibleComponents();
        }
        isFrameUpdateQueued = false;
    });
}

function translateComponent(comp, dx, dy) {
    comp.nodes().positions((node) => {
        const pos = node.position();
        return { x: pos.x + dx, y: pos.y + dy };
    });
}

function resolveComponentOverlaps() {
    const components = cy.elements(":visible").components().filter((comp) => comp.nodes().length > 0);
    if (components.length <= 1) return false;

    const zoom = cy.zoom() || 1;
    let movedAny = false;

    for (let iter = 0; iter < COMPONENT_MAX_ITER; iter++) {
        let moved = false;
        for (let i = 0; i < components.length; i++) {
            const bboxA = components[i].renderedBoundingBox({ includeLabels: true, includeOverlays: false });
            for (let j = i + 1; j < components.length; j++) {
                const bboxB = components[j].renderedBoundingBox({ includeLabels: true, includeOverlays: false });

                const ax1 = bboxA.x1 - COMPONENT_PADDING;
                const ax2 = bboxA.x2 + COMPONENT_PADDING;
                const ay1 = bboxA.y1 - COMPONENT_PADDING;
                const ay2 = bboxA.y2 + COMPONENT_PADDING;
                const bx1 = bboxB.x1 - COMPONENT_PADDING;
                const bx2 = bboxB.x2 + COMPONENT_PADDING;
                const by1 = bboxB.y1 - COMPONENT_PADDING;
                const by2 = bboxB.y2 + COMPONENT_PADDING;

                const overlapX = Math.min(ax2, bx2) - Math.max(ax1, bx1);
                const overlapY = Math.min(ay2, by2) - Math.max(ay1, by1);

                if (overlapX <= 0 || overlapY <= 0) {
                    continue;
                }

                const centerA = { x: (bboxA.x1 + bboxA.x2) / 2, y: (bboxA.y1 + bboxA.y2) / 2 };
                const centerB = { x: (bboxB.x1 + bboxB.x2) / 2, y: (bboxB.y1 + bboxB.y2) / 2 };
                let dx = centerB.x - centerA.x;
                let dy = centerB.y - centerA.y;
                if (Math.abs(dx) < 1 && Math.abs(dy) < 1) {
                    dx = 1;
                    dy = 0;
                }

                let shiftX = 0;
                let shiftY = 0;
                if (overlapX < overlapY) {
                    shiftX = Math.sign(dx) * (overlapX + COMPONENT_PADDING);
                } else {
                    shiftY = Math.sign(dy) * (overlapY + COMPONENT_PADDING);
                }

                translateComponent(components[j], shiftX / zoom, shiftY / zoom);
                moved = true;
                movedAny = true;
            }
        }
        if (!moved) {
            break;
        }
    }

    return movedAny;
}

function tileComponents() {
    const components = cy.elements(":visible").components().filter((comp) => comp.nodes().length > 0);
    if (components.length === 0) return false;

    const bboxes = components.map((comp) => comp.boundingBox({ includeLabels: true, includeOverlays: false }));
    const maxW = Math.max(...bboxes.map((b) => b.w));
    const maxH = Math.max(...bboxes.map((b) => b.h));
    const tilePadding = COMPONENT_PADDING;
    const tileW = maxW + tilePadding * 2;
    const tileH = maxH + tilePadding * 2;
    const cols = Math.max(1, Math.ceil(Math.sqrt(components.length)));

    components.forEach((comp, idx) => {
        const col = idx % cols;
        const row = Math.floor(idx / cols);
        const targetCenter = {
            x: col * tileW + tileW / 2,
            y: row * tileH + tileH / 2,
        };

        const bbox = bboxes[idx];
        const compCenter = {
            x: (bbox.x1 + bbox.x2) / 2,
            y: (bbox.y1 + bbox.y2) / 2,
        };

        translateComponent(comp, targetCenter.x - compCenter.x, targetCenter.y - compCenter.y);
    });

    return true;
}

function fitVisibleComponents() {
    const visibles = cy.elements(":visible");
    if (visibles && visibles.length > 0) {
        cy.fit(visibles, COMPONENT_FIT_PADDING);
    }
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
        showSubnetworkTooltip({ component, renderedPos, cyInstance: cy });
    });
}

cy.on("layoutstop", () => scheduleSubnetworkFrameUpdate({ resolve: true, autoFit: true }));
cy.on("zoom pan", () => scheduleSubnetworkFrameUpdate());
cy.on("position", "node", () => scheduleSubnetworkFrameUpdate());
window.addEventListener("resize", () => scheduleSubnetworkFrameUpdate());
scheduleSubnetworkFrameUpdate({ resolve: true, autoFit: true });

// ############################################################################
// Side panel toggles
// ############################################################################

function refreshCyViewport() {
    if (!cy) return;
    if (bodyContainer) {
        void bodyContainer.offsetWidth;
    }
    requestAnimationFrame(() => {
        cy.resize();
        cy.fit();
        cy.center();
        scheduleSubnetworkFrameUpdate();
    });
}

function toggleSidePanel(side) {
    if (!bodyContainer) return;

    const className = `${side}-panel-hidden`;
    const shouldHide = !bodyContainer.classList.contains(className);

    bodyContainer.classList.toggle(className, shouldHide);

    const targetButton = side === "left" ? leftPanelToggleButton : rightPanelToggleButton;
    if (targetButton) {
        targetButton.classList.toggle("collapsed", shouldHide);
        targetButton.setAttribute("aria-label", shouldHide ? `Show ${side} panel` : `Hide ${side} panel`);
    }

    refreshCyViewport();
}

function setupSidePanelToggles() {
    if (!leftPanelToggleButton || !rightPanelToggleButton || !bodyContainer) {
        return;
    }

    leftPanelToggleButton.addEventListener("click", () => toggleSidePanel("left"));
    rightPanelToggleButton.addEventListener("click", () => toggleSidePanel("right"));
}

setupSidePanelToggles();

// ############################################################################
// Control panel handler
// ############################################################################

// --------------------------------------------------------
// Network layout dropdown
// --------------------------------------------------------
document.getElementById("layout-dropdown").addEventListener("change", function () {
    layoutController.setLayout(this.value);
    layoutController.clearLayoutRefresh();
    queueAutoArrange({ afterLayout: true, delayMs: AUTO_ARRANGE_DELAY_MS });
    layoutController.runLayoutWithRepulsion();
});

// =============================================================================
// Slider initialization and filtering helpers
// =============================================================================

// --------------------------------------------------------
// Edge size slider for Phenotypes similarity
// --------------------------------------------------------

const edgeSlider = document.getElementById("filter-edge-slider");
let edgeSliderRangeMin = EDGE_SLIDER_MIN;
let edgeSliderRangeMax = EDGE_SLIDER_MAX;
let edgeSliderStartMin = EDGE_SLIDER_MIN;
let edgeSliderStartMax = EDGE_SLIDER_MAX;

if (isGeneSymbolPage) {
    edgeSliderRangeMin = edgeMin;
    edgeSliderRangeMax = edgeMax === edgeMin ? edgeMin + 1 : edgeMax;
    edgeSliderStartMin = edgeSliderRangeMin;
    edgeSliderStartMax = edgeSliderRangeMax;
} else {
    edgeSliderRangeMin = EDGE_SLIDER_MIN;
    edgeSliderRangeMax = EDGE_SLIDER_MAX;
    edgeSliderStartMin = EDGE_SLIDER_MIN;
    edgeSliderStartMax = EDGE_SLIDER_MAX;
}

if (edgeSlider) {
    noUiSlider.create(edgeSlider, {
        start: [edgeSliderStartMin, edgeSliderStartMax],
        connect: true,
        range: { min: edgeSliderRangeMin, max: edgeSliderRangeMax },
        step: 1,
    });
}

// --------------------------------------------------------
// Phenotype severity slider (Phenotype pages only)
// --------------------------------------------------------

const nodeSlider = document.getElementById("filter-node-slider");
if (isPhenotypePage && nodeSlider && !isBinaryPhenotype) {
    noUiSlider.create(nodeSlider, {
        start: [NODE_SLIDER_MIN, NODE_SLIDER_MAX],
        connect: true,
        range: { min: NODE_SLIDER_MIN, max: NODE_SLIDER_MAX },
        step: 1,
    });
}

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

let filterByNodeColorAndEdgeSize = () => { };

if (isPhenotypePage) {
    filterByNodeColorAndEdgeSize = function () {
        const hasNodeSlider = nodeSlider && nodeSlider.noUiSlider;
        const nodeSliderValues = hasNodeSlider
            ? nodeSlider.noUiSlider.get().map(Number)
            : [NODE_SLIDER_MIN, NODE_SLIDER_MAX];
        const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

        const nodeLowerBound = Math.min(nodeMin, nodeMax);
        const nodeUpperBound = Math.max(nodeMin, nodeMax);
        const rawNodeMin = Math.min(...nodeSliderValues);
        const rawNodeMax = Math.max(...nodeSliderValues);
        let nodeMinValue = scaleToOriginalRange(
            rawNodeMin,
            nodeLowerBound,
            nodeUpperBound,
            NODE_SLIDER_MIN,
            NODE_SLIDER_MAX,
        );
        let nodeMaxValue = scaleToOriginalRange(
            rawNodeMax,
            nodeLowerBound,
            nodeUpperBound,
            NODE_SLIDER_MIN,
            NODE_SLIDER_MAX,
        );
        if (nodeLowerBound === nodeUpperBound) {
            nodeMinValue = nodeLowerBound;
            nodeMaxValue = nodeUpperBound;
        }

        const rawEdgeMin = Math.min(...edgeSliderValues);
        const rawEdgeMax = Math.max(...edgeSliderValues);
        let edgeMinValue = scaleToOriginalRange(rawEdgeMin, edgeMin, edgeMax, EDGE_SLIDER_MIN, EDGE_SLIDER_MAX);
        let edgeMaxValue = scaleToOriginalRange(rawEdgeMax, edgeMin, edgeMax, EDGE_SLIDER_MIN, EDGE_SLIDER_MAX);
        if (edgeMin === edgeMax) {
            edgeMinValue = edgeMin;
            edgeMaxValue = edgeMax;
        }

        cy.nodes().forEach((node) => {
            const nodeColorForFilter = node.data("node_color_for_filter") || node.data("node_color");
            const isVisible =
                nodeColorForFilter >= Math.min(nodeMinValue, nodeMaxValue) &&
                nodeColorForFilter <= Math.max(nodeMinValue, nodeMaxValue);
            node.style("display", isVisible ? "element" : "none");
        });

        cy.edges().forEach((edge) => {
            const edgeSize = edge.data("edge_size");
            const sharedPhenotypes = edge.data("phenotype") || [];
            const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
            const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";

            const isVisible =
                sourceVisible &&
                targetVisible &&
                edgeSize >= Math.min(edgeMinValue, edgeMaxValue) &&
                edgeSize <= Math.max(edgeMinValue, edgeMaxValue) &&
                sharedPhenotypes.length >= 2;

            edge.style("display", isVisible ? "element" : "none");
        });

        cy.nodes().forEach((node) => {
            const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
            if (visibleEdges.length === 0) {
                node.style("display", "none");
            }
        });

        layoutController.runLayoutWithRepulsion();
        checkEmptyState();

        if (window.refreshPhenotypeList) {
            window.refreshPhenotypeList();
        }

        if (typeof window.recalculateCentrality === "function") {
            window.recalculateCentrality();
        }
    };
} else if (isGeneSymbolPage) {
    filterByNodeColorAndEdgeSize = function () {
        const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

        let selectedMin = Math.min(...edgeSliderValues);
        let selectedMax = Math.max(...edgeSliderValues);

        if (edgeMin === edgeMax) {
            selectedMin = edgeMin;
            selectedMax = edgeMax;
        }

        const edgeMinValue = Math.max(edgeMin, selectedMin);
        const edgeMaxValue = Math.min(edgeMax, selectedMax);

        cy.elements().forEach((ele) => ele.style("display", "none"));

        cy.edges().forEach((edge) => {
            const edgeSize = edge.data("edge_size");
            const isVisible =
                edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
            edge.style("display", isVisible ? "element" : "none");
        });

        const visibleEdges = cy.edges().filter((edge) => edge.style("display") === "element");
        const candidateElements = visibleEdges.union(visibleEdges.connectedNodes());
        const components = candidateElements.components();

        const targetGene = pageConfig.name;
        const targetNode = cy.getElementById(targetGene);

        if (targetNode.length === 0) {
            return;
        }

        targetNode.style("display", "element");

        const directlyConnectedNodes = new Set([targetGene]);

        cy.edges().forEach((edge) => {
            if (edge.style("display") === "element") {
                const source = edge.data("source");
                const target = edge.data("target");

                if (source === targetGene) {
                    directlyConnectedNodes.add(target);
                } else if (target === targetGene) {
                    directlyConnectedNodes.add(source);
                }
            }
        });

        cy.edges().forEach((edge) => {
            if (edge.style("display") === "element") {
                const source = edge.data("source");
                const target = edge.data("target");

                if (directlyConnectedNodes.has(source) && directlyConnectedNodes.has(target)) {
                    edge.style("display", "element");
                } else {
                    edge.style("display", "none");
                }
            }
        });

        cy.nodes().forEach((node) => {
            const nodeId = node.data("id");
            if (directlyConnectedNodes.has(nodeId)) {
                node.style("display", "element");
            } else {
                node.style("display", "none");
            }
        });

        layoutController.runLayoutWithRepulsion();
        checkEmptyState();

        if (window.refreshPhenotypeList) {
            window.refreshPhenotypeList();
        }

        if (typeof window.recalculateCentrality === "function") {
            window.recalculateCentrality();
        }
    };
} else {
    filterByNodeColorAndEdgeSize = function () {
        const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
        const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax, 1, 100);
        const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax, 1, 100);

        cy.nodes().forEach((node) => node.style("display", "element"));

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

        const components = calculateConnectedComponents(cy);
        const validComponents = components.filter((comp) =>
            Object.keys(comp).some((label) => {
                const node = cy.$(`node[label="${label}"]`);
                return node.data("node_color") === 1;
            }),
        );

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

        cy.nodes().forEach((node) => {
            const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
            if (visibleEdges.length === 0) {
                node.style("display", "none");
            }
        });

        layoutController.runLayoutWithRepulsion();
        checkEmptyState();

        if (window.refreshPhenotypeList) {
            window.refreshPhenotypeList();
        }

        if (typeof window.recalculateCentrality === "function") {
            window.recalculateCentrality();
        }
    };
}

if (edgeSlider && edgeSlider.noUiSlider) {
    edgeSlider.noUiSlider.on("update", function (values) {
        const formattedValues = values.map((value) => Math.round(Number(value)));
        document.getElementById("edge-size-value").textContent = formattedValues.join(" - ");
        filterByNodeColorAndEdgeSize();
    });
    edgeSlider.noUiSlider.on("set", function () {
        queueAutoArrange({ afterLayout: true, delayMs: AUTO_ARRANGE_DELAY_MS });
    });
}

if (isPhenotypePage && nodeSlider && nodeSlider.noUiSlider) {
    nodeSlider.noUiSlider.on("update", function (values) {
        const intValues = values.map((value) => Math.round(value));
        const label = document.getElementById("node-color-value");
        if (label) {
            label.textContent = intValues.join(" - ");
        }
        filterByNodeColorAndEdgeSize();
    });
    nodeSlider.noUiSlider.on("set", function () {
        queueAutoArrange({ afterLayout: true, delayMs: AUTO_ARRANGE_DELAY_MS });
    });
}

// =============================================================================
// Genotype, sex, and life-stage specific filtering
// =============================================================================

let targetPhenotype = isPhenotypePage ? pageConfig.displayName : "";

function isGenotypeAllSelected() {
    const allCheckbox = document.querySelector('#genotype-filter-form input[value="All"]');
    return allCheckbox ? allCheckbox.checked : true;
}

function applyFiltering() {
    queueAutoArrange({ afterLayout: true, delayMs: AUTO_ARRANGE_DELAY_MS });
    const sourceElements = isGenotypeAllSelected() ? baseElements : elements;
    filterElementsByGenotypeAndSex(sourceElements, cy, targetPhenotype, filterByNodeColorAndEdgeSize);
    if (typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
}

function setupAllToggle(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const checkboxes = Array.from(form.querySelectorAll('input[type="checkbox"]'));
    const allCheckbox = checkboxes.find((checkbox) => checkbox.value === "All");
    const optionCheckboxes = checkboxes.filter((checkbox) => checkbox !== allCheckbox);

    const ensureAllSelected = () => {
        if (allCheckbox) {
            allCheckbox.checked = true;
            optionCheckboxes.forEach((checkbox) => {
                checkbox.checked = false;
            });
        }
    };

    if (allCheckbox) {
        allCheckbox.addEventListener("change", () => {
            if (allCheckbox.checked) {
                optionCheckboxes.forEach((checkbox) => {
                    checkbox.checked = false;
                });
            } else if (!optionCheckboxes.some((checkbox) => checkbox.checked)) {
                ensureAllSelected();
            }
            applyFiltering();
        });
    }

    optionCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                if (allCheckbox) {
                    allCheckbox.checked = false;
                }
                if (optionCheckboxes.every((option) => option.checked)) {
                    ensureAllSelected();
                    applyFiltering();
                    return;
                }
            } else if (!optionCheckboxes.some((option) => option.checked)) {
                ensureAllSelected();
                applyFiltering();
                return;
            }
            applyFiltering();
        });
    });

    if (!optionCheckboxes.some((checkbox) => checkbox.checked)) {
        ensureAllSelected();
    }
}

["genotype-filter-form", "sex-filter-form", "lifestage-filter-form"].forEach((formId) => setupAllToggle(formId));

// =============================================================================
// Highlight human disease annotations
// =============================================================================
highlightDiseaseAnnotation({ cy });

// ############################################################################
// Cytoscape's visualization setting
// ############################################################################

setupGeneSearch({ cy });

setupPhenotypeSearch({ cy, elements });

createSlider("font-size-slider", isGeneSymbolPage ? 10 : 20, 1, 50, 1, (intValues) => {
    document.getElementById("font-size-value").textContent = intValues;
    cy.style()
        .selector("node")
        .style("font-size", intValues + "px")
        .update();
});

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

const layoutDropdown = document.getElementById("layout-dropdown");
const nodeRepulsionContainer = document.getElementById("node-repulsion-container");
const nodeRepulsionBox = document.getElementById("node-repulsion-box");

function updateNodeRepulsionVisibility() {
    const displayValue = "block";

    if (nodeRepulsionContainer) {
        nodeRepulsionContainer.style.display = displayValue;
    }

    if (nodeRepulsionBox) {
        nodeRepulsionBox.style.display = displayValue;
    }
}

updateNodeRepulsionVisibility();
layoutDropdown.addEventListener("change", updateNodeRepulsionVisibility);

createSlider("nodeRepulsion-slider", defaultNodeRepulsion, 1, 10, 1, (intValues) => {
    document.getElementById("node-repulsion-value").textContent = intValues;
    layoutController.updateRepulsionScale(intValues);
    layoutController.scheduleNodeRepulsion();
    if (layoutController.getLayout() !== "random") {
        layoutController.queueLayoutRefresh(150);
    }
});
const nodeRepulsionSlider = document.getElementById("nodeRepulsion-slider");
if (nodeRepulsionSlider && nodeRepulsionSlider.noUiSlider) {
    nodeRepulsionSlider.noUiSlider.on("set", () => {
        const needsLayoutStop = layoutController.getLayout() !== "random";
        queueAutoArrange({ afterLayout: needsLayoutStop, delayMs: AUTO_ARRANGE_DELAY_MS });
    });
}

// ############################################################################
// Initialize centrality system
// ############################################################################

initializeCentralitySystem(cy, createSlider);
window.recalculateCentrality = recalculateCentrality;

// ############################################################################
// Tooltip handling
// ############################################################################

const DIM_NODE_CLASS = "dim-node";
const DIM_EDGE_CLASS = "dim-edge";
const FOCUS_NODE_CLASS = "focus-node";
const FOCUS_EDGE_CLASS = "focus-edge";

function clearNeighborHighlights() {
    cy.nodes().removeClass(DIM_NODE_CLASS);
    cy.edges().removeClass(DIM_EDGE_CLASS);
    cy.nodes().removeClass(FOCUS_NODE_CLASS);
    cy.edges().removeClass(FOCUS_EDGE_CLASS);
}

function highlightNeighbors(target) {
    if (!target) {
        return;
    }

    clearNeighborHighlights();

    let highlightElements;

    if (target.isNode()) {
        const nodeId = target.id();
        const neighborIds = new Set([nodeId]);

        target.connectedEdges().forEach((edge) => {
            if (!edge.visible()) return;
            const srcId = edge.source().id();
            const tgtId = edge.target().id();
            if (srcId === nodeId) {
                neighborIds.add(tgtId);
            }
            if (tgtId === nodeId) {
                neighborIds.add(srcId);
            }
        });

        const highlightNodes = cy.nodes().filter((n) => n.visible() && neighborIds.has(n.id()));
        const highlightEdges = cy
            .edges()
            .filter((e) => e.visible() && (e.source().id() === nodeId || e.target().id() === nodeId));

        highlightElements = highlightNodes.union(highlightEdges);
    } else if (target.isEdge()) {
        highlightElements = target.union(target.connectedNodes()).filter((ele) => ele.visible());
    } else {
        return;
    }

    // Dim all visible elements first, then un-dim the highlight set to ensure neighbors stay emphasized
    const visibleElements = cy.elements().filter((ele) => ele.visible());
    visibleElements.nodes().addClass(DIM_NODE_CLASS);
    visibleElements.edges().addClass(DIM_EDGE_CLASS);

    // Remove dimming from the intended highlight set
    highlightElements.nodes().removeClass(DIM_NODE_CLASS);
    highlightElements.edges().removeClass(DIM_EDGE_CLASS);
    highlightElements.nodes().addClass(FOCUS_NODE_CLASS);
    highlightElements.edges().addClass(FOCUS_EDGE_CLASS);
}

cy.on("tap", "node, edge", function (event) {
    highlightNeighbors(event.target);
});

cy.on("tap", "node, edge", function (event) {
    showTooltip(event, cy, mapSymbolToId, targetPhenotype, { nodeColorValues });
});

cy.on("tap", function (event) {
    if (event.target !== cy) {
        return;
    }

    const renderedPos = event.renderedPosition || event.position || { x: 0, y: 0 };
    const component = findComponentByPosition(renderedPos);
    if (component) {
        showSubnetworkTooltip({ component, renderedPos, cyInstance: cy });
    } else {
        removeTooltips();
        clearNeighborHighlights();
    }
});

// ############################################################################
// Exporter
// ############################################################################

const fileName = `TSUMUGI_${pageConfig.name || "network"}`;

function attachExportHandler(elementId, handler) {
    const button = document.getElementById(elementId);
    if (!button) return;
    button.addEventListener("click", handler);
}

attachExportHandler("export-png", () => exportGraphAsPNG(cy, fileName));
attachExportHandler("export-jpg", () => exportGraphAsJPG(cy, fileName));
attachExportHandler("export-svg", () => exportGraphAsSVG(cy, fileName));
attachExportHandler("export-csv", () => exportGraphAsCSV(cy, fileName));
attachExportHandler("export-graphml", () => exportGraphAsGraphML(cy, fileName));

attachExportHandler("export-png-mobile", () => exportGraphAsPNG(cy, fileName));
attachExportHandler("export-jpg-mobile", () => exportGraphAsJPG(cy, fileName));
attachExportHandler("export-svg-mobile", () => exportGraphAsSVG(cy, fileName));
attachExportHandler("export-csv-mobile", () => exportGraphAsCSV(cy, fileName));
attachExportHandler("export-graphml-mobile", () => exportGraphAsGraphML(cy, fileName));

// ############################################################################
// UI Helpers
// ############################################################################

function checkEmptyState() {
    const visibleNodes = cy.nodes(":visible").length;
    const messageEl = document.getElementById("no-nodes-message");
    if (messageEl) {
        messageEl.style.display = visibleNodes === 0 ? "block" : "none";
    }
}

const recenterBtn = document.getElementById("recenter-button");
if (recenterBtn) {
    recenterBtn.addEventListener("click", () => {
        if (cy) {
            cy.fit();
            cy.center();
            scheduleSubnetworkFrameUpdate();
        }
    });
}

function autoArrangeModules() {
    if (!cy) return;
    cy.startBatch();
    tileComponents();
    resolveComponentOverlaps();
    cy.endBatch();
    fitVisibleComponents();
    scheduleSubnetworkFrameUpdate();
}

function setupInitialAutoArrange() {
    let handled = false;
    let scheduled = false;
    let hasRendered = false;

    cy.one("render", () => {
        hasRendered = true;
    });

    const triggerInitialArrange = (reason) => {
        if (handled) return;
        handled = true;
        const arrangeButton = document.getElementById("arrange-modules-button");
        if (arrangeButton) {
            arrangeButton.click();
            return;
        }
        autoArrangeModules();
    };

    const scheduleInitialArrange = (reason) => {
        if (scheduled) return;
        scheduled = true;
        setTimeout(() => {
            triggerInitialArrange(reason);
        }, INITIAL_ARRANGE_CLICK_DELAY_MS);
    };

    const triggerAfterRender = (reason) => {
        const runAfterPaint = () => {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    scheduleInitialArrange(reason);
                });
            });
        };

        if (hasRendered) {
            runAfterPaint();
            return;
        }

        cy.one("render", runAfterPaint);
    };

    const timeoutId = setTimeout(() => {
        triggerAfterRender("timeout");
    }, INITIAL_AUTO_ARRANGE_TIMEOUT_MS);

    cy.one("layoutstop", () => {
        clearTimeout(timeoutId);
        triggerAfterRender("layoutstop");
    });

    window.addEventListener(
        REPULSION_FINISH_EVENT,
        () => {
            clearTimeout(timeoutId);
            triggerAfterRender("repulsion");
        },
        { once: true },
    );
}

function queueAutoArrange({ afterLayout = false, delayMs = AUTO_ARRANGE_DELAY_MS } = {}) {
    if (!cy) return;
    let arranged = false;
    const runAutoArrange = () => {
        if (arranged) return;
        arranged = true;
        autoArrangeModules();
    };
    const scheduleRun = () => {
        setTimeout(runAutoArrange, delayMs);
    };
    if (!afterLayout) {
        scheduleRun();
        return;
    }
    let repulsionFallbackId = null;
    const onRepulsionFinish = (event) => {
        if (repulsionFallbackId) {
            clearTimeout(repulsionFallbackId);
            repulsionFallbackId = null;
        }
        scheduleRun();
    };
    const scheduleAfterRepulsion = () => {
        window.addEventListener(REPULSION_FINISH_EVENT, onRepulsionFinish, { once: true });
        repulsionFallbackId = setTimeout(() => {
            window.removeEventListener(REPULSION_FINISH_EVENT, onRepulsionFinish);
            scheduleRun();
        }, AUTO_ARRANGE_REPULSION_TIMEOUT_MS);
    };
    const layoutFallbackId = setTimeout(() => {
        scheduleRun();
    }, AUTO_ARRANGE_LAYOUT_TIMEOUT_MS);
    cy.one("layoutstop", () => {
        if (arranged) return;
        clearTimeout(layoutFallbackId);
        scheduleAfterRepulsion();
    });
}

const arrangeModulesButton = document.getElementById("arrange-modules-button");
if (arrangeModulesButton) {
    arrangeModulesButton.addEventListener("click", autoArrangeModules);
}

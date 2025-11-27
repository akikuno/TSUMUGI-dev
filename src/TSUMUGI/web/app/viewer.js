import { exportGraphAsPNG, exportGraphAsJPG, exportGraphAsCSV, exportGraphAsGraphML } from "./js/exporter.js";
import { scaleToOriginalRange, getColorForValue } from "./js/value_scaler.js";
import { removeTooltips, showSubnetworkTooltip, showTooltip } from "./js/tooltips.js";
import { getOrderedComponents, calculateConnectedComponents } from "./js/components.js";
import { createSlider } from "./js/slider.js";
import { filterElementsByGenotypeAndSex } from "./js/filters.js";
import { loadJSONGz, loadJSON } from "./js/data_loader.js";
import { setupGeneSearch } from "./js/gene_searcher.js";
import { highlightDiseaseAnnotation } from "./js/highlighter.js";
import { setupPhenotypeSearch } from "./js/phenotype_searcher.js";
import { initializeCentralitySystem, recalculateCentrality } from "./js/centrality.js";

const NODE_SLIDER_MIN = 1;
const NODE_SLIDER_MAX = 100;
const EDGE_SLIDER_MIN = 1;
const EDGE_SLIDER_MAX = 100;

function getPageConfig() {
    const params = new URLSearchParams(window.location.search);
    const modeParam = params.get("mode");
    const mode = ["phenotype", "genesymbol", "genelist"].includes(modeParam || "") ? modeParam : "phenotype";
    const providedName = params.get("name") || "";
    const name = mode === "genelist" && !providedName ? "geneList" : providedName;
    const title = params.get("title") || name;

    return {
        mode,
        name,
        displayName: title || name || "TSUMUGI",
    };
}

function hidePhenotypeOnlySections(isPhenotypePage) {
    document.querySelectorAll(".phenotype-only").forEach((el) => {
        el.style.display = isPhenotypePage ? "" : "none";
    });
}

function setPageTitle(config, mapSymbolToId) {
    const pageTitleLink = document.getElementById("page-title-link");
    const pageTitle = config.displayName || config.name || "TSUMUGI";
    let targetUrl = "";

    if (config.mode === "genesymbol" && mapSymbolToId) {
        const accession = mapSymbolToId[config.name];
        if (accession) {
            targetUrl = `https://www.mousephenotype.org/data/genes/${accession}`;
        }
    }

    if (targetUrl) {
        pageTitleLink.href = targetUrl;
        pageTitleLink.target = "_blank";
        pageTitleLink.rel = "noreferrer";
    } else {
        pageTitleLink.removeAttribute("href");
        pageTitleLink.style.pointerEvents = "none";
        pageTitleLink.style.cursor = "default";
    }

    pageTitleLink.textContent = pageTitle;
    document.title = `${pageTitle} | TSUMUGI`;
}

function setVersionLabel() {
    const versionLabel = document.getElementById("tsumugi-version");
    if (!versionLabel) return;

    fetch("../version.txt")
        .then((res) => (res.ok ? res.text() : ""))
        .then((text) => {
            versionLabel.textContent = text.trim() || "-";
        })
        .catch(() => {
            versionLabel.textContent = "-";
        });
}

function loadElementsForConfig(config) {
    if (config.mode === "phenotype") {
        return loadJSONGz(`../data/phenotype/${config.name}.json.gz`) || [];
    }

    if (config.mode === "genesymbol") {
        return loadJSONGz(`../data/genesymbol/${config.name}.json.gz`) || [];
    }

    // Gene list page pulls data from localStorage
    try {
        const stored = localStorage.getItem("elements");
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error("Failed to parse stored elements for gene list:", error);
        return [];
    }
}

function renderEmptyState(message) {
    const container = document.querySelector(".cy");
    if (!container) return;

    container.innerHTML = `<div style="padding: 24px; font-size: 16px;">${message}</div>`;
}

function applyNodeMinMax(elements, nodeColorMin, nodeColorMax) {
    // Ensure at least one gene pair remains visible even at slider extremes. Issue #72
    const nodeColorMap = new Map();
    elements.forEach((ele) => {
        if (ele.data.node_color !== undefined && ele.data.id !== undefined) {
            nodeColorMap.set(ele.data.id, ele.data.node_color);
        }
    });

    const sortedNodeColors = [...new Set([...nodeColorMap.values()])].sort((a, b) => a - b);
    if (sortedNodeColors.length === 0) {
        return { nodeMin: nodeColorMin, nodeMax: nodeColorMax };
    }

    const nodeColorToRank = new Map();
    sortedNodeColors.forEach((val, idx) => {
        nodeColorToRank.set(val, idx + 1);
    });

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

    if (edgeRankPairs.length === 0) {
        return { nodeMin: nodeColorMin, nodeMax: nodeColorMax };
    }

    const minRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum < b.rankSum ? a : b));
    const maxRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum > b.rankSum ? a : b));

    const nodeMin = minRankEdge.maxVal;
    const nodeMax = maxRankEdge.minVal;

    elements.forEach((ele) => {
        if (ele.data.node_color !== undefined) {
            ele.data.original_node_color = ele.data.node_color;

            if (ele.data.node_color <= nodeMin) {
                ele.data.node_color_for_filter = nodeMin;
            } else if (ele.data.node_color >= nodeMax) {
                ele.data.node_color_for_filter = nodeMax;
            } else {
                ele.data.node_color_for_filter = ele.data.node_color;
            }
        }
    });

    return { nodeMin, nodeMax };
}

// Track which search mode is active in this viewer
const pageConfig = getPageConfig();
const isPhenotypePage = pageConfig.mode === "phenotype";
const isGeneSymbolPage = pageConfig.mode === "genesymbol";

hidePhenotypeOnlySections(isPhenotypePage);
setVersionLabel();

const map_symbol_to_id = loadJSON("../data/marker_symbol_accession_id.json") || {};
setPageTitle(pageConfig, map_symbol_to_id);

const elements = loadElementsForConfig(pageConfig);
if (!elements || elements.length === 0) {
    renderEmptyState("No data found. Please check your input.");
    throw new Error("No elements available to render");
}

// ############################################################################
// Input handler
// ############################################################################

const nodeSizes = elements.filter((ele) => ele.data.node_color !== undefined).map((ele) => ele.data.node_color);
const nodeColorMin = nodeSizes.length ? Math.min(...nodeSizes) : 0;
const nodeColorMax = nodeSizes.length ? Math.max(...nodeSizes) : 1;

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

const defaultNodeRepulsion = isGeneSymbolPage ? 8 : 5;

let nodeRepulsionValue = scaleToOriginalRange(defaultNodeRepulsion, nodeRepulsionMin, nodeRepulsionMax);
let componentSpacingValue = scaleToOriginalRange(defaultNodeRepulsion, componentSpacingMin, componentSpacingMax);

function getLayoutOptions() {
    const baseOptions = {
        name: currentLayout,
        nodeRepulsion: nodeRepulsionValue,
        componentSpacing: componentSpacingValue,
    };

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
    layout: getLayoutOptions(),
});

window.cy = cy;

function handleMobileResize() {
    if (cy) {
        setTimeout(() => {
            cy.resize();
            cy.fit();
            cy.center();
        }, 300);
    }
}

setTimeout(() => {
    if (window.innerWidth <= 600) {
        cy.resize();
        cy.fit();
        cy.center();
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
if (isPhenotypePage && nodeSlider) {
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

        cy.layout(getLayoutOptions()).run();

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

        cy.layout(getLayoutOptions()).run();

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

        cy.layout(getLayoutOptions()).run();

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
}

// =============================================================================
// Genotype, sex, and life-stage specific filtering
// =============================================================================

let target_phenotype = isPhenotypePage ? pageConfig.displayName : "";

function applyFiltering() {
    filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterByNodeColorAndEdgeSize);
    if (typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
}

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

initializeCentralitySystem(cy, createSlider);
window.recalculateCentrality = recalculateCentrality;

// ############################################################################
// Tooltip handling
// ############################################################################

cy.on("tap", "node, edge", function (event) {
    showTooltip(event, cy, map_symbol_to_id, target_phenotype, nodeColorMin, nodeColorMax, edgeMin, edgeMax, nodeSizes);
});

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

const file_name = `TSUMUGI_${pageConfig.name || "network"}`;

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

const exportCsvButton = document.getElementById("export-csv");
if (exportCsvButton) {
    exportCsvButton.addEventListener("click", function () {
        exportGraphAsCSV(cy, file_name);
    });
}

const exportGraphmlButton = document.getElementById("export-graphml");
if (exportGraphmlButton) {
    exportGraphmlButton.addEventListener("click", function () {
        exportGraphAsGraphML(cy, file_name);
    });
}

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

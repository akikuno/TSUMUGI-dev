import { exportGraphAsPNG, exportGraphAsJPG, exportGraphAsCSV, exportGraphAsGraphML, exportGraphAsSVG } from "./js/export/graphExporter.js?v=20260613-safe-export";
import { scaleToOriginalRange, getColorForValue } from "./js/graph/valueScaler.js";
import { initInfoTooltips, removeTooltips, showSubnetworkTooltip, showTooltip } from "./js/ui/tooltips.js";
import { getOrderedComponents, calculateConnectedComponents } from "./js/graph/components.js";
import { createSlider } from "./js/ui/slider.js";
import { filterElementsByGenotypeAndSex } from "./js/graph/filters.js";
import { loadJSON, loadJSONGz } from "./js/data/dataLoader.js";
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
const MODULE_MODE_SIMILARITY = "similarity";
const MODULE_MODE_TOP_LEVEL_MP = "top-level-mp";
const MODULE_BASE_VISIBLE_SCRATCH = "moduleBaseVisible";
const TOP_LEVEL_MODULE_DATA_KEY = "top_level_module_memberships";
const MODULE_GROUP_NODE_SPACING = 110;
const MODULE_GROUP_COMPACT_SPAN = 420;
const TOP_LEVEL_MODULE_TILE_PADDING = 96;
const SUBNETWORK_LABEL_HEIGHT = 26;
const EXPORT_FRAME_PADDING = 20;
const EXPORT_FRAME_LABEL_OFFSET = 18;
const MODULE_DIM_NODE_CLASS = "module-dim-node";
const MODULE_DIM_EDGE_CLASS = "module-dim-edge";
const MODULE_FOCUS_NODE_CLASS = "module-focus-node";
const MODULE_FOCUS_EDGE_CLASS = "module-focus-edge";
const TARGET_GENE_NODE_CLASS = "target-gene-node";
const TARGET_GENE_NODE_SIZE = 56;
const GENE_SYMBOL_FONT_SIZE = 16;

// Initialize UI helpers that only depend on DOM availability.
initInfoTooltips();
initDynamicFontSize();
initMobilePanel();

// Track which search mode is active in this viewer
const pageConfig = getPageConfig();
const isPhenotypePage = pageConfig.mode === "phenotype";
const isGeneSymbolPage = pageConfig.mode === "genesymbol";
const isGeneListPage = pageConfig.mode === "genelist";
const DEFAULT_FONT_SIZE = isGeneSymbolPage ? GENE_SYMBOL_FONT_SIZE : 20;
const DEFAULT_LINE_WIDTH = isGeneSymbolPage ? 1 : 5;

let subnetworkOverlay = null;

function updateNoNodesMessage(shouldShow) {
    const messageEl = document.getElementById("no-nodes-message");
    if (!messageEl) return;

    if (messageEl.textContent !== "No Gene Network Found") {
        messageEl.textContent = "No Gene Network Found";
    }

    messageEl.style.display = shouldShow ? "block" : "none";

    if (!subnetworkOverlay) {
        subnetworkOverlay = document.querySelector(".subnetwork-overlay");
    }

    if (subnetworkOverlay) {
        subnetworkOverlay.style.display = shouldShow ? "none" : "";
    }
}

setVersionLabel();

const mapSymbolToId = loadJSON("../data/marker_symbol_accession_id.json") || {};
const mapPhenotypeToId = loadJSON("../data/mp_term_id_lookup.json") || {};
const mapPhenotypeToTopLevelModules = loadJSON("../data/mp_top_level_module_lookup.json") || {};
setPageTitle(pageConfig, mapSymbolToId, mapPhenotypeToId);

let elements;
try {
    elements = await loadElementsForConfig(pageConfig);
} catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load network data.";
    console.error("Failed to construct network:", error);
    if (isGeneSymbolPage || isGeneListPage) {
        updateNoNodesMessage(true);
    }
    renderEmptyState(message);
    throw error;
}
if (!elements || elements.length === 0) {
    if (isGeneSymbolPage) {
        updateNoNodesMessage(true);
    }
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
const genePhenotypeModules = loadGenePhenotypeModules(pageConfig);
const genePhenotypeModuleState = createGenePhenotypeModuleState(genePhenotypeModules);
const nonGeneModuleState = {
    similarityComponents: new Map(),
    topLevelModules: new Map(),
};
let syncedGenePhenotypeModuleId = null;

function mapEdgeSizeToWidth(edgeSize) {
    if (edgeMax === edgeMin) {
        return 1.5;
    }
    const normalized = (edgeSize - edgeMin) / (edgeMax - edgeMin);
    return 0.5 + normalized * 1.5;
}

function loadGenePhenotypeModules(config) {
    if (config.mode !== "genesymbol" || !config.name) {
        return null;
    }
    return loadJSONGz(`../data/genesymbol_modules/${config.name}.json.gz`);
}

function createGenePhenotypeModuleState(data) {
    if (!data || !Array.isArray(data.modules)) {
        return {
            modules: [],
            modulesById: new Map(),
            edgeMemberships: new Map(),
            nodeMemberships: new Map(),
        };
    }

    const modulesById = new Map(data.modules.map((module) => [module.id, module]));
    const edgeMemberships = new Map();
    Object.entries(data.edges || {}).forEach(([key, value]) => {
        const modules = new Map();
        (value.modules || []).forEach((module) => {
            modules.set(module.id, module);
        });
        edgeMemberships.set(key, modules);
    });

    const nodeMemberships = new Map();
    Object.entries(data.nodes || {}).forEach(([nodeId, value]) => {
        const modules = new Map();
        (value.modules || []).forEach((module) => {
            modules.set(module.id, module);
        });
        nodeMemberships.set(nodeId, modules);
    });

    return {
        modules: data.modules,
        modulesById,
        edgeMemberships,
        nodeMemberships,
    };
}

function isNonGeneModulePage() {
    return isPhenotypePage || isGeneListPage;
}

function normalizePhenotypes(value) {
    if (Array.isArray(value)) return value.filter(Boolean);
    return value ? [value] : [];
}

function getPhenotypeTermName(annotation) {
    const text = String(annotation || "");
    const suffixIndex = text.lastIndexOf(" (");
    return suffixIndex >= 0 ? text.slice(0, suffixIndex) : text;
}

function buildTopLevelModuleMemberships(phenotypes) {
    const counts = new Map();

    normalizePhenotypes(phenotypes).forEach((annotation) => {
        const modules = mapPhenotypeToTopLevelModules[getPhenotypeTermName(annotation)] || [];
        modules.forEach((module) => {
            if (!module || !module.id || !module.label) return;
            if (!counts.has(module.id)) {
                counts.set(module.id, {
                    id: module.id,
                    label: module.label,
                    support_count: 0,
                });
            }
            counts.get(module.id).support_count += 1;
        });
    });

    return buildTopLevelModuleMembershipsFromCounts([...counts.values()]);
}

function buildTopLevelModuleMembershipsFromCounts(counts) {
    const total = counts.reduce((sum, module) => sum + module.support_count, 0);
    if (total === 0) return [];
    return counts
        .map((module) => ({
            ...module,
            weight: Number((module.support_count / total).toFixed(6)),
        }))
        .sort((a, b) => {
            if (b.weight !== a.weight) return b.weight - a.weight;
            if (b.support_count !== a.support_count) return b.support_count - a.support_count;
            return a.label.localeCompare(b.label);
        });
}

function clearPublicModuleData(ele) {
    ele.removeData("module_memberships primary_module primary_module_label");
}

function elementHasTopLevelModule(ele, moduleId) {
    if (!moduleId) return true;
    return (ele.data(TOP_LEVEL_MODULE_DATA_KEY) || []).some((module) => module.id === moduleId);
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
                "font-size": DEFAULT_FONT_SIZE + "px",
                width: 15,
                height: 15,
                "background-color": function (ele) {
                    if (ele.data("effect_size_missing")) {
                        return "#ffffff";
                    }
                    const originalColor = ele.data("original_node_color") || ele.data("node_color");
                    return getColorForValue(originalColor, nodeColorMin, nodeColorMax);
                },
                "border-width": function (ele) {
                    return ele.data("effect_size_missing") ? 1.5 : 0;
                },
                "border-color": "#666666",
            },
        },
        {
            selector: "edge",
            style: {
                "curve-style": isGeneSymbolPage ? "haystack" : "bezier",
                "haystack-radius": 0,
                "text-rotation": "autorotate",
                width: function (ele) {
                    return mapEdgeSizeToWidth(ele.data("edge_size"));
                },
            },
        },
        {
            selector: `node.${MODULE_DIM_NODE_CLASS}`,
            style: {
                opacity: 0.12,
            },
        },
        {
            selector: `edge.${MODULE_DIM_EDGE_CLASS}`,
            style: {
                opacity: 0.08,
            },
        },
        {
            selector: `node.${MODULE_FOCUS_NODE_CLASS}`,
            style: {
                opacity: 1,
                "border-width": 4,
                "border-color": "#2f7ed8",
            },
        },
        {
            selector: `edge.${MODULE_FOCUS_EDGE_CLASS}`,
            style: {
                opacity: 0.95,
                "line-color": "#2f7ed8",
                "target-arrow-color": "#2f7ed8",
                "source-arrow-color": "#2f7ed8",
            },
        },
        {
            selector: `node.${TARGET_GENE_NODE_CLASS}`,
            style: {
                width: TARGET_GENE_NODE_SIZE,
                height: TARGET_GENE_NODE_SIZE,
                "font-size": GENE_SYMBOL_FONT_SIZE + "px",
                "font-weight": "bold",
                "background-color": "#ff8c00",
                "border-width": 3,
                "border-color": "#b85a00",
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
        {
            selector: ".export-module-frame-box",
            style: {
                shape: "rectangle",
                width: (ele) => ele.data("width") || 1,
                height: (ele) => ele.data("height") || 1,
                "background-opacity": 0,
                "border-width": 2,
                "border-color": "#888888",
                "border-opacity": 0.9,
                "border-style": "dashed",
                label: "",
            },
        },
        {
            selector: ".export-module-frame-label",
            style: {
                label: "data(label)",
                width: 1,
                height: 1,
                "background-opacity": 0,
                color: "#ffffff",
                "font-size": "12px",
                "font-weight": "bold",
                "text-background-color": "#333333",
                "text-background-opacity": 0.85,
                "text-background-padding": 5,
                "text-valign": "center",
                "text-halign": "center",
            },
        },
    ],
    layout: layoutController.getLayoutOptions(),
    userZoomingEnabled: true,
    zoomingEnabled: true,
    textureOnViewport: isGeneSymbolPage,
    hideEdgesOnViewport: isGeneSymbolPage,
    hideLabelsOnViewport: isGeneSymbolPage,
    pixelRatio: isGeneSymbolPage ? 1 : "auto",
    wheelSensitivity: 0.2,
});

window.cy = cy;
layoutController.attachCy(cy);
layoutController.registerInitialLayoutStop();
if (isGeneSymbolPage && pageConfig.name) {
    cy.getElementById(pageConfig.name).addClass(TARGET_GENE_NODE_CLASS);
}
initializeTopLevelModuleData();
setupInitialAutoArrange();
cy.one("render", () => {
    checkEmptyState();
});

function getEdgeModuleKey(edge) {
    const source = edge.data("source");
    const target = edge.data("target");
    return [source, target].sort((a, b) => a.localeCompare(b)).join("||");
}

function getSelectedPhenotypeModuleId() {
    const dropdown = document.getElementById("phenotype-module-dropdown");
    return dropdown ? dropdown.value : "";
}

function normalizeModuleMembership(module) {
    if (!module) return null;
    const weight = Number(module.weight);
    const supportCount = Number(module.support_count ?? module.count) || 0;
    const label = module.label || module.name;
    if (!module.id || !label) return null;
    return {
        id: module.id,
        name: module.name || label,
        label,
        support_count: supportCount,
        weight: Number.isFinite(weight) ? weight : 0,
    };
}

function getVisibleModuleMemberships(membershipMap, moduleId = "") {
    if (!membershipMap) return [];
    return [...membershipMap.values()]
        .filter((module) => !moduleId || module.id === moduleId)
        .map((module) => normalizeModuleMembership(module))
        .filter(Boolean)
        .sort((a, b) => {
            if (b.weight !== a.weight) return b.weight - a.weight;
            if (b.support_count !== a.support_count) return b.support_count - a.support_count;
            return a.label.localeCompare(b.label);
        });
}

function setModuleMembershipData(ele, memberships) {
    ele.removeData("module_memberships primary_module primary_module_label");
    if (!memberships || memberships.length === 0) return;
    const primary = memberships[0];
    ele.data("module_memberships", memberships);
    ele.data("primary_module", primary.id);
    ele.data("primary_module_label", primary.label);
}

function syncGenePhenotypeModuleTooltipData(moduleId = "") {
    if (syncedGenePhenotypeModuleId === moduleId) {
        return;
    }

    cy.edges().forEach((edge) => {
        const memberships = genePhenotypeModuleState.edgeMemberships.get(getEdgeModuleKey(edge));
        setModuleMembershipData(edge, getVisibleModuleMemberships(memberships, moduleId));
    });

    cy.nodes().forEach((node) => {
        const memberships = genePhenotypeModuleState.nodeMemberships.get(node.id());
        setModuleMembershipData(node, getVisibleModuleMemberships(memberships, moduleId));
    });

    syncedGenePhenotypeModuleId = moduleId;
}

function clearPhenotypeModuleOverlay() {
    cy.nodes().removeClass(MODULE_DIM_NODE_CLASS);
    cy.nodes().removeClass(MODULE_FOCUS_NODE_CLASS);
    cy.edges().removeClass(MODULE_DIM_EDGE_CLASS);
    cy.edges().removeClass(MODULE_FOCUS_EDGE_CLASS);
}

function initializeTopLevelModuleData() {
    const nodeCounts = new Map();

    cy.edges().forEach((edge) => {
        const memberships = buildTopLevelModuleMemberships(edge.data("phenotype"));
        edge.data(TOP_LEVEL_MODULE_DATA_KEY, memberships);
        if (memberships.length === 0) return;

        [edge.data("source"), edge.data("target")].forEach((nodeId) => {
            if (!nodeId) return;
            if (!nodeCounts.has(nodeId)) {
                nodeCounts.set(nodeId, new Map());
            }
            const moduleMap = nodeCounts.get(nodeId);
            memberships.forEach((module) => {
                if (!moduleMap.has(module.id)) {
                    moduleMap.set(module.id, {
                        id: module.id,
                        label: module.label,
                        support_count: 0,
                    });
                }
                moduleMap.get(module.id).support_count += module.support_count;
            });
        });
    });

    cy.nodes().forEach((node) => {
        const moduleMap = nodeCounts.get(node.id()) || new Map();
        node.data(TOP_LEVEL_MODULE_DATA_KEY, buildTopLevelModuleMembershipsFromCounts([...moduleMap.values()]));
    });
}

function restoreElementStateAfterReset() {
    if (isGeneSymbolPage && pageConfig.name) {
        cy.getElementById(pageConfig.name).addClass(TARGET_GENE_NODE_CLASS);
        syncedGenePhenotypeModuleId = null;
    }
    initializeTopLevelModuleData();
}

function isTopLevelModuleModeActive() {
    if (isGeneSymbolPage) {
        return genePhenotypeModuleState.modules.length > 0;
    }
    return isNonGeneModulePage() && getSelectedModuleMode() === MODULE_MODE_TOP_LEVEL_MP;
}

function getSelectedModuleMode() {
    const selected = document.querySelector('input[name="phenotype-module-mode"]:checked');
    return selected ? selected.value : MODULE_MODE_SIMILARITY;
}

function getEdgeModuleWeight(edge, moduleId) {
    const memberships = genePhenotypeModuleState.edgeMemberships.get(getEdgeModuleKey(edge));
    const module = memberships ? memberships.get(moduleId) : null;
    return module ? Number(module.weight) || 0 : 0;
}

function getNodeModuleWeight(node, moduleId) {
    const memberships = genePhenotypeModuleState.nodeMemberships.get(node.id());
    const module = memberships ? memberships.get(moduleId) : null;
    return module ? Number(module.weight) || 0 : 0;
}

function applyPhenotypeModuleOverlay() {
    if (!isGeneSymbolPage || genePhenotypeModuleState.modules.length === 0) {
        return;
    }

    const moduleId = getSelectedPhenotypeModuleId();
    const focusedNodeIds = new Set();

    cy.batch(() => {
        clearPhenotypeModuleOverlay();
        syncGenePhenotypeModuleTooltipData(moduleId);

        if (!moduleId) {
            return;
        }

        cy.edges().forEach((edge) => {
            if (!edge.visible()) {
                return;
            }
            const weight = getEdgeModuleWeight(edge, moduleId);
            if (weight > 0) {
                edge.addClass(MODULE_FOCUS_EDGE_CLASS);
                focusedNodeIds.add(edge.source().id());
                focusedNodeIds.add(edge.target().id());
            } else {
                edge.addClass(MODULE_DIM_EDGE_CLASS);
            }
        });

        cy.nodes().forEach((node) => {
            if (!node.visible()) {
                return;
            }
            const weight = getNodeModuleWeight(node, moduleId);
            if (weight > 0 || focusedNodeIds.has(node.id())) {
                node.addClass(MODULE_FOCUS_NODE_CLASS);
            } else {
                node.addClass(MODULE_DIM_NODE_CLASS);
            }
        });
    });
}

function setBaseVisibilityScratch(ele, isVisible) {
    ele.scratch(MODULE_BASE_VISIBLE_SCRATCH, Boolean(isVisible));
}

function isBaseVisible(ele) {
    const value = ele.scratch(MODULE_BASE_VISIBLE_SCRATCH);
    return value === undefined ? ele.visible() : value === true;
}

function getBaseVisibleElements() {
    return cy.elements().filter((ele) => isBaseVisible(ele));
}

function buildSimilarityModuleOptions() {
    const components = getBaseVisibleElements()
        .components()
        .filter((component) => component.nodes().length > 0)
        .sort((a, b) => {
            const labelA = a.nodes()[0]?.data("label") || a.nodes()[0]?.id() || "";
            const labelB = b.nodes()[0]?.data("label") || b.nodes()[0]?.id() || "";
            return labelA.localeCompare(labelB);
        });

    nonGeneModuleState.similarityComponents = new Map();
    return components.map((component, index) => {
        const id = `component:${index + 1}`;
        nonGeneModuleState.similarityComponents.set(id, component);
        return {
            id,
            label: `Module ${index + 1}`,
            count: component.nodes().length,
        };
    });
}

function buildTopLevelModuleOptions() {
    const moduleMap = new Map();

    cy.edges().forEach((edge) => {
        if (!isBaseVisible(edge)) return;
        (edge.data(TOP_LEVEL_MODULE_DATA_KEY) || []).forEach((module) => {
            if (!moduleMap.has(module.id)) {
                moduleMap.set(module.id, {
                    id: module.id,
                    label: module.label,
                    supportCount: 0,
                    edgeCount: 0,
                    genes: new Set(),
                });
            }
            const entry = moduleMap.get(module.id);
            entry.supportCount += module.support_count || 0;
            entry.edgeCount += 1;
            entry.genes.add(edge.data("source"));
            entry.genes.add(edge.data("target"));
        });
    });

    const modules = [...moduleMap.values()].sort((a, b) => {
        if (b.supportCount !== a.supportCount) return b.supportCount - a.supportCount;
        if (b.edgeCount !== a.edgeCount) return b.edgeCount - a.edgeCount;
        return a.label.localeCompare(b.label);
    });
    nonGeneModuleState.topLevelModules = new Map(modules.map((module) => [module.id, module]));
    return modules.map((module) => ({
        id: module.id,
        label: module.label,
        count: module.edgeCount,
    }));
}

function refreshPhenotypeModuleOptions() {
    const container = document.getElementById("phenotype-module-controls");
    const dropdown = document.getElementById("phenotype-module-dropdown");
    if (!container || !dropdown) return;

    if (isGeneSymbolPage) {
        if (genePhenotypeModuleState.modules.length === 0) {
            container.style.display = "none";
            return;
        }
        container.style.display = "";
        const previousValue = dropdown.value;
        dropdown.innerHTML = "";

        const allOption = document.createElement("option");
        allOption.value = "";
        allOption.textContent = "All top-level MP modules";
        dropdown.appendChild(allOption);

        genePhenotypeModuleState.modules.forEach((module) => {
            const option = document.createElement("option");
            option.value = module.id;
            option.textContent = `${module.name || module.label} (${module.target_edge_count})`;
            dropdown.appendChild(option);
        });

        dropdown.value = [...dropdown.options].some((option) => option.value === previousValue) ? previousValue : "";
        return;
    }

    if (!isNonGeneModulePage()) {
        container.style.display = "none";
        return;
    }

    container.style.display = "";
    const previousValue = dropdown.value;
    const mode = getSelectedModuleMode();
    const options = mode === MODULE_MODE_TOP_LEVEL_MP ? buildTopLevelModuleOptions() : buildSimilarityModuleOptions();

    dropdown.innerHTML = "";

    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = mode === MODULE_MODE_TOP_LEVEL_MP ? "All top-level MP modules" : "All similarity modules";
    dropdown.appendChild(allOption);

    options.forEach((module) => {
        const option = document.createElement("option");
        option.value = module.id;
        option.textContent = `${module.label} (${module.count})`;
        dropdown.appendChild(option);
    });

    dropdown.value = [...dropdown.options].some((option) => option.value === previousValue) ? previousValue : "";
}

function setupPhenotypeModuleControls() {
    const container = document.getElementById("phenotype-module-controls");
    const dropdown = document.getElementById("phenotype-module-dropdown");
    const modeToggle = document.getElementById("phenotype-module-mode-toggle");
    if (!container || !dropdown) return;

    if (modeToggle) {
        const showModeToggle = isNonGeneModulePage();
        modeToggle.hidden = !showModeToggle;
        modeToggle.style.display = showModeToggle ? "" : "none";
    }

    refreshPhenotypeModuleOptions();
    applyPhenotypeModuleOverlay();

    dropdown.addEventListener("change", () => {
        if (isGeneSymbolPage) {
            invalidateSubnetworkSummaryCache();
            applyPhenotypeModuleOverlay();
            queueAutoArrange({ afterLayout: false, delayMs: AUTO_ARRANGE_DELAY_MS });
            return;
        }
        filterByNodeColorAndEdgeSize({ runLayout: false, refreshCentrality: true });
        queueAutoArrange({ afterLayout: false, delayMs: AUTO_ARRANGE_DELAY_MS });
    });

    document.querySelectorAll('input[name="phenotype-module-mode"]').forEach((input) => {
        input.addEventListener("change", () => {
            dropdown.value = "";
            refreshPhenotypeModuleOptions();
            const shouldRunSelectedLayout = !isTopLevelModuleModeActive();
            filterByNodeColorAndEdgeSize({ runLayout: shouldRunSelectedLayout, refreshCentrality: true });
            queueAutoArrange({ afterLayout: shouldRunSelectedLayout, delayMs: AUTO_ARRANGE_DELAY_MS });
        });
    });
}

function refreshVisibleTopLevelModuleData() {
    if (!isTopLevelModuleModeActive()) {
        cy.elements().forEach((ele) => clearPublicModuleData(ele));
        return;
    }

    const nodeCounts = new Map();
    cy.edges().forEach((edge) => {
        if (!edge.visible()) {
            clearPublicModuleData(edge);
            return;
        }
        const memberships = edge.data(TOP_LEVEL_MODULE_DATA_KEY) || [];
        setModuleMembershipData(edge, memberships);
        memberships.forEach((module) => {
            [edge.data("source"), edge.data("target")].forEach((nodeId) => {
                if (!nodeCounts.has(nodeId)) {
                    nodeCounts.set(nodeId, new Map());
                }
                const moduleMap = nodeCounts.get(nodeId);
                if (!moduleMap.has(module.id)) {
                    moduleMap.set(module.id, {
                        id: module.id,
                        label: module.label,
                        support_count: 0,
                    });
                }
                moduleMap.get(module.id).support_count += module.support_count || 0;
            });
        });
    });

    cy.nodes().forEach((node) => {
        if (!node.visible()) {
            clearPublicModuleData(node);
            return;
        }
        const counts = [...(nodeCounts.get(node.id()) || new Map()).values()];
        setModuleMembershipData(node, buildTopLevelModuleMembershipsFromCounts(counts));
    });
}

function applyNonGeneModuleFilter() {
    if (!isNonGeneModulePage()) return;

    refreshPhenotypeModuleOptions();
    const dropdown = document.getElementById("phenotype-module-dropdown");
    const selectedModuleId = dropdown ? dropdown.value : "";
    const mode = getSelectedModuleMode();
    const visibleNodeIds = new Set();
    const visibleEdgeIds = new Set();

    if (!selectedModuleId) {
        cy.batch(() => {
            cy.nodes().forEach((node) => node.style("display", isBaseVisible(node) ? "element" : "none"));
            cy.edges().forEach((edge) => edge.style("display", isBaseVisible(edge) ? "element" : "none"));
        });
        refreshVisibleTopLevelModuleData();
        return;
    }

    if (mode === MODULE_MODE_SIMILARITY) {
        const component = nonGeneModuleState.similarityComponents.get(selectedModuleId);
        if (component) {
            component.nodes().forEach((node) => visibleNodeIds.add(node.id()));
            component.edges().forEach((edge) => visibleEdgeIds.add(edge));
        }
    } else {
        cy.edges().forEach((edge) => {
            if (!isBaseVisible(edge) || !elementHasTopLevelModule(edge, selectedModuleId)) return;
            visibleEdgeIds.add(edge);
            visibleNodeIds.add(edge.data("source"));
            visibleNodeIds.add(edge.data("target"));
        });
    }

    cy.batch(() => {
        cy.nodes().forEach((node) => {
            node.style("display", visibleNodeIds.has(node.id()) ? "element" : "none");
        });
        cy.edges().forEach((edge) => {
            edge.style("display", visibleEdgeIds.has(edge) ? "element" : "none");
        });
    });
    refreshVisibleTopLevelModuleData();
}

setupPhenotypeModuleControls();

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

subnetworkOverlay = createSubnetworkOverlay();
let subnetworkMeta = [];
let isFrameUpdateQueued = false;
let subnetworkDragState = null;
let subnetworkSummaryVersion = 0;
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
            normalizePhenotypes(edge.data("phenotype")).forEach((name) => {
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

function invalidateSubnetworkSummaryCache() {
    subnetworkSummaryVersion += 1;
}

function ensureSubnetworkPhenotypeSummary(componentMeta) {
    if (!componentMeta) return;
    if (!componentMeta.component) return;
    if (componentMeta.phenotypeSummaryVersion === subnetworkSummaryVersion && componentMeta.phenotypes) return;
    componentMeta.phenotypes = summarizeEdgePhenotypes(componentMeta.component);
    componentMeta.phenotypeSummaryVersion = subnetworkSummaryVersion;
}

function summarizeTopLevelModulePhenotypes(moduleId, nodes) {
    const nodeIds = new Set(nodes.map((node) => node.id()));
    const counts = new Map();

    cy.edges(":visible").forEach((edge) => {
        if (!elementHasTopLevelModule(edge, moduleId)) return;
        if (!nodeIds.has(edge.data("source")) && !nodeIds.has(edge.data("target"))) return;
        normalizePhenotypes(edge.data("phenotype")).forEach((name) => {
            counts.set(name, (counts.get(name) || 0) + 1);
        });
    });

    return [...counts.entries()].sort((a, b) => {
        if (b[1] === a[1]) return a[0].localeCompare(b[0]);
        return b[1] - a[1];
    });
}

function getVisibleTopLevelModuleGroups() {
    const groupMap = new Map();

    cy.nodes(":visible").forEach((node) => {
        const memberships = node.data("module_memberships") || node.data(TOP_LEVEL_MODULE_DATA_KEY) || [];
        if (memberships.length === 0) return;
        const selectedModuleId = getSelectedPhenotypeModuleId();
        const membership =
            selectedModuleId && isTopLevelModuleModeActive()
                ? memberships.find((module) => module.id === selectedModuleId)
                : memberships[0];
        if (!membership) return;
        if (!groupMap.has(membership.id)) {
            groupMap.set(membership.id, {
                id: membership.id,
                label: membership.label,
                supportCount: 0,
                nodes: [],
            });
        }
        const group = groupMap.get(membership.id);
        group.supportCount += membership.support_count || 0;
        group.nodes.push(node);
    });

    return [...groupMap.values()]
        .map((group) => ({
            ...group,
            nodes: cy.collection(group.nodes),
        }))
        .sort((a, b) => {
            if (b.supportCount !== a.supportCount) return b.supportCount - a.supportCount;
            if (b.nodes.length !== a.nodes.length) return b.nodes.length - a.nodes.length;
            return a.label.localeCompare(b.label);
        });
}

function getSubnetworkFrameGroups() {
    if (isTopLevelModuleModeActive()) {
        return getVisibleTopLevelModuleGroups().map((group) => ({
            label: group.label,
            nodes: group.nodes,
            phenotypes: summarizeTopLevelModulePhenotypes(group.id, group.nodes),
            phenotypeSummaryVersion: subnetworkSummaryVersion,
        }));
    }

    return getOrderedComponents(cy).map((component, index) => ({
        label: `Module ${index + 1}`,
        component,
        nodes: component.nodes(),
        phenotypes: null,
        phenotypeSummaryVersion: -1,
    }));
}

function updateSubnetworkFrames() {
    if (!subnetworkOverlay) return;
    subnetworkOverlay.innerHTML = "";
    subnetworkMeta = [];

    const visibleGroups = getSubnetworkFrameGroups();
    const padding = 16;
    const containerWidth = cy.width();
    const containerHeight = cy.height();

    visibleGroups.forEach((group, idx) => {
        if (group.nodes.length === 0) return;
        const bbox = group.nodes.renderedBoundingBox({ includeOverlays: false, includeLabels: true });
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
        label.classList.add(visibleTop >= SUBNETWORK_LABEL_HEIGHT ? "subnetwork-frame__label--top" : "subnetwork-frame__label--bottom");
        label.textContent = group.label;
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

        subnetworkMeta.push({
            id: idx + 1,
            label: group.label,
            bbox: { x1: visibleLeft, y1: visibleTop, x2: visibleLeft + width, y2: visibleTop + height },
            component: group.component,
            phenotypes: group.phenotypes,
            phenotypeSummaryVersion: group.phenotypeSummaryVersion,
            nodes: group.nodes,
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

function translateNodes(nodes, dx, dy) {
    nodes.positions((node) => {
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

function placeNodesInGrid(nodes, center, spacing = MODULE_GROUP_NODE_SPACING) {
    const orderedNodes = nodes.toArray().sort((a, b) => {
        const labelA = a.data("label") || a.id();
        const labelB = b.data("label") || b.id();
        return labelA.localeCompare(labelB);
    });
    if (orderedNodes.length === 0) return;

    const cols = Math.ceil(Math.sqrt(orderedNodes.length));
    const rows = Math.ceil(orderedNodes.length / cols);
    const xOffset = ((cols - 1) * spacing) / 2;
    const yOffset = ((rows - 1) * spacing) / 2;

    orderedNodes.forEach((node, index) => {
        const col = index % cols;
        const row = Math.floor(index / cols);
        node.position({
            x: center.x + col * spacing - xOffset,
            y: center.y + row * spacing - yOffset,
        });
    });
}

function normalizeNodesToSpan(nodes, center, maxSpan) {
    const bbox = nodes.boundingBox({ includeLabels: true, includeOverlays: false });
    if (!bbox || !Number.isFinite(bbox.x1) || !Number.isFinite(bbox.y1)) {
        placeNodesInGrid(nodes, center);
        return;
    }

    const currentCenter = {
        x: (bbox.x1 + bbox.x2) / 2,
        y: (bbox.y1 + bbox.y2) / 2,
    };
    const span = Math.max(bbox.w || 0, bbox.h || 0);
    if (span < 1) {
        placeNodesInGrid(nodes, center);
        return;
    }

    const scale = span > maxSpan ? maxSpan / span : 1;
    nodes.positions((node) => {
        const pos = node.position();
        return {
            x: center.x + (pos.x - currentCenter.x) * scale,
            y: center.y + (pos.y - currentCenter.y) * scale,
        };
    });
}

function arrangeTopLevelModuleGroups() {
    const groups = getVisibleTopLevelModuleGroups();
    if (groups.length === 0) return false;

    groups.forEach((group) => {
        placeNodesInGrid(group.nodes, { x: 0, y: 0 });
    });

    const bboxes = groups.map((group) => group.nodes.boundingBox({ includeLabels: true, includeOverlays: false }));
    const maxW = Math.max(MODULE_GROUP_COMPACT_SPAN, ...bboxes.map((bbox) => bbox.w || 0));
    const maxH = Math.max(MODULE_GROUP_COMPACT_SPAN, ...bboxes.map((bbox) => bbox.h || 0));
    const tileW = maxW + TOP_LEVEL_MODULE_TILE_PADDING * 2;
    const tileH = maxH + TOP_LEVEL_MODULE_TILE_PADDING * 2;
    const cols = Math.max(1, Math.ceil(Math.sqrt(groups.length)));

    groups.forEach((group, index) => {
        const col = index % cols;
        const row = Math.floor(index / cols);
        const targetCenter = {
            x: col * tileW + tileW / 2,
            y: row * tileH + tileH / 2,
        };
        const bbox = bboxes[index];
        const currentCenter = {
            x: (bbox.x1 + bbox.x2) / 2,
            y: (bbox.y1 + bbox.y2) / 2,
        };

        translateNodes(group.nodes, targetCenter.x - currentCenter.x, targetCenter.y - currentCenter.y);
    });

    fitVisibleComponents();
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
        ensureSubnetworkPhenotypeSummary(component);
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

function clampNumber(value, min, max) {
    if (!Number.isFinite(value)) {
        return min;
    }
    return Math.min(Math.max(value, min), max);
}

function getSliderRoundedValues(slider) {
    if (!slider || !slider.noUiSlider) return null;
    return slider.noUiSlider.get().map((value) => Math.round(Number(value)));
}

function getSingleSliderValue(sliderInstance) {
    if (!sliderInstance) return null;
    const raw = sliderInstance.get();
    const value = Array.isArray(raw) ? raw[0] : raw;
    const numeric = Math.round(Number(value));
    if (!Number.isFinite(numeric)) return null;
    return numeric;
}

function syncRangeInputs(minInput, maxInput, values) {
    if (!minInput || !maxInput || !values) return;
    const [minValue, maxValue] = values;
    if (minInput.value !== String(minValue)) {
        minInput.value = minValue;
    }
    if (maxInput.value !== String(maxValue)) {
        maxInput.value = maxValue;
    }
}

function setupRangeInputs({ minInput, maxInput, slider, rangeMin, rangeMax, step = 1 }) {
    if (!minInput || !maxInput || !slider || !slider.noUiSlider) return;

    minInput.min = rangeMin;
    minInput.max = rangeMax;
    minInput.step = step;
    maxInput.min = rangeMin;
    maxInput.max = rangeMax;
    maxInput.step = step;

    syncRangeInputs(minInput, maxInput, getSliderRoundedValues(slider));

    const commit = () => {
        const currentValues = getSliderRoundedValues(slider) || [rangeMin, rangeMax];
        let minValue = Number(minInput.value);
        let maxValue = Number(maxInput.value);

        if (!Number.isFinite(minValue)) minValue = currentValues[0];
        if (!Number.isFinite(maxValue)) maxValue = currentValues[1];

        minValue = clampNumber(minValue, rangeMin, rangeMax);
        maxValue = clampNumber(maxValue, rangeMin, rangeMax);

        if (minValue > maxValue) {
            [minValue, maxValue] = [maxValue, minValue];
        }

        minValue = Math.round(minValue);
        maxValue = Math.round(maxValue);

        syncRangeInputs(minInput, maxInput, [minValue, maxValue]);
        slider.noUiSlider.set([minValue, maxValue]);
    };

    ["change", "blur"].forEach((eventName) => {
        minInput.addEventListener(eventName, () => commit());
        maxInput.addEventListener(eventName, () => commit());
    });

    minInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            commit();
        }
    });
    maxInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            commit();
        }
    });

    slider.noUiSlider.on("update", (values) => {
        const rounded = values.map((value) => Math.round(Number(value)));
        syncRangeInputs(minInput, maxInput, rounded);
    });
}

function setupSingleInput({ input, sliderInstance, rangeMin, rangeMax, step = 1 }) {
    if (!input || !sliderInstance) return;

    input.min = rangeMin;
    input.max = rangeMax;
    input.step = step;

    const initialValue = getSingleSliderValue(sliderInstance);
    if (initialValue !== null && input.value !== String(initialValue)) {
        input.value = initialValue;
    }

    const commit = () => {
        const currentValue = getSingleSliderValue(sliderInstance) ?? rangeMin;
        let value = Number(input.value);

        if (!Number.isFinite(value)) {
            value = currentValue;
        }

        value = clampNumber(value, rangeMin, rangeMax);
        value = Math.round(value);

        if (input.value !== String(value)) {
            input.value = value;
        }

        sliderInstance.set(value);
    };

    ["change", "blur"].forEach((eventName) => {
        input.addEventListener(eventName, () => commit());
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            commit();
        }
    });

    sliderInstance.on("update", (value) => {
        const nextValue = Math.round(Number(Array.isArray(value) ? value[0] : value));
        if (Number.isFinite(nextValue) && input.value !== String(nextValue)) {
            input.value = nextValue;
        }
    });
}

// --------------------------------------------------------
// Edge size slider for Phenotypes similarity
// --------------------------------------------------------

const edgeSlider = document.getElementById("filter-edge-slider");
const edgeMinInput = document.getElementById("edge-size-min-input");
const edgeMaxInput = document.getElementById("edge-size-max-input");
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

setupRangeInputs({
    minInput: edgeMinInput,
    maxInput: edgeMaxInput,
    slider: edgeSlider,
    rangeMin: edgeSliderRangeMin,
    rangeMax: edgeSliderRangeMax,
    step: 1,
});

// --------------------------------------------------------
// Effect size slider (Phenotype pages only)
// --------------------------------------------------------

const nodeSlider = document.getElementById("filter-node-slider");
const nodeMinInput = document.getElementById("node-color-min-input");
const nodeMaxInput = document.getElementById("node-color-max-input");
if (isPhenotypePage && nodeSlider && !isBinaryPhenotype) {
    noUiSlider.create(nodeSlider, {
        start: [NODE_SLIDER_MIN, NODE_SLIDER_MAX],
        connect: true,
        range: { min: NODE_SLIDER_MIN, max: NODE_SLIDER_MAX },
        step: 1,
    });

    setupRangeInputs({
        minInput: nodeMinInput,
        maxInput: nodeMaxInput,
        slider: nodeSlider,
        rangeMin: NODE_SLIDER_MIN,
        rangeMax: NODE_SLIDER_MAX,
        step: 1,
    });
}

// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

let filterByNodeColorAndEdgeSize = () => { };

function finishFilterUpdate({ runLayout = false, refreshCentrality = false } = {}) {
    invalidateSubnetworkSummaryCache();
    if (isNonGeneModulePage()) {
        applyNonGeneModuleFilter();
    } else {
        applyPhenotypeModuleOverlay();
    }

    if (runLayout) {
        layoutController.runLayoutWithRepulsion();
    } else {
        scheduleSubnetworkFrameUpdate();
    }

    checkEmptyState();

    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }

    if (refreshCentrality && typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
}

if (isPhenotypePage) {
    filterByNodeColorAndEdgeSize = function (options = {}) {
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

        const nodeDisplay = new Map();
        const visibleEdgeCounts = new Map();
        const edgeDisplay = new Map();
        const lowerNodeValue = Math.min(nodeMinValue, nodeMaxValue);
        const upperNodeValue = Math.max(nodeMinValue, nodeMaxValue);
        const lowerEdgeValue = Math.min(edgeMinValue, edgeMaxValue);
        const upperEdgeValue = Math.max(edgeMinValue, edgeMaxValue);

        cy.nodes().forEach((node) => {
            const nodeColorForFilter = node.data("node_color_for_filter") || node.data("node_color");
            const isVisible =
                nodeColorForFilter >= lowerNodeValue &&
                nodeColorForFilter <= upperNodeValue;
            nodeDisplay.set(node.id(), isVisible);
            if (isVisible) {
                visibleEdgeCounts.set(node.id(), 0);
            }
        });

        cy.edges().forEach((edge) => {
            const edgeSize = edge.data("edge_size");
            const sharedPhenotypes = edge.data("phenotype") || [];
            const source = edge.data("source");
            const target = edge.data("target");
            const sourceVisible = nodeDisplay.get(source) === true;
            const targetVisible = nodeDisplay.get(target) === true;

            const isVisible =
                sourceVisible &&
                targetVisible &&
                edgeSize >= lowerEdgeValue &&
                edgeSize <= upperEdgeValue &&
                sharedPhenotypes.length >= 2;

            edgeDisplay.set(edge, isVisible);
            if (isVisible) {
                visibleEdgeCounts.set(source, (visibleEdgeCounts.get(source) || 0) + 1);
                visibleEdgeCounts.set(target, (visibleEdgeCounts.get(target) || 0) + 1);
            }
        });

        cy.batch(() => {
            cy.nodes().forEach((node) => {
                const shouldShow = nodeDisplay.get(node.id()) === true && (visibleEdgeCounts.get(node.id()) || 0) > 0;
                setBaseVisibilityScratch(node, shouldShow);
                node.style("display", shouldShow ? "element" : "none");
            });

            cy.edges().forEach((edge) => {
                const shouldShow = edgeDisplay.get(edge) === true;
                setBaseVisibilityScratch(edge, shouldShow);
                edge.style("display", shouldShow ? "element" : "none");
            });
        });

        finishFilterUpdate(options);
    };
} else if (isGeneSymbolPage) {
    filterByNodeColorAndEdgeSize = function (options = {}) {
        const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

        let selectedMin = Math.min(...edgeSliderValues);
        let selectedMax = Math.max(...edgeSliderValues);

        if (edgeMin === edgeMax) {
            selectedMin = edgeMin;
            selectedMax = edgeMax;
        }

        const edgeMinValue = Math.max(edgeMin, selectedMin);
        const edgeMaxValue = Math.min(edgeMax, selectedMax);
        const targetGene = pageConfig.name;
        const targetNode = cy.getElementById(targetGene);

        if (targetNode.length === 0) {
            updateNoNodesMessage(true);
            return;
        }

        const directlyConnectedNodes = new Set([targetGene]);
        const edgeWithinScoreRange = new Map();
        const lowerEdgeValue = Math.min(edgeMinValue, edgeMaxValue);
        const upperEdgeValue = Math.max(edgeMinValue, edgeMaxValue);

        cy.edges().forEach((edge) => {
            const edgeSize = edge.data("edge_size");
            const source = edge.data("source");
            const target = edge.data("target");
            const isInRange = edgeSize >= lowerEdgeValue && edgeSize <= upperEdgeValue;
            edgeWithinScoreRange.set(edge, isInRange);

            if (!isInRange) {
                return;
            }
            if (source === targetGene) {
                directlyConnectedNodes.add(target);
            } else if (target === targetGene) {
                directlyConnectedNodes.add(source);
            }
        });

        cy.batch(() => {
            cy.nodes().forEach((node) => {
                const nodeId = node.data("id");
                node.style("display", directlyConnectedNodes.has(nodeId) ? "element" : "none");
            });

            cy.edges().forEach((edge) => {
                const source = edge.data("source");
                const target = edge.data("target");
                const isVisible =
                    edgeWithinScoreRange.get(edge) === true &&
                    directlyConnectedNodes.has(source) &&
                    directlyConnectedNodes.has(target);

                edge.style("display", isVisible ? "element" : "none");
            });
        });

        finishFilterUpdate(options);
    };
} else {
    filterByNodeColorAndEdgeSize = function (options = {}) {
        const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
        const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax, 1, 100);
        const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax, 1, 100);

        cy.batch(() => {
            cy.nodes().forEach((node) => node.style("display", "element"));

            cy.edges().forEach((edge) => {
                const edgeSize = edge.data("edge_size");
                const isVisible =
                    edgeSize >= Math.min(edgeMinValue, edgeMaxValue) &&
                    edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
                setBaseVisibilityScratch(edge, isVisible);
                edge.style("display", isVisible ? "element" : "none");
            });
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

        cy.batch(() => {
            cy.nodes().forEach((node) => {
                const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
                const shouldShow = visibleEdges.length > 0;
                setBaseVisibilityScratch(node, shouldShow);
                node.style("display", shouldShow ? "element" : "none");
            });
        });

        finishFilterUpdate(options);
    };
}

if (edgeSlider && edgeSlider.noUiSlider) {
    edgeSlider.noUiSlider.on("update", function (values) {
        filterByNodeColorAndEdgeSize({ runLayout: false, refreshCentrality: false });
    });
    edgeSlider.noUiSlider.on("set", function () {
        filterByNodeColorAndEdgeSize({ runLayout: false, refreshCentrality: true });
        queueAutoArrange({ afterLayout: true, delayMs: AUTO_ARRANGE_DELAY_MS });
    });
}

if (isPhenotypePage && nodeSlider && nodeSlider.noUiSlider) {
    nodeSlider.noUiSlider.on("update", function (values) {
        filterByNodeColorAndEdgeSize({ runLayout: false, refreshCentrality: false });
    });
    nodeSlider.noUiSlider.on("set", function () {
        filterByNodeColorAndEdgeSize({ runLayout: false, refreshCentrality: true });
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
    const sourceElements = isGenotypeAllSelected() ? baseElements : elements;
    filterElementsByGenotypeAndSex(sourceElements, cy, targetPhenotype, () => {
        restoreElementStateAfterReset();
        filterByNodeColorAndEdgeSize({ runLayout: !isGeneSymbolPage, refreshCentrality: false });
    });
    if (typeof window.recalculateCentrality === "function") {
        window.recalculateCentrality();
    }
    queueAutoArrange({ afterLayout: !isGeneSymbolPage, delayMs: AUTO_ARRANGE_DELAY_MS });
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

const fontSizeInput = document.getElementById("font-size-input");
const fontSizeSliderInstance = createSlider("font-size-slider", DEFAULT_FONT_SIZE, 1, 50, 1, (intValues) => {
    if (fontSizeInput) {
        fontSizeInput.value = intValues;
    }
    cy.style()
        .selector("node")
        .style("font-size", intValues + "px")
        .update();
});

const edgeWidthInput = document.getElementById("edge-width-input");
const edgeWidthSliderInstance = createSlider("edge-width-slider", DEFAULT_LINE_WIDTH, 1, 10, 1, (intValues) => {
    if (edgeWidthInput) {
        edgeWidthInput.value = intValues;
    }
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
if (layoutDropdown) {
    layoutDropdown.value = layoutController.getLayout();
}

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

const nodeRepulsionInput = document.getElementById("node-repulsion-input");
const nodeRepulsionSliderInstance = createSlider("nodeRepulsion-slider", defaultNodeRepulsion, 1, 10, 1, (intValues) => {
    if (nodeRepulsionInput) {
        nodeRepulsionInput.value = intValues;
    }
    layoutController.updateRepulsionScale(intValues);
    layoutController.scheduleNodeRepulsion();
    if (layoutController.getLayout() !== "random") {
        layoutController.queueLayoutRefresh(150);
    }
});

setupSingleInput({
    input: fontSizeInput,
    sliderInstance: fontSizeSliderInstance,
    rangeMin: 1,
    rangeMax: 50,
    step: 1,
});

setupSingleInput({
    input: edgeWidthInput,
    sliderInstance: edgeWidthSliderInstance,
    rangeMin: 1,
    rangeMax: 10,
    step: 1,
});

setupSingleInput({
    input: nodeRepulsionInput,
    sliderInstance: nodeRepulsionSliderInstance,
    rangeMin: 1,
    rangeMax: 10,
    step: 1,
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
        ensureSubnetworkPhenotypeSummary(component);
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

function getExportModuleFrameToggles() {
    return [
        document.getElementById("export-module-frames"),
        document.getElementById("export-module-frames-mobile"),
    ].filter(Boolean);
}

function syncExportModuleFrameToggles() {
    const toggles = getExportModuleFrameToggles();
    toggles.forEach((toggle) => {
        toggle.addEventListener("change", () => {
            toggles.forEach((otherToggle) => {
                if (otherToggle !== toggle) {
                    otherToggle.checked = toggle.checked;
                }
            });
        });
    });
}

function shouldIncludeModuleFramesInImageExport() {
    const toggles = getExportModuleFrameToggles();
    if (toggles.length === 0) return true;
    return toggles.some((toggle) => toggle.checked);
}

function buildModuleFrameExportFrames() {
    if (!shouldIncludeModuleFramesInImageExport()) return [];

    return getSubnetworkFrameGroups().flatMap((group, index) => {
        if (!group.nodes || group.nodes.length === 0) return [];

        const bbox = group.nodes.boundingBox({ includeOverlays: false, includeLabels: true });
        if (!bbox || !Number.isFinite(bbox.x1) || !Number.isFinite(bbox.y1)) {
            return [];
        }

        const x1 = bbox.x1 - EXPORT_FRAME_PADDING;
        const y1 = bbox.y1 - EXPORT_FRAME_PADDING;
        const x2 = bbox.x2 + EXPORT_FRAME_PADDING;
        const y2 = bbox.y2 + EXPORT_FRAME_PADDING;
        const width = x2 - x1;
        const height = y2 - y1;
        if (width <= 0 || height <= 0) return [];

        return [{
            label: group.label || `Module ${index + 1}`,
            x1,
            y1,
            x2,
            y2,
            labelX: x1,
            labelY: y1 - EXPORT_FRAME_LABEL_OFFSET,
        }];
    });
}

function getImageExportOptions() {
    return {
        frames: buildModuleFrameExportFrames(),
    };
}

function getCurrentCsvExportMode() {
    if (isTopLevelModuleModeActive()) {
        return "top-level-mp";
    }

    const selectedTopLevelInput = document.querySelector('input[name="phenotype-module-mode"][value="top-level-mp"]');
    if (selectedTopLevelInput && selectedTopLevelInput.checked) {
        return "top-level-mp";
    }

    const dropdown = document.getElementById("phenotype-module-dropdown");
    const firstOption = dropdown && dropdown.options.length > 0 ? dropdown.options[0].textContent || "" : "";
    return firstOption.toLowerCase().includes("top-level") ? "top-level-mp" : "similarity";
}

function getCsvExportOptions() {
    const csvMode = getCurrentCsvExportMode();
    if (csvMode === "top-level-mp") {
        refreshVisibleTopLevelModuleData();
    }

    return {
        csvMode,
        topLevelModuleDataKey: TOP_LEVEL_MODULE_DATA_KEY,
    };
}

syncExportModuleFrameToggles();

attachExportHandler("export-png", () => exportGraphAsPNG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-jpg", () => exportGraphAsJPG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-svg", () => exportGraphAsSVG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-csv", () => exportGraphAsCSV(cy, fileName, getCsvExportOptions()));
attachExportHandler("export-graphml", () => exportGraphAsGraphML(cy, fileName));

attachExportHandler("export-png-mobile", () => exportGraphAsPNG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-jpg-mobile", () => exportGraphAsJPG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-svg-mobile", () => exportGraphAsSVG(cy, fileName, getImageExportOptions()));
attachExportHandler("export-csv-mobile", () => exportGraphAsCSV(cy, fileName, getCsvExportOptions()));
attachExportHandler("export-graphml-mobile", () => exportGraphAsGraphML(cy, fileName));

// ############################################################################
// UI Helpers
// ############################################################################

function checkEmptyState() {
    const visibleNodes = cy.nodes(":visible").length;
    const visibleEdges = cy.edges(":visible").length;
    let shouldShow = visibleNodes === 0;

    if (isGeneSymbolPage) {
        const targetNode = cy.getElementById(pageConfig.name);
        const targetVisible = targetNode.length > 0 && targetNode.style("display") !== "none";
        if (!targetVisible || visibleEdges === 0) {
            shouldShow = true;
        }
    }

    updateNoNodesMessage(shouldShow);
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
    if (isTopLevelModuleModeActive()) {
        arrangeTopLevelModuleGroups();
    } else if (layoutController.getLayout() === "grid") {
        tileComponents();
    }
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

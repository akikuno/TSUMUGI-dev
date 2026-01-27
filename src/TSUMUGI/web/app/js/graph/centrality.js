/**
 * Count the number of phenotypes for a node, excluding empty entries.
 * @param {Object} node - Cytoscape node
 * @returns {number} Number of phenotypes associated with the node
 */
function countNodePhenotypes(node) {
    const nodeData = node.data();
    const phenotypes = nodeData.phenotype || [];
    const phenotypeArray = Array.isArray(phenotypes) ? phenotypes : [phenotypes];
    return phenotypeArray.filter((p) => p && p !== "").length;
}

/**
 * Calculate degree centrality for all visible nodes in the network
 * @param {Object} cy - Cytoscape instance
 * @returns {Map} Map of node id to degree centrality value
 */
export function calculateDegreeCentrality(cy) {
    const degreeCentrality = new Map();

    // Get only visible nodes
    const visibleNodes = cy.nodes().filter(node => node.style('display') === 'element');

    visibleNodes.forEach(node => {
        // Count only visible edges
        const visibleEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        const degree = visibleEdges.length;
        degreeCentrality.set(node.id(), degree);
    });

    return degreeCentrality;
}

/**
 * Calculate betweenness centrality using Brandes algorithm
 * Brandes' algorithm is O(n*m) for unweighted graphs where n = nodes, m = edges
 * @param {Object} cy - Cytoscape instance
 * @returns {Map} Map of node id to betweenness centrality value
 */
export function calculateBetweennessCentrality(cy) {
    const visibleNodes = cy.nodes().filter(node => node.style('display') === 'element');
    const betweennessCentrality = new Map();

    // Initialize all nodes with 0
    visibleNodes.forEach(node => {
        betweennessCentrality.set(node.id(), 0);
    });

    // If there are less than 3 nodes, betweenness centrality is 0 for all
    if (visibleNodes.length < 3) {
        return betweennessCentrality;
    }

    // Build adjacency list for visible nodes only
    const adjacencyList = new Map();
    visibleNodes.forEach(node => {
        adjacencyList.set(node.id(), []);
    });

    // Add edges to adjacency list (only if both nodes are visible)
    cy.edges().filter(edge => edge.style('display') === 'element').forEach(edge => {
        const source = edge.source().id();
        const target = edge.target().id();
        if (adjacencyList.has(source) && adjacencyList.has(target)) {
            adjacencyList.get(source).push(target);
            adjacencyList.get(target).push(source); // Undirected graph
        }
    });

    // Brandes algorithm main loop
    visibleNodes.forEach(s => {
        const S = []; // Stack
        const P = new Map(); // Predecessors
        const sigma = new Map(); // Number of shortest paths
        const d = new Map(); // Distance
        const delta = new Map(); // Dependency

        // Initialize
        visibleNodes.forEach(node => {
            P.set(node.id(), []);
            sigma.set(node.id(), 0);
            d.set(node.id(), -1);
            delta.set(node.id(), 0);
        });

        sigma.set(s.id(), 1);
        d.set(s.id(), 0);

        // BFS
        const Q = [s.id()];
        while (Q.length > 0) {
            const v = Q.shift();
            S.push(v);

            const neighbors = adjacencyList.get(v) || [];
            neighbors.forEach(w => {
                // First time we reach w?
                if (d.get(w) < 0) {
                    Q.push(w);
                    d.set(w, d.get(v) + 1);
                }
                // Shortest path to w via v?
                if (d.get(w) === d.get(v) + 1) {
                    sigma.set(w, sigma.get(w) + sigma.get(v));
                    P.get(w).push(v);
                }
            });
        }

        // Accumulation - back propagation of dependencies
        while (S.length > 0) {
            const w = S.pop();
            const predecessors = P.get(w) || [];
            predecessors.forEach(v => {
                const sigmav = sigma.get(v) || 1;
                const sigmaw = sigma.get(w) || 1;
                const deltav = delta.get(v) || 0;
                const deltaw = delta.get(w) || 0;
                delta.set(v, deltav + (sigmav / sigmaw) * (1 + deltaw));
            });
            if (w !== s.id()) {
                const current = betweennessCentrality.get(w) || 0;
                betweennessCentrality.set(w, current + delta.get(w));
            }
        }
    });

    // For undirected graphs, divide by 2
    betweennessCentrality.forEach((value, key) => {
        betweennessCentrality.set(key, value / 2);
    });

    // Normalize by the maximum possible betweenness centrality: (n-1)(n-2)/2 for undirected graphs
    const n = visibleNodes.length;
    if (n > 2) {
        const normalizationFactor = ((n - 1) * (n - 2)) / 2;
        betweennessCentrality.forEach((value, key) => {
            betweennessCentrality.set(key, value / normalizationFactor);
        });
    }

    return betweennessCentrality;
}

/**
 * Calculate normalized degree centrality (degree divided by phenotype count)
 * @param {Object} cy - Cytoscape instance
 * @returns {Map} Map of node id to normalized degree centrality value
 */
export function calculateNormalizedDegreeCentrality(cy) {
    const normalizedDegreeCentrality = new Map();
    const degreeCentrality = calculateDegreeCentrality(cy);
    const visibleNodes = cy.nodes().filter(node => node.style('display') === 'element');

    visibleNodes.forEach(node => {
        const degree = degreeCentrality.get(node.id()) || 0;
        const phenotypeCount = countNodePhenotypes(node);
        const normalizedDegree = phenotypeCount > 0 ? degree / phenotypeCount : 0;
        normalizedDegreeCentrality.set(node.id(), normalizedDegree);
    });

    return normalizedDegreeCentrality;
}

/**
 * Calculate normalized betweenness centrality (betweenness divided by phenotype count)
 * @param {Object} cy - Cytoscape instance
 * @returns {Map} Map of node id to normalized betweenness centrality value
 */
export function calculateNormalizedBetweennessCentrality(cy) {
    const normalizedBetweennessCentrality = new Map();
    const betweennessCentrality = calculateBetweennessCentrality(cy);
    const visibleNodes = cy.nodes().filter(node => node.style('display') === 'element');

    visibleNodes.forEach(node => {
        const betweenness = betweennessCentrality.get(node.id()) || 0;
        const phenotypeCount = countNodePhenotypes(node);
        const normalizedBetweenness = phenotypeCount > 0 ? betweenness / phenotypeCount : 0;
        normalizedBetweennessCentrality.set(node.id(), normalizedBetweenness);
    });

    return normalizedBetweennessCentrality;
}

/**
 * Update node data with centrality values
 * @param {Object} cy - Cytoscape instance
 * @param {Map} centralityMap - Map of node id to centrality value
 * @param {string} centralityType - Type of centrality ('degree' or 'betweenness')
 */
export function updateNodeCentrality(cy, centralityMap, centralityType) {
    cy.nodes().forEach(node => {
        const centralityValue = centralityMap.get(node.id()) || 0;
        node.data(`${centralityType}_centrality`, centralityValue);
    });
}

/**
 * Get min and max centrality values from visible nodes
 * @param {Object} cy - Cytoscape instance
 * @param {string} centralityType - Type of centrality ('degree' or 'betweenness')
 * @returns {Object} Object with min and max values
 */
export function getCentralityRange(cy, centralityType) {
    const visibleNodes = cy.nodes().filter(node => node.style('display') === 'element');
    const values = visibleNodes.map(node => node.data(`${centralityType}_centrality`) || 0);

    if (values.length === 0) {
        return { min: 0, max: 0 };
    }

    return {
        min: Math.min(...values),
        max: Math.max(...values)
    };
}

// ############################################################################
// Centrality UI state and management
// ############################################################################

let centralityType = 'normalized_degree'; // active options: none, degree, betweenness, normalized_degree, normalized_betweenness
let centralityScale = 0; // 0 to 1 scale factor
let cytoscapeInstance = null;
let createSliderFunction = null;
let isCentralityInputBound = false;

function clampNumber(value, min, max) {
    if (!Number.isFinite(value)) {
        return min;
    }
    return Math.min(Math.max(value, min), max);
}

function setupCentralityInput(sliderInstance) {
    if (!sliderInstance || isCentralityInputBound) return;
    const input = document.getElementById("centrality-scale-input");
    if (!input) return;

    const rangeMin = 0;
    const rangeMax = 100;

    input.min = rangeMin;
    input.max = rangeMax;
    input.step = 1;

    const initial = Math.round(Number(sliderInstance.get()));
    if (Number.isFinite(initial)) {
        input.value = initial;
    }

    const commit = () => {
        const currentValue = Math.round(Number(sliderInstance.get()));
        let value = Number(input.value);
        if (!Number.isFinite(value)) {
            value = currentValue;
        }
        value = clampNumber(value, rangeMin, rangeMax);
        value = Math.round(value);
        input.value = value;
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

    isCentralityInputBound = true;
}

/**
 * Initialize centrality system with dependencies
 * @param {Object} cy - Cytoscape instance
 * @param {Function} createSlider - Slider creation function
 */
export function initializeCentralitySystem(cy, createSlider) {
    cytoscapeInstance = cy;
    createSliderFunction = createSlider;

    // Set up global handler for HTML onchange
    window.handleCentralityTypeChange = handleCentralityTypeChange;

    // Initialize controls
    initializeCentralityControls();
    const centralityDropdown = document.getElementById("centrality-type-dropdown");
    if (centralityDropdown) {
        centralityDropdown.value = centralityType;
    }
    handleCentralityTypeChange(centralityType);

    // Calculate initial centrality values
    setTimeout(() => {
        recalculateCentrality();
    }, 500);
}

/**
 * Handle centrality type change from dropdown
 * @param {string} value - Selected centrality type
 */
function handleCentralityTypeChange(value) {
    centralityType = value;

    const container = document.getElementById("centrality-slider-container");
    if (container) {
        if (value === 'none') {
            container.style.display = 'none';
            centralityScale = 0;
            if (window.centralitySliderInstance) {
                window.centralitySliderInstance.set(0);
            }
        } else {
            container.style.display = 'block';
            // Initialize slider if not already done
            if (!window.centralitySliderInstance) {
                initializeCentralitySlider();
            }
        }
        updateNodeSizeByCentrality();
    }
}

/**
 * Initialize the centrality scale slider
 */
function initializeCentralitySlider() {
    const sliderElement = document.getElementById("centrality-scale-slider");
    if (sliderElement && createSliderFunction) {
        const sliderInstance = createSliderFunction("centrality-scale-slider", 0, 0, 100, 1, (value) => {
            // Convert 0-100 integer to 0.00-1.00 for internal calculation
            centralityScale = parseInt(value) / 100;
            const input = document.getElementById("centrality-scale-input");
            if (input) {
                input.value = parseInt(value);
            }
            updateNodeSizeByCentrality();
        });
        window.centralitySliderInstance = sliderInstance;
        setupCentralityInput(sliderInstance);
    } else {
        console.error("Centrality slider element not found or createSlider function not available");
    }
}

/**
 * Calculate and update centrality values for all visible nodes
 */
export function recalculateCentrality() {
    if (!cytoscapeInstance) {
        console.error("Cytoscape instance not available for centrality calculation");
        return;
    }

    // Calculate centrality for visible nodes
    const degreeCentrality = calculateDegreeCentrality(cytoscapeInstance);
    const betweennessCentrality = calculateBetweennessCentrality(cytoscapeInstance);
    const normalizedDegreeCentrality = calculateNormalizedDegreeCentrality(cytoscapeInstance);
    const normalizedBetweennessCentrality = calculateNormalizedBetweennessCentrality(cytoscapeInstance);

    // Update node data with centrality values
    updateNodeCentrality(cytoscapeInstance, degreeCentrality, 'degree');
    updateNodeCentrality(cytoscapeInstance, betweennessCentrality, 'betweenness');
    updateNodeCentrality(cytoscapeInstance, normalizedDegreeCentrality, 'normalized_degree');
    updateNodeCentrality(cytoscapeInstance, normalizedBetweennessCentrality, 'normalized_betweenness');

    // Apply node size updates if sliders are active
    updateNodeSizeByCentrality();
}

/**
 * Update node sizes based on current centrality settings
 */
function updateNodeSizeByCentrality() {
    if (!cytoscapeInstance) {
        return;
    }

    const baseSize = 15; // Consistent base size

    if (centralityType === 'none' || centralityScale === 0) {
        // Reset all nodes to default size
        cytoscapeInstance.nodes().forEach(node => {
            node.style({
                'width': baseSize,
                'height': baseSize
            });
        });
        return;
    }

    const centralityRange = getCentralityRange(cytoscapeInstance, centralityType);

    cytoscapeInstance.nodes().forEach(node => {
        let size = baseSize; // Start with base size

        if (centralityType === 'degree' && centralityRange.max > centralityRange.min) {
            const degreeCentrality = node.data('degree_centrality') || 0;
            const normalizedDegree = (degreeCentrality - centralityRange.min) / (centralityRange.max - centralityRange.min);
            // Add scaling on top of base size
            size = baseSize + (normalizedDegree * 35 * centralityScale);
        } else if (centralityType === 'betweenness') {
            const betweennessCentrality = node.data('betweenness_centrality') || 0;

            // Use logarithmic scaling for better differentiation
            // Add 1 to avoid log(0) and ensure nodes with 0 centrality have minimum size
            const logCentrality = Math.log10(betweennessCentrality + 1);
            const maxLogCentrality = Math.log10((centralityRange.max || 1) + 1);

            // Normalize using log scale
            const normalizedBetweenness = maxLogCentrality > 0 ? logCentrality / maxLogCentrality : 0;

            // Add scaling on top of base size
            const scalingFactor = normalizedBetweenness * 35 * centralityScale;
            size = baseSize + scalingFactor;

            // Ensure nodes with centrality > 0 are visually distinct from those with 0
            // Only apply minimum boost if there's actual scaling happening
            if (betweennessCentrality > 0 && centralityScale > 0 && scalingFactor < 2) {
                size = baseSize + 2; // Minimum visible increase for non-zero centrality
            }
        } else if (centralityType === 'normalized_degree' && centralityRange.max > centralityRange.min) {
            const normalizedDegreeCentrality = node.data('normalized_degree_centrality') || 0;
            const normalizedValue = (normalizedDegreeCentrality - centralityRange.min) / (centralityRange.max - centralityRange.min);
            size = baseSize + (normalizedValue * 35 * centralityScale);
        } else if (centralityType === 'normalized_betweenness') {
            const normalizedBetweennessCentrality = node.data('normalized_betweenness_centrality') || 0;
            const epsilon = 0.001;
            const logCentrality = Math.log10(normalizedBetweennessCentrality + epsilon);
            const maxLogCentrality = Math.log10((centralityRange.max || epsilon) + epsilon);
            const minLogCentrality = Math.log10(epsilon);
            const normalizedLog = maxLogCentrality > minLogCentrality
                ? (logCentrality - minLogCentrality) / (maxLogCentrality - minLogCentrality)
                : 0;
            const scalingFactor = normalizedLog * 35 * centralityScale;
            size = baseSize + scalingFactor;

            if (normalizedBetweennessCentrality > 0 && centralityScale > 0 && scalingFactor < 2) {
                size = baseSize + 2;
            }
        }

        node.style({
            'width': size,
            'height': size
        });
    });
}

/**
 * Initialize centrality controls in the DOM
 */
function initializeCentralityControls() {

    const centralityDropdown = document.getElementById("centrality-type-dropdown");

    if (centralityDropdown) {
        if (typeof window.handleCentralityTypeChange !== 'function') {
            console.error("Global handler not available");
        }
    } else {
        console.error("Centrality dropdown not found");
    }
}

/**
 * Set up DOM event listeners for centrality controls
 */
function setupCentralityEventListeners() {
    // Initialize centrality controls
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCentralityControls);
    } else {
        initializeCentralityControls();
    }

    // Backup initialization
    setTimeout(initializeCentralityControls, 500);
}

// Set up event listeners when module is imported
setupCentralityEventListeners();

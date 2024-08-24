// ========================================================
// Input handling
// ========================================================

const elements = (function () {
    const req = new XMLHttpRequest();
    let result = null;
    req.onreadystatechange = function () {
        if (req.readyState === 4 && req.status === 200) {
            result = JSON.parse(req.responseText);
        }
    };
    req.open("GET", "https://www.md.tsukuba.ac.jp/LabAnimalResCNT/test-tsumugi/network/data/XXX.json", false);
    // req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/3615e66d75627351f3b3c2300cc27101d46cd749/network.json", false);
    req.send(null);
    return result;
})();

// ========================================================
// Normalize node color and edge sizes
// ========================================================

const nodeSizes = elements.filter(ele => ele.data.node_color !== undefined).map(ele => ele.data.node_color);
const edgeSizes = elements.filter(ele => ele.data.edge_size !== undefined).map(ele => ele.data.edge_size);

const nodeMin = Math.min(...nodeSizes);
const nodeMax = Math.max(...nodeSizes);
const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);

// Function to normalize edge sizes to a range of 0.5 to 2
function normalizeEdgeSize(edgeSize) {
    const minRange = 1;
    const maxRange = 10;
    return minRange + (edgeSize - edgeMin) * (maxRange - minRange) / (edgeMax - edgeMin);
}

function scaleToOriginalRange(value, minValue, maxValue) {
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

function scaleToSliderRange(value, minValue, maxValue) {
    return 1 + (value - minValue) * 9 / (maxValue - minValue);
}

function getColorForValue(value) {
    const ratio = (value - 1) / (10 - 1);
    const r1 = 248, g1 = 229, b1 = 140; // Light Yellow
    const r2 = 255, g2 = 140, b2 = 0;   // Orange

    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return `rgb(${r}, ${g}, ${b})`;
}

// ========================================================
// Cytoscape handling
// ========================================================

let currentLayout = 'cose';

const cy = cytoscape({
    container: document.querySelector('.cy'),
    elements: elements,
    style: [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-family': 'Roboto',
                'font-size': '20px',
                'width': 15,
                'height': 15,
                'background-color': function (ele) {
                    const color_value = scaleToOriginalRange(ele.data('node_color'), nodeMin, nodeMax);
                    return getColorForValue(color_value);
                }
            }
        },
        {
            selector: 'edge',
            style: {
                'curve-style': 'bezier',
                'text-rotation': 'autorotate',
                'width': function (ele) {
                    const originalSize = ele.data('edge_size');
                    return normalizeEdgeSize(originalSize);
                }
            }
        }
    ],
    layout: { name: currentLayout }
});

// Event listener for layout change
document.getElementById('layout-dropdown').addEventListener('change', function () {
    currentLayout = this.value;
    cy.layout({ name: currentLayout }).run();
});

// Event listeners for sliders
document.getElementById('node-color-slider').addEventListener('input', function () {
    document.getElementById('node-color-value').textContent = this.value;
    filterElements();
});

document.getElementById('edge-size-slider').addEventListener('input', function () {
    document.getElementById('edge-size-value').textContent = this.value;
    filterElements();
});

document.getElementById('font-size-slider').addEventListener('input', function () {
    const fontSize = this.value + 'px';
    document.getElementById('font-size-value').textContent = this.value;
    cy.style()
        .selector('node')
        .style('font-size', fontSize)
        .update();
});

// ========================================================
// Filtering function
// ========================================================

function filterElements() {
    const nodeColorSliderValue = parseFloat(document.getElementById('node-color-slider').value);
    const edgeSizeSliderValue = parseFloat(document.getElementById('edge-size-slider').value);

    const nodeThreshold = scaleToOriginalRange(nodeColorSliderValue, nodeMin, nodeMax);
    const edgeThreshold = scaleToOriginalRange(edgeSizeSliderValue, edgeMin, edgeMax);

    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', nodeColor >= nodeThreshold ? 'element' : 'none');
    });

    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data('edge_size');
        const sourceNode = cy.getElementById(edge.data('source'));
        const targetNode = cy.getElementById(edge.data('target'));

        if (sourceNode.style('display') === 'element' && targetNode.style('display') === 'element' && edgeSize >= edgeThreshold) {
            edge.style('display', 'element');
        } else {
            edge.style('display', 'none');
        }
    });

    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        if (connectedEdges.length === 0) {
            node.style('display', 'none');
        }
    });

    cy.layout({ name: currentLayout, componentSpacing: 100, nodeRepulsion: 100 }).run();
}

// ========================================================
// Tooltip handling
// ========================================================

cy.on('tap', 'node, edge', function (event) {
    const data = event.target.data();
    let tooltipText = '';

    if (event.target.isNode()) {
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(function (anno) { return '・ ' + anno; }).join('<br>')
            : '・ ' + data.annotation;
        tooltipText = "<b>Phenotypes of " + data.label + " KO</b><br>" + annotations;
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data('label');
        const targetNode = cy.getElementById(data.target).data('label');
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(function (anno) { return '・ ' + anno; }).join('<br>')
            : '・ ' + data.annotation;
        tooltipText = "<b>Shared phenotypes of " + sourceNode + " and " + targetNode + " KOs</b><br>" + annotations;
    }

    document.querySelector('.tooltip-container').innerHTML = tooltipText;
});

// Initial filtering and node color setup
filterElements();

// ========================================================
// Input handling
// ========================================================

const elements = [
    { data: { id: 'Nanog', label: 'Nanog', annotation: ['hoge', 'hooo'], node_color: 50 } },
    { data: { id: 'Pou5f1', label: 'Pou5f1', annotation: 'fuga', node_color: 100 } },
    { data: { id: 'Sox2', label: 'Sox2', annotation: 'foo', node_color: 3 } },
    { data: { source: 'Nanog', target: 'Pou5f1', annotation: 'Foo', edge_size: 5 } },
    { data: { source: 'Nanog', target: 'Sox2', annotation: 'FooBar', edge_size: 1 } },
    { data: { source: 'Sox2', target: 'Pou5f1', annotation: 'FooBar', edge_size: 10 } },
];

// const elements = (function () {
//     const req = new XMLHttpRequest();
//     let result = null;
//     req.onreadystatechange = function () {
//         if (req.readyState === 4 && req.status === 200) {
//             result = JSON.parse(req.responseText);
//         }
//     };
//     req.open("GET", "https://www.md.tsukuba.ac.jp/LabAnimalResCNT/test-tsumugi/network/data/XXX.json", false);
//     // req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/3615e66d75627351f3b3c2300cc27101d46cd749/network.json", false);
//     req.send(null);
//     return result;
// })();

// ========================================================
// Normalize node color and edge sizes
// ========================================================

const nodeSizes = elements.filter(ele => ele.data.node_color !== undefined).map(ele => ele.data.node_color);
const edgeSizes = elements.filter(ele => ele.data.edge_size !== undefined).map(ele => ele.data.edge_size);

const nodeMin = Math.min(...nodeSizes);
const nodeMax = Math.max(...nodeSizes);
const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);


function scaleToOriginalRange(value, minValue, maxValue) {
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

function scaleValue(value, minValue, maxValue, minScale, maxScale) {
    // スケール範囲をminScaleとmaxScaleに合わせて変換
    return minScale + (value - minValue) * (maxScale - minScale) / (maxValue - minValue);
}

function getColorForValue(value) {
    // value を1-10の範囲から0-1の範囲に変換
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
                'font-size': '20px',
                'width': 15,
                'height': 15,
                'background-color': function (ele) {
                    const color_value = scaleValue(ele.data('node_color'), nodeMin, nodeMax, 1, 10);
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
                    return scaleValue(ele.data('edge_size'), edgeMin, edgeMax, 0.5, 2);
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

document.getElementById('font-size-slider').addEventListener('input', function () {
    const fontSize = this.value + 'px';
    document.getElementById('font-size-value').textContent = this.value;
    cy.style()
        .selector('node')
        .style('font-size', fontSize)
        .update();
});

// ========================================================
// Filtering function for nodes (node-color-slider)
// ========================================================

function filterNodesByColor() {
    const nodeColorSliderValue = parseFloat(document.getElementById('node-color-slider').value);
    const nodeThreshold = scaleToOriginalRange(nodeColorSliderValue, nodeMin, nodeMax);

    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', nodeColor >= nodeThreshold ? 'element' : 'none');
    });

    // Apply layout after node filtering
    cy.layout({ name: currentLayout, componentSpacing: 100, nodeRepulsion: 100 }).run();
}

// Event listeners for sliders
document.getElementById('node-color-slider').addEventListener('input', function () {
    document.getElementById('node-color-value').textContent = this.value;
    filterNodesByColor();
});


// ========================================================
// Filtering function for edges (edge-size-slider)
// ========================================================

function filterEdgesBySize() {
    const edgeSizeSliderValue = parseFloat(document.getElementById('edge-size-slider').value);
    const edgeThreshold = scaleToOriginalRange(edgeSizeSliderValue, edgeMin, edgeMax);

    // Reset all nodes and edges to visible before applying the filter
    cy.nodes().forEach(function (node) {
        node.style('display', 'element');
    });

    cy.edges().forEach(function (edge) {
        edge.style('display', 'element');
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

    // After filtering edges, check for nodes with no connected edges
    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        if (connectedEdges.length === 0) {
            node.style('display', 'none');  // Remove node if no connected edges
        }
    });

    // Apply layout after edge filtering
    cy.layout({ name: currentLayout, componentSpacing: 100, nodeRepulsion: 100 }).run();
}

document.getElementById('edge-size-slider').addEventListener('input', function () {
    document.getElementById('edge-size-value').textContent = this.value;
    filterEdgesBySize();
});


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

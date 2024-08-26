// ========================================================
// Input handling
// ========================================================

// const elements = [
//     { data: { id: 'a', label: 'Nanog', annotation: ['hoge', 'hooo'], node_color: 3 } },
//     { data: { id: 'b', label: 'Pou5f1', annotation: 'fuga', node_color: 10 } },
//     { data: { id: 'c', label: 'Sox2', annotation: 'foo', node_color: 1 } },
//     { data: { source: 'a', target: 'b', annotation: 'Foo', edge_size: 0.5 } },
//     { data: { source: 'a', target: 'c', annotation: 'FooBar', edge_size: 1.5 } },
// ];

const elements = (function () {
    const req = new XMLHttpRequest();
    let result = null;
    req.onreadystatechange = function () {
        if (req.readyState === 4 && req.status === 200) {
            result = JSON.parse(req.responseText);
        }
    };
    // req.open("GET", "https://www.md.tsukuba.ac.jp/LabAnimalResCNT/test-tsumugi/network/data/increased_circulating_glucose_level.json", false);
    req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/59593039eb836eb989d4d47102da3c731ba0498e/gist_increased_circulating_glucose_level.json", false);
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

function scaleToOriginalRange(value, minValue, maxValue) {
    // Scale the slider value (1-10) to the original range
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

function scaleToSliderRange(value, minValue, maxValue) {
    // Scale the original range value to the slider value (1-10)
    return 1 + (value - minValue) * 9 / (maxValue - minValue);
}

function getColorForValue(value) {
    // Assumes value is in the range of 1 to 10
    const ratio = (value - 1) / (10 - 1);

    // Gradient from light yellow to orange
    const r1 = 248, g1 = 229, b1 = 140; // Light Yellow
    const r2 = 255, g2 = 140, b2 = 0;   // Orange

    // Linear interpolation
    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return `rgb(${r}, ${g}, ${b})`;
}

function filterElements() {
    const nodeColorSliderValue = parseFloat(document.getElementById('node-color-slider').value);
    const edgeSizeSliderValue = parseFloat(document.getElementById('edge-size-slider').value);

    const nodeThreshold = scaleToOriginalRange(nodeColorSliderValue, nodeMin, nodeMax);
    const edgeThreshold = scaleToOriginalRange(edgeSizeSliderValue, edgeMin, edgeMax);

    // Filter nodes
    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', nodeColor >= nodeThreshold ? 'element' : 'none');
    });

    // Filter edges
    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data('edge_size');
        const sourceNode = cy.getElementById(edge.data('source'));
        const targetNode = cy.getElementById(edge.data('target'));

        // Edge filtering conditions
        if (sourceNode.style('display') === 'element' && targetNode.style('display') === 'element' && edgeSize >= edgeThreshold) {
            edge.style('display', 'element');
        } else {
            edge.style('display', 'none');
        }
    });

    // Hide nodes with degree 0 after filtering edges
    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        if (connectedEdges.length === 0) {
            node.style('display', 'none');
        }
    });

    // Re-run the layout
    cy.layout({ name: 'cose', componentSpacing: 100, nodeRepulsion: 100000 }).run();  // Re-run the currently used layout
}

// Initial slider setup
document.getElementById('node-color-slider').value = 1;
document.getElementById('node-color-value').textContent = 1;

document.getElementById('edge-size-slider').value = 1;
document.getElementById('edge-size-value').textContent = 1;


// ========================================================
// Cytoscape handling
// ========================================================


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
                'font-size': "20px",
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
                'width': 'data(edge_size)',
            }
        }
    ],
    layout: { name: 'cose', }
});


// Event listener for layout change
document.getElementById('layout-dropdown').addEventListener('change', function () {
    const layout = this.value;
    cy.layout({ name: layout }).run();
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

// Initial filtering and node color setup
filterElements();


// ========================================================
// Tooltip handling
// ========================================================

cy.on('mouseover', 'node, edge', function (event) {
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

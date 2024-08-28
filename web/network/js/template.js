// ========================================================
// Input handling
// ========================================================

// const elements = [
//     { data: { id: 'Nanog', label: 'Nanog', annotation: ['hoge', 'hooo'], node_color: 50, marker_id: "MGI:97281" } },
//     { data: { id: 'Pou5f1', label: 'Pou5f1', annotation: 'fuga', node_color: 100, marker_id: "MGI:1352748" } },
//     { data: { id: 'Sox2', label: 'Sox2', annotation: 'foo', node_color: 3, marker_id: "MGI:96217" } },
//     { data: { source: 'Nanog', target: 'Pou5f1', annotation: ['Foo', 'FooBar'], edge_size: 5 } },
//     { data: { source: 'Nanog', target: 'Sox2', annotation: 'FooBar', edge_size: 1 } },
//     { data: { source: 'Sox2', target: 'Pou5f1', annotation: 'FooBar', edge_size: 10 } },
// ];

// const elements = [
//     { data: { id: 'Nanog', label: 'Nanog', annotation: ['hoge', 'hooo'], node_color: 50, } },
//     { data: { id: 'Pou5f1', label: 'Pou5f1', annotation: 'fuga', node_color: 100, } },
//     { data: { id: 'Sox2', label: 'Sox2', annotation: 'foo', node_color: 3, } },
//     { data: { source: 'Nanog', target: 'Pou5f1', annotation: ['Foo', 'FooBar'], edge_size: 5 } },
//     { data: { source: 'Nanog', target: 'Sox2', annotation: 'FooBar', edge_size: 1 } },
//     { data: { source: 'Sox2', target: 'Pou5f1', annotation: 'FooBar', edge_size: 10 } },
// ];

// const map_symbol_to_id = { 'Nanog': 'MGI:97281', 'Pou5f1': 'MGI:1352748', 'Sox2': 'MGI:96217' };

const elements = (function () {
    const req = new XMLHttpRequest();
    let result = null;
    req.onreadystatechange = function () {
        if (req.readyState === 4 && req.status === 200) {
            result = JSON.parse(req.responseText);
        }
    };
    req.open("GET", "https://www.md.tsukuba.ac.jp/LabAnimalResCNT/test-tsumugi/network/data/XXX_snake_case.json", false);

    // req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/b33aa992d7950fbd6d302735f1251d83f554cccb/gist_male_infertility.json", false);
    // req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/33cbe08513d54ef0ca3afc6f1fb1dd12b86c1901/gist_increased_circulating_glucose_level.json", false);

    req.send(null);
    return result;
})();


const map_symbol_to_id = (function () {
    const req = new XMLHttpRequest();
    let result = null;
    req.onreadystatechange = function () {
        if (req.readyState === 4 && req.status === 200) {
            result = JSON.parse(req.responseText);
        }
    };
    // req.open("GET", "https://www.md.tsukuba.ac.jp/LabAnimalResCNT/test-tsumugi/network/data/XXX_snake_case.json", false);

    req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/1481158ce41ef5165be3c0e17d4b83b6d265b783/gist_marker_symbol_accession_id.json", false);
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

const nodeRepulsionMin = 10;
const nodeRepulsionMax = 20000;

function scaleToOriginalRange(value, minValue, maxValue) {
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

function scaleValue(value, minValue, maxValue, minScale, maxScale) {
    // スケール範囲をminScaleとmaxScaleに合わせて変換
    if (minValue == maxValue) {
        return (maxScale + minScale) / 2;
    }
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

let currentNodeRepulsionValue = scaleToOriginalRange(parseFloat(document.getElementById('nodeRepulsion-slider').value), nodeRepulsionMin, nodeRepulsionMax);

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
    layout: { name: currentLayout, nodeRepulsion: currentNodeRepulsionValue }
});

// ========================================================
// Visualization handling
// ========================================================

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

document.getElementById('edge-width-slider').addEventListener('input', function () {
    const edgeWidthScale = this.value;
    document.getElementById('edge-width-value').textContent = this.value;
    cy.style()
        .selector('edge')
        .style('width', function (ele) {
            return scaleValue(ele.data('edge_size'), edgeMin, edgeMax, 0.5, 2) * edgeWidthScale;
        })
        .update();
});

document.getElementById('nodeRepulsion-slider').addEventListener('input', function () {
    currentNodeRepulsionValue = scaleToOriginalRange(parseFloat(this.value), nodeRepulsionMin, nodeRepulsionMax);
    document.getElementById('node-repulsion-value').textContent = this.value;
    cy.layout({ name: currentLayout, nodeRepulsion: currentNodeRepulsionValue }).run();
});

// ========================================================
// Filtering function for nodes (filter-node-slider)
// ========================================================

function filterNodesByColor() {
    const nodeColorSliderValue = parseFloat(document.getElementById('filter-node-slider').value);
    const nodeThreshold = scaleToOriginalRange(nodeColorSliderValue, nodeMin, nodeMax);

    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', nodeColor >= nodeThreshold ? 'element' : 'none');
    });

    cy.layout({ name: currentLayout, nodeRepulsion: currentNodeRepulsionValue }).run();

}

document.getElementById('filter-node-slider').addEventListener('input', function () {
    document.getElementById('node-color-value').textContent = this.value;
    // Check if nodeMin is equal to nodeMax
    if (nodeMin == nodeMax) {
        // Disable slider or just return to prevent any filtering
        return;
    }
    filterNodesByColor();
});

// ========================================================
// Filtering function for edges (filter-edge-slider)
// ========================================================

function filterEdgesBySize() {
    const edgeSizeSliderValue = parseFloat(document.getElementById('filter-edge-slider').value);
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
    cy.layout({ name: currentLayout, nodeRepulsion: currentNodeRepulsionValue }).run();
}

document.getElementById('filter-edge-slider').addEventListener('input', function () {
    document.getElementById('edge-size-value').textContent = this.value;
    filterEdgesBySize();
});

// ========================================================
// Tooltip handling
// ========================================================

cy.on('tap', 'node, edge', function (event) {
    const data = event.target.data();
    let tooltipText = '';

    // Remove any existing tooltips
    document.querySelectorAll('.cy-tooltip').forEach(function (el) {
        el.remove();
    });

    let pos;

    if (event.target.isNode()) {
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(function (anno) { return '・ ' + anno; }).join('<br>')
            : '・ ' + data.annotation;

        // Get the MGI link from the map_symbol_to_id
        const mgiLink = map_symbol_to_id[data.label];
        const message = `<b>Significant Phenotypes of ${data.label} KO mice</b>`;
        const link_to_impc = `https://www.mousephenotype.org/data/genes/${mgiLink}`;

        // Construct the tooltipText with the hyperlink
        tooltipText = `<a href="${link_to_impc}" target="_blank">${message}</a><br>` + annotations;

        // Get position of the tapped node
        pos = event.target.renderedPosition();

    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data('label');
        const targetNode = cy.getElementById(data.target).data('label');
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(function (anno) { return '・ ' + anno; }).join('<br>')
            : '・ ' + data.annotation;

        tooltipText = `<b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs</b><br>` + annotations;

        // Calculate the midpoint of the edge for tooltip positioning
        const sourcePos = cy.getElementById(data.source).renderedPosition();
        const targetPos = cy.getElementById(data.target).renderedPosition();
        pos = {
            x: (sourcePos.x + targetPos.x) / 2,
            y: (sourcePos.y + targetPos.y) / 2
        };
    }

    // Create a tooltip element
    const tooltip = document.createElement('div');
    tooltip.classList.add('cy-tooltip');
    tooltip.innerHTML = tooltipText;
    tooltip.style.position = 'absolute';
    tooltip.style.left = (pos.x + 10) + 'px';  // Position to the right of the element
    tooltip.style.top = (pos.y + 10) + 'px';   // Position slightly below the element
    tooltip.style.padding = '5px';
    tooltip.style.background = 'white';
    tooltip.style.border = '1px solid #ccc';
    tooltip.style.borderRadius = '5px';
    tooltip.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    tooltip.style.zIndex = '1000';
    tooltip.style.cursor = 'move';  // Show the move cursor
    tooltip.style.userSelect = 'text';  // Allow text selection

    // Append the tooltip to the container
    document.querySelector('.cy').appendChild(tooltip);

    // Handle drag events to move the tooltip
    let isDragging = false;
    let offset = { x: 0, y: 0 };

    tooltip.addEventListener('mousedown', function (e) {
        e.stopPropagation(); // Prevent Cytoscape from receiving this event
        isDragging = true;
        const rect = tooltip.getBoundingClientRect();
        offset.x = e.clientX - rect.left;
        offset.y = e.clientY - rect.top;
        tooltip.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function (e) {
        if (isDragging) {
            const containerRect = document.querySelector('.cy').getBoundingClientRect();
            // Adjust the tooltip's position, keeping the offset constant
            tooltip.style.left = (e.clientX - offset.x - containerRect.left) + 'px';
            tooltip.style.top = (e.clientY - offset.y - containerRect.top) + 'px';
        }
    });

    document.addEventListener('mouseup', function () {
        isDragging = false;
        tooltip.style.cursor = 'move';
    });
});

// ========================================================
// Exporter
// ========================================================

document.getElementById('export-png').addEventListener('click', function () {
    const pngContent = cy.png({
        scale: 6.25,   // Scale to achieve 600 DPI
        full: true     // Set to true to include the entire graph, even the offscreen parts
    });

    const a = document.createElement('a');
    a.href = pngContent;
    a.download = 'TSUMUGI_XXX_snake_case.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

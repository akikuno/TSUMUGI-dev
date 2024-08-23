const elements = [
    { data: { id: 'a', label: 'A', annotation: ['hoge', 'hooo'], node_size: 3 } },
    { data: { id: 'b', label: 'B', annotation: 'fuga', node_size: 10 } },
    { data: { id: 'c', label: 'C', annotation: 'foo', node_size: 1 } },
    { data: { source: 'a', target: 'b', annotation: 'Foo', edge_size: 0.5 } },
    { data: { source: 'a', target: 'c', annotation: 'FooBar', edge_size: 1.5 } },
];

const nodeSizes = elements.filter(ele => ele.data.node_size !== undefined).map(ele => ele.data.node_size);
const edgeSizes = elements.filter(ele => ele.data.edge_size !== undefined).map(ele => ele.data.edge_size);

const nodeMin = Math.min(...nodeSizes);
const nodeMax = Math.max(...nodeSizes);
const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);

function scaleValue(value, minValue, maxValue, scaleMin, scaleMax) {
    return scaleMin + (value - minValue) * (scaleMax - scaleMin) / (maxValue - minValue);
}

function getColorForValue(value, minValue, maxValue) {
    const ratio = (value - minValue) / (maxValue - minValue);

    const r1 = 248, g1 = 229, b1 = 140;
    const r2 = 255, g2 = 140, b2 = 0;

    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return 'rgb(' + r + ',' + g + ',' + b + ')';
}

function filterElements() {
    const minNodeSize = parseFloat(document.getElementById('node-size-slider').value);
    const minEdgeSize = parseFloat(document.getElementById('edge-size-slider').value);

    cy.elements().forEach(function (ele) {
        if (ele.isNode()) {
            const nodeSize = ele.data('node_size');
            ele.style('display', nodeSize >= minNodeSize ? 'element' : 'none');
        } else if (ele.isEdge()) {
            const edgeSize = ele.data('edge_size');
            ele.style('display', edgeSize >= minEdgeSize ? 'element' : 'none');
        }
    });
}

elements.forEach(function (ele) {
    if (ele.data.node_size !== undefined) {
        ele.data.node_size = scaleValue(ele.data.node_size, nodeMin, nodeMax, 10, 30);
        ele.style = {
            'background-color': getColorForValue(ele.data.node_size, 10, 30)
        };
    }
    if (ele.data.edge_size !== undefined) {
        ele.data.edge_size = scaleValue(ele.data.edge_size, edgeMin, edgeMax, 0.5, 2);
        ele.style = {
            'line-color': 'gray',
        };
    }
});

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
                'font-family': 'Cabin',
                'width': 'data(node_size)',
                'height': 'data(node_size)',
                'font-size': function (ele) {
                    const size = ele.data('node_size');
                    return Math.max(8, size / 2) + 'px';
                }
            }
        },
        {
            selector: 'edge',
            style: {
                'curve-style': 'bezier',
                'font-family': 'Cabin',
                'text-rotation': 'autorotate',
                'width': 'data(edge_size)',
                'font-size': function (ele) {
                    const size = ele.data('edge_size');
                    return Math.max(8, size / 2) + 'px';
                },
            }
        }
    ],
    layout: { name: 'cose' }
});

document.getElementById('layout-dropdown').addEventListener('change', function () {
    const layout = this.value;
    cy.layout({ name: layout }).run();
});

document.getElementById('node-size-slider').addEventListener('input', filterElements);
document.getElementById('edge-size-slider').addEventListener('input', filterElements);

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
        tooltipText = "<b>Shared phenotypes of " + sourceNode + " and " + targetNode + "</b><br>" + annotations;
    }

    document.querySelector('.tooltip-container').innerHTML = tooltipText;
});

// Initial filtering based on default slider values
filterElements();

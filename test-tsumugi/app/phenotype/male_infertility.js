import { exportGraphAsPNG, exportGraphAsCSV } from '../js/exporter.js';
import { scaleToOriginalRange, scaleValue, getColorForValue } from '../js/value_scaler.js';


// ############################################################################
// Input handler
// ############################################################################


const target_phenotype = 'male_infertility'.replace(/_/g, " ");

const elements = (function () {
    const req = new XMLHttpRequest();
    let result = null;

    try {
        req.open("GET", "../../data/phenotype/male_infertility.json.gz", false);

        req.overrideMimeType("text/plain; charset=x-user-defined"); // バイナリデータとして扱うための設定
        req.send(null);

        if (req.status === 200) {
            // gzipデータをUint8Arrayに変換
            const compressedData = new Uint8Array(
                req.responseText.split("").map(c => c.charCodeAt(0) & 0xff)
            );
            // pakoでデコード
            const decompressedData = pako.ungzip(compressedData, { to: "string" });
            result = JSON.parse(decompressedData);
        } else {
            console.error("HTTP error!! status:", req.status);
        }
    } catch (error) {
        console.error("Failed to load or decode JSON.gz:", error);
    }

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
    req.open("GET", "../../data/marker_symbol_accession_id.json", false);

    req.send(null);
    return result;
})();


// ############################################################################
// 遺伝型・正特異的フィルタリング関数
// ############################################################################

// フィルターフォームの取得
const filterGenotypeForm = document.getElementById('genotype-filter-form');
const filterSexForm = document.getElementById('sex-filter-form');

// フィルタリング関数（遺伝型 + 性別）
function filterElementsByGenotypeAndSex() {
    const checkedGenotypes = Array.from(filterGenotypeForm.querySelectorAll('input:checked')).map(input => input.value);
    const checkedSexs = Array.from(filterSexForm.querySelectorAll('input:checked')).map(input => input.value);

    // console.log("検索キーワード (Genotype):", checkedGenotypes);
    // console.log("検索キーワード (Sex):", checkedSexs);

    let targetElements;

    // もし checkedSexs に Female と Male の両方が含まれていたら、性別のフィルターを無効にし、遺伝型のフィルターのみ適用
    if (checkedSexs.includes("Female") && checkedSexs.includes("Male")) {
        // console.log("性別フィルター無効（遺伝型のみ適用）");
        targetElements = elements;
    } else {
        targetElements = elements.map(item => {
            if (item.data.annotation) {
                const filteredAnnotations = item.data.annotation.filter(annotation => {
                    const sexMatch = checkedSexs.some(sex => annotation.includes(`${sex}`));
                    return sexMatch;
                });

                return { ...item, data: { ...item.data, annotation: filteredAnnotations } };
            }
            return item;
        }).filter(item => item.data.annotation && item.data.annotation.length > 0);
    }

    // 遺伝型フィルターの適用
    let filteredElements = targetElements.map(item => {
        if (item.data.annotation) {
            const filteredAnnotations = item.data.annotation.filter(annotation => {
                const genotypeMatch = checkedGenotypes.some(genotype => annotation.includes(`${genotype}`));
                return genotypeMatch;
            });

            return { ...item, data: { ...item.data, annotation: filteredAnnotations } };
        }
        return item;
    }).filter(item => item.data.annotation && item.data.annotation.length > 0);

    // console.log("標的表現型:", target_phenotype);
    // `target_phenotype` をまったく含まないノードを削除
    filteredElements = filteredElements.filter(item => {
        if (item.data.annotation) {
            return item.data.annotation.some(annotation => annotation.includes(target_phenotype));
        }
        return false;
    }).filter(item => item.data.annotation && item.data.annotation.length > 2); // 3つ以上の表現型を持つノードのみを表示

    // Cytoscape のデータを更新
    cy.elements().remove(); // 既存の要素を削除
    cy.add(filteredElements); // 新しい要素を追加
    filterElements(); // 孤立ノードを削除
}


// フォーム変更時にフィルタリング関数を実行
filterGenotypeForm.addEventListener('change', filterElementsByGenotypeAndSex);
filterSexForm.addEventListener('change', filterElementsByGenotypeAndSex);


// ############################################################################
// Cytoscape Elements handler
// ############################################################################

const nodeSizes = elements.filter(ele => ele.data.node_color !== undefined).map(ele => ele.data.node_color);
const edgeSizes = elements.filter(ele => ele.data.edge_size !== undefined).map(ele => ele.data.edge_size);

const nodeMin = Math.min(...nodeSizes);
const nodeMax = Math.max(...nodeSizes);
const edgeMin = Math.min(...edgeSizes);
const edgeMax = Math.max(...edgeSizes);


function getLayoutOptions() {
    return {
        name: currentLayout,
        nodeRepulsion: nodeRepulsionValue,
        componentSpacing: componentSpacingValue
    };
}

let currentLayout = 'cose';

const nodeRepulsionMin = 1;
const nodeRepulsionMax = 10000;
const componentSpacingMin = 1;
const componentSpacingMax = 200;

let nodeRepulsionValue = scaleToOriginalRange(
    parseFloat(document.getElementById('nodeRepulsion-slider').value),
    nodeRepulsionMin,
    nodeRepulsionMax
);

let componentSpacingValue = scaleToOriginalRange(
    parseFloat(document.getElementById('nodeRepulsion-slider').value),
    componentSpacingMin,
    componentSpacingMax
);

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
    layout: getLayoutOptions()
});


// レイアウトが変更されるか、フィルタリングが実行された際に連結成分を計算する関数
function calculateConnectedComponents() {
    // 表示されている要素のみを取得
    const visibleElements = cy.elements(':visible');

    // 可視状態の要素で連結成分を計算
    const connectedComponents = visibleElements.components();

    let connected_component = connectedComponents.map(component => {
        let componentObject = {};

        // ノードを処理
        component.nodes().forEach(node => {
            const nodeLabel = node.data('label');
            const nodeAnnotations = Array.isArray(node.data('annotation'))
                ? node.data('annotation')
                : [node.data('annotation')]; // annotation が配列でない場合も考慮

            // ノード名をキー、アノテーションを値とするオブジェクトを作成
            componentObject[nodeLabel] = nodeAnnotations;
        });

        return componentObject;
    });

    // 結果をログに出力（デバッグ用）
    // console.log('Connected Components (Formatted):', connected_component);

    // 必要に応じて connected_component を他の場所で利用可能にする
    return connected_component;
}

// レイアウト変更後にイベントリスナーを設定
cy.on('layoutstop', function () {
    calculateConnectedComponents();
});

// ############################################################################
// Control panel handler
// ############################################################################

// --------------------------------------------------------
// Network layout dropdown
// --------------------------------------------------------
document.getElementById('layout-dropdown').addEventListener('change', function () {
    currentLayout = this.value;
    cy.layout({ name: currentLayout }).run();
});

// --------------------------------------------------------
// Initialization and Update of the Slider for Phenotypes similarity
// --------------------------------------------------------
const edgeSlider = document.getElementById('filter-edge-slider');
noUiSlider.create(edgeSlider, {
    start: [1, 10],
    connect: true,
    range: {
        'min': 1,
        'max': 10
    },
    step: 1
});




// --------------------------------------------------------
// Modify the filter function to handle upper and lower bounds
// --------------------------------------------------------

let nodeSliderValues = [1, 10];

function filterElements() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(parseFloat);

    const nodeMinValue = scaleToOriginalRange(nodeSliderValues[0], nodeMin, nodeMax);
    const nodeMaxValue = scaleToOriginalRange(nodeSliderValues[1], nodeMin, nodeMax);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // Filter nodes based on color
    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', (nodeColor >= nodeMinValue && nodeColor <= nodeMaxValue) ? 'element' : 'none');
    });

    // Filter edges based on size
    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data('edge_size');
        const sourceNode = cy.getElementById(edge.data('source'));
        const targetNode = cy.getElementById(edge.data('target'));

        if (sourceNode.style('display') === 'element' && targetNode.style('display') === 'element' &&
            edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue) {
            edge.style('display', 'element');
        } else {
            edge.style('display', 'none');
        }
    });

    // After filtering, remove nodes with no connected visible edges
    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        if (connectedEdges.length === 0) {
            node.style('display', 'none');  // Hide node if no connected edges
        }
    });

    // Reapply layout after filtering
    cy.layout(getLayoutOptions()).run();
}

// --------------------------------------------------------
// Update of the Slider
// --------------------------------------------------------

edgeSlider.noUiSlider.on('update', function (values) {
    const intValues = values.map(value => Math.round(value));
    document.getElementById('edge-size-value').textContent = intValues.join(' - ');
    filterElements();
});




// ############################################################################
// Cytoscape's visualization setting
// ############################################################################

// --------------------------------------------------------
// Slider for Font size
// --------------------------------------------------------
const fontSizeSlider = document.getElementById('font-size-slider');
noUiSlider.create(fontSizeSlider, {
    start: 20,
    connect: [true, false],
    range: {
        'min': 1,
        'max': 50
    },
    step: 1
});
fontSizeSlider.noUiSlider.on('update', function (value) {
    const intValues = Math.round(value);
    document.getElementById('font-size-value').textContent = intValues;
    cy.style().selector('node').style('font-size', intValues + 'px').update();
});

// --------------------------------------------------------
// Slider for Edge width
// --------------------------------------------------------
const edgeWidthSlider = document.getElementById('edge-width-slider');
noUiSlider.create(edgeWidthSlider, {
    start: 5,
    connect: [true, false],
    range: {
        'min': 1,
        'max': 10
    },
    step: 1
});
edgeWidthSlider.noUiSlider.on('update', function (value) {
    const intValues = Math.round(value);
    document.getElementById('edge-width-value').textContent = intValues;
    cy.style().selector('edge').style('width', function (ele) {
        return scaleValue(ele.data('edge_size'), edgeMin, edgeMax, 0.5, 2) * intValues;
    }).update();
});

// --------------------------------------------------------
// Slider for Node repulsion
// --------------------------------------------------------
const nodeRepulsionSlider = document.getElementById('nodeRepulsion-slider');
noUiSlider.create(nodeRepulsionSlider, {
    start: 5,
    connect: [true, false],
    range: {
        'min': 1,
        'max': 10
    },
    step: 1
});
nodeRepulsionSlider.noUiSlider.on('update', function (value) {
    const intValues = Math.round(value);
    nodeRepulsionValue = scaleToOriginalRange(parseFloat(intValues), nodeRepulsionMin, nodeRepulsionMax);
    componentSpacingValue = scaleToOriginalRange(parseFloat(intValues), componentSpacingMin, componentSpacingMax);
    document.getElementById('node-repulsion-value').textContent = intValues;
    cy.layout(getLayoutOptions()).run();
});

// ############################################################################
// Tooltip handling
// ############################################################################

// Show tooltip on tap
cy.on('tap', 'node, edge', function (event) {
    showTooltip(event, cy, map_symbol_to_id);
});


// Hide tooltip when tapping on background
cy.on('tap', function (event) {
    if (event.target === cy) {
        removeTooltips();
    }
});

// ############################################################################
// Exporter
// ############################################################################

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

document.getElementById('export-png').addEventListener('click', exportGraphAsPNG);


// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

document.getElementById('export-csv').addEventListener('click', function () {
    exportGraphAsCSV();
});

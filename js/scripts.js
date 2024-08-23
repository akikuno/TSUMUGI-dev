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
    var req = new XMLHttpRequest();  // XMLHttpRequest オブジェクトを生成する
    var result = null;
    req.onreadystatechange = function () {  // XMLHttpRequest オブジェクトの状態が変化した際に呼び出されるイベントハンドラ
        if (req.readyState == 4 && req.status == 200) {  // サーバーからのレスポンスが完了し、かつ、通信が正常に終了した場合
            result = JSON.parse(req.responseText);  // 取得した JSON をパースしてresultに代入
        }
    };
    req.open("GET", "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/3615e66d75627351f3b3c2300cc27101d46cd749/network.json", false); // HTTPメソッドとアクセスするサーバーのURLを指定
    req.send(null);  // 実際にサーバーへリクエストを送信
    return result;  // パースされたJSONデータを返す
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
    // スライダーの値（1-10）を元の範囲にスケール
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

function scaleToSliderRange(value, minValue, maxValue) {
    // 元の範囲の値をスライダーの値（1-10）にスケール
    return 1 + (value - minValue) * 9 / (maxValue - minValue);
}

function getColorForValue(value) {
    // valueが1から10の範囲であることを前提
    const ratio = (value - 1) / (10 - 1); // 1から10の間での割合

    // ライトイエローからオレンジへのグラデーション
    const r1 = 248, g1 = 229, b1 = 140; // ライトイエロー
    const r2 = 255, g2 = 140, b2 = 0;   // オレンジ

    // 線形補間
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

    // ノードのフィルタリング
    cy.nodes().forEach(function (node) {
        const nodeColor = node.data('node_color');
        node.style('display', nodeColor >= nodeThreshold ? 'element' : 'none');
    });

    // エッジのフィルタリング
    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data('edge_size');
        const sourceNode = cy.getElementById(edge.data('source'));
        const targetNode = cy.getElementById(edge.data('target'));

        // エッジのフィルタリング条件
        if (sourceNode.style('display') === 'element' && targetNode.style('display') === 'element' && edgeSize >= edgeThreshold) {
            edge.style('display', 'element');
        } else {
            edge.style('display', 'none');
        }
    });

    // エッジのフィルタリング後に、次数が0のノードを非表示にする
    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter(edge => edge.style('display') === 'element');
        if (connectedEdges.length === 0) {
            node.style('display', 'none');
        }
    });

    // レイアウトの再実行
    cy.layout({ name: 'cose', componentSpacing: 100, nodeRepulsion: 100000 }).run();  // 現在使用しているレイアウトを再実行
}

// スライダーの初期設定
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
                'width': 10,
                'height': 10,
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


// レイアウト変更のイベントリスナー
document.getElementById('layout-dropdown').addEventListener('change', function () {
    const layout = this.value;
    cy.layout({ name: layout }).run();
});

// スライダーのイベントリスナー
document.getElementById('node-color-slider').addEventListener('input', function () {
    document.getElementById('node-color-value').textContent = this.value;
    filterElements();
});

document.getElementById('edge-size-slider').addEventListener('input', function () {
    document.getElementById('edge-size-value').textContent = this.value;
    filterElements();
});

// 初期フィルタリングとノード色の設定
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

// 初期フィルタリングとノード色の設定
filterElements();

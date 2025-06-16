export function highlightDiseaseAnnotation({ cy, checkboxId = "disease" }) {
    const checkbox = document.getElementById(checkboxId);

    checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
            // チェックされた場合：「**Associated Human Diseases**」を含むノードを赤枠でハイライト
            highlightDiseaseNodes(cy);
        } else {
            // チェックが外された場合：ハイライトをリセット
            resetDiseaseHighlight(cy);
        }
    });
}

export function highlightDiseaseNodes(cy) {
    // 疾患関連ノードを検索してハイライト
    const diseaseNodes = cy.nodes().filter((node) => {
        const nodeData = node.data();
        return checkNodeForDiseaseInfo(nodeData);
    });

    if (diseaseNodes.length > 0) {
        diseaseNodes.addClass("disease-highlight");
        // diseaseNodes.style("border-width", 3);
        // diseaseNodes.style("border-color", "#fc4c00");
    }
}

function resetDiseaseHighlight(cy) {
    // 疾患関連ノードを検索してハイライト
    const diseaseNodes = cy.nodes().filter((node) => {
        const nodeData = node.data();
        return checkNodeForDiseaseInfo(nodeData);
    });

    if (diseaseNodes.length > 0) {
        diseaseNodes.removeClass("disease-highlight");
    }
}

function checkNodeForDiseaseInfo(nodeData) {
    // ツールチップコードを参考に、diseaseフィールドをチェック
    const diseases = Array.isArray(nodeData.disease) ? nodeData.disease : [nodeData.disease];

    // diseasesが存在し、空でない場合は疾患関連ノードとみなす
    // ツールチップでは diseases[0] !== "" の条件で "Associated Human Diseases" を表示している
    if (diseases && diseases.length > 0 && diseases[0] !== "" && diseases[0] !== undefined && diseases[0] !== null) {
        return true;
    }

    return false;
}

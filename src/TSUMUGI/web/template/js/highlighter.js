export function highlightDiseaseAnnotation({ cy, checkboxId = "disease" }) {
    const checkbox = document.getElementById(checkboxId);

    checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
            // When checked, highlight nodes that contain "**Associated Human Diseases**"
            highlightDiseaseNodes(cy);
        } else {
            // When unchecked, remove the highlight
            resetDiseaseHighlight(cy);
        }
    });
}

export function highlightDiseaseNodes(cy) {
    // Find disease-related nodes and highlight them
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
    // Find disease-related nodes and remove highlighting
    const diseaseNodes = cy.nodes().filter((node) => {
        const nodeData = node.data();
        return checkNodeForDiseaseInfo(nodeData);
    });

    if (diseaseNodes.length > 0) {
        diseaseNodes.removeClass("disease-highlight");
    }
}

function checkNodeForDiseaseInfo(nodeData) {
    // Reuse the tooltip logic for checking the disease field
    const diseases = Array.isArray(nodeData.disease) ? nodeData.disease : [nodeData.disease];

    // Treat nodes as disease-related if the diseases array contains a non-empty value
    // Tooltips display "Associated Human Diseases" when diseases[0] !== ""
    if (diseases && diseases.length > 0 && diseases[0] !== "" && diseases[0] !== undefined && diseases[0] !== null) {
        return true;
    }

    return false;
}

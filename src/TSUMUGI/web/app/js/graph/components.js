function getComponentSortKey(component) {
    const labels = component
        .nodes()
        .map((node) => node.data("label") || node.id())
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b));
    return labels[0] || "";
}

export function getOrderedComponents(cy) {
    const visibleElements = cy.elements(":visible");
    const connectedComponents = visibleElements.components();
    return connectedComponents.sort((a, b) => getComponentSortKey(a).localeCompare(getComponentSortKey(b)));
}

export function calculateConnectedComponents(cy) {
    const orderedComponents = getOrderedComponents(cy);

    return orderedComponents.map((component) => {
        let componentObject = {};
        component.nodes().forEach((node) => {
            const nodeLabel = node.data("label");
            const nodePhenotypes = Array.isArray(node.data("phenotype"))
                ? node.data("phenotype")
                : [node.data("phenotype")];
            componentObject[nodeLabel] = nodePhenotypes;
        });
        return componentObject;
    });
}

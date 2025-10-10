export function calculateConnectedComponents(cy) {
    const visibleElements = cy.elements(":visible");
    const connectedComponents = visibleElements.components();

    return connectedComponents.map((component) => {
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

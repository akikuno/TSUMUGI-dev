export function calculateConnectedComponents(cy) {
    const visibleElements = cy.elements(':visible');
    const connectedComponents = visibleElements.components();

    return connectedComponents.map(component => {
        let componentObject = {};
        component.nodes().forEach(node => {
            const nodeLabel = node.data('label');
            const nodeAnnotations = Array.isArray(node.data('annotation'))
                ? node.data('annotation')
                : [node.data('annotation')];
            componentObject[nodeLabel] = nodeAnnotations;
        });
        return componentObject;
    });
}

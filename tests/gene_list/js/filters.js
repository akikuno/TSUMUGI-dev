// Filtering function (genotype + sex)
export function filterElementsByGenotypeAndSex(elements, target_phenotype, cy, filterElements) {
    // Retrieve checkbox states
    const checkedSexs = Array.from(document.querySelectorAll('#sex-filter-form input[type="checkbox"]:checked')).map(
        (input) => input.value,
    );
    const checkedGenotypes = Array.from(
        document.querySelectorAll('#genotype-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    let targetElements;

    // When both "Female" and "Male" are selected, skip the sex filter
    if (checkedSexs.includes("Female") && checkedSexs.includes("Male")) {
        targetElements = elements;
    } else {
        // Apply the sex filter
        targetElements = elements
            .map((item) => {
                if (item.data.annotation) {
                    const filteredAnnotations = item.data.annotation.filter((annotation) =>
                        checkedSexs.some((sex) => annotation.includes(`${sex}`)),
                    );

                    return {
                        ...item,
                        data: { ...item.data, annotation: filteredAnnotations },
                    };
                }
                return item;
            })
            .filter((item) => item.data.annotation && item.data.annotation.length > 0);
    }

    // Apply the genotype filter
    let filteredElements = targetElements
        .map((item) => {
            if (item.data.annotation) {
                const filteredAnnotations = item.data.annotation.filter((annotation) =>
                    checkedGenotypes.some((genotype) => annotation.includes(`${genotype}`)),
                );

                return {
                    ...item,
                    data: { ...item.data, annotation: filteredAnnotations },
                };
            }
            return item;
        })
        .filter((item) => item.data.annotation && item.data.annotation.length > 0);

    // If `target_phenotype` is specified, apply the phenotype filter
    if (target_phenotype) {
        filteredElements = filteredElements
            .filter((item) => item.data.annotation?.some((annotation) => annotation.includes(target_phenotype)))
            .filter((item) => item.data.annotation.length > 2); // Display only nodes with three or more phenotypes
    }

    // Update Cytoscape data
    cy.elements().remove(); // Remove existing elements
    cy.add(filteredElements); // Add new elements
    filterElements(); // Remove isolated nodes and refresh visualization
}

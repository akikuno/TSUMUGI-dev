export function filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterElements) {
    const checkedSexs = Array.from(document.querySelectorAll('#sex-filter-form input[type="checkbox"]:checked')).map(
        (input) => input.value,
    );

    const checkedGenotypes = Array.from(
        document.querySelectorAll('#genotype-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    const checkedLifestages = Array.from(
        document.querySelectorAll('#lifestage-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    const allSexs = ["Female", "Male"];
    const allGenotypes = ["Homo", "Hetero", "Hemi"];
    const allLifestages = ["Embryo", "Early", "Interval", "Late"];

    let filteredElements = elements.map((item) => ({
        ...item,
        data: {
            ...item.data,
            _originalAnnotations: item.data.annotation || [], // 🔁 元の annotation を保持
            annotation: item.data.annotation || [],
        },
    }));

    // 性別フィルター
    if (checkedSexs.length !== allSexs.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.annotation.filter((annotation) =>
                    checkedSexs.some((sex) => annotation.includes(sex)),
                );
                return {
                    ...item,
                    data: { ...item.data, annotation: filtered },
                };
            })
            .filter((item) => item.data.annotation.length > 0);
    }

    // 遺伝型フィルター
    if (checkedGenotypes.length !== allGenotypes.length) {
        filteredElements = filteredElements
            .map((item) => {
                const original = item.data._originalAnnotations;
                const filtered = item.data.annotation.filter((annotation) =>
                    checkedGenotypes.some((gt) => annotation.includes(gt)),
                );
                return {
                    ...item,
                    data: { ...item.data, annotation: filtered },
                };
            })
            .filter((item) => item.data.annotation.length > 0);
    }

    // ライフステージフィルター
    if (checkedLifestages.length !== allLifestages.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.annotation.filter((annotation) =>
                    checkedLifestages.some((stage) => annotation.includes(stage)),
                );
                return {
                    ...item,
                    data: { ...item.data, annotation: filtered },
                };
            })
            .filter((item) => item.data.annotation.length > 0);
    }

    // ✅ 2つ以上の annotation を持つものだけ残す
    filteredElements = filteredElements.filter((item) => item.data.annotation && item.data.annotation.length > 1);

    // 🔁 target_phenotype を復元
    if (target_phenotype) {
        filteredElements = filteredElements.map((item) => {
            const original = item.data._originalAnnotations;
            const restored = original.filter((annotation) => annotation.includes(target_phenotype));

            const merged = [...item.data.annotation, ...restored];
            const unique = Array.from(new Set(merged));

            return {
                ...item,
                data: {
                    ...item.data,
                    annotation: unique,
                },
            };
        });
    }

    // ✅ target_phenotype を含まない要素を除外する
    if (target_phenotype) {
        filteredElements = filteredElements.filter((item) =>
            item.data.annotation.some((anno) => anno.includes(target_phenotype)),
        );
    }

    // Cytoscape更新
    cy.elements().remove();
    cy.add(filteredElements);
    filterElements();
}

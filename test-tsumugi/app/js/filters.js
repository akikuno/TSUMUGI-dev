function filterConnectedComponentsByDisease(cy) {
    // #human-disease-filter-form のチェック状態確認
    const isDiseaseFilterChecked = document.querySelector('#human-disease-filter-form input[type="checkbox"]:checked');
    if (!isDiseaseFilterChecked) return;

    // 全ての連結成分を取得
    const components = cy.elements().components();

    components.forEach((component) => {
        // この連結成分のノードの中に、diseaseが空でないものがあるか？
        const hasDisease = component.nodes().some((node) => {
            const disease = node.data("disease");
            return disease && disease.length > 0;
        });

        // diseaseが空のノードだけで構成されている場合は非表示
        if (!hasDisease) {
            component.remove();
        }
    });
}

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
            _originalPhenotypes: item.data.phenotype || [], // 🔁 元の phenotype を保持
            phenotype: item.data.phenotype || [],
        },
    }));

    // 性別フィルター
    if (checkedSexs.length !== allSexs.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedSexs.some((sex) => phenotype.includes(sex)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // 遺伝型フィルター
    if (checkedGenotypes.length !== allGenotypes.length) {
        filteredElements = filteredElements
            .map((item) => {
                const original = item.data._originalPhenotypes;
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedGenotypes.some((gt) => phenotype.includes(gt)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // ライフステージフィルター
    if (checkedLifestages.length !== allLifestages.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedLifestages.some((stage) => phenotype.includes(stage)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // ✅ 2つ以上の phenotype を持つものだけ残す
    filteredElements = filteredElements.filter((item) => item.data.phenotype && item.data.phenotype.length > 1);

    // 🔁 target_phenotype を復元
    if (target_phenotype) {
        filteredElements = filteredElements.map((item) => {
            const original = item.data._originalPhenotypes;
            const restored = original.filter((phenotype) => phenotype.includes(target_phenotype));

            const merged = [...item.data.phenotype, ...restored];
            const unique = Array.from(new Set(merged));

            return {
                ...item,
                data: {
                    ...item.data,
                    phenotype: unique,
                },
            };
        });
    }

    // ✅ target_phenotype を含まない要素を除外する
    if (target_phenotype) {
        filteredElements = filteredElements.filter((item) =>
            item.data.phenotype.some((anno) => anno.includes(target_phenotype)),
        );
    }

    // Cytoscape更新
    cy.elements().remove();
    cy.add(filteredElements);
    filterElements();

    // ✅ diseaseフィルター適用
    filterConnectedComponentsByDisease(cy);
}

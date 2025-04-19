// フィルタリング関数（遺伝型 + 性別 + ライフステージ）
export function filterElementsByGenotypeAndSex(elements, cy, filterElements) {
    // チェックボックスの状態を取得
    const checkedSexs = Array.from(document.querySelectorAll('#sex-filter-form input[type="checkbox"]:checked')).map(
        (input) => input.value,
    );

    const checkedGenotypes = Array.from(
        document.querySelectorAll('#genotype-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    const checkedLifestages = Array.from(
        document.querySelectorAll('#lifestage-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    let targetElements;

    // "Female" と "Male" の両方が選択された場合、性別フィルターを適用しない
    if (checkedSexs.includes("Female") && checkedSexs.includes("Male")) {
        targetElements = elements;
    } else {
        targetElements = elements
            .map((item) => {
                if (item.data.annotation) {
                    const filteredAnnotations = item.data.annotation.filter((annotation) =>
                        checkedSexs.some((sex) => annotation.includes(sex)),
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

    // 遺伝型フィルター適用
    targetElements = targetElements
        .map((item) => {
            if (item.data.annotation) {
                const filteredAnnotations = item.data.annotation.filter((annotation) =>
                    checkedGenotypes.some((genotype) => annotation.includes(genotype)),
                );
                return {
                    ...item,
                    data: { ...item.data, annotation: filteredAnnotations },
                };
            }
            return item;
        })
        .filter((item) => item.data.annotation && item.data.annotation.length > 0);

    // ライフステージフィルター適用
    targetElements = targetElements
        .map((item) => {
            if (item.data.annotation) {
                const filteredAnnotations = item.data.annotation.filter((annotation) =>
                    checkedLifestages.some((stage) => annotation.includes(stage)),
                );
                return {
                    ...item,
                    data: { ...item.data, annotation: filteredAnnotations },
                };
            }
            return item;
        })
        .filter((item) => item.data.annotation && item.data.annotation.length > 0);

    // Cytoscape のデータを更新
    cy.elements().remove();
    cy.add(targetElements);
    filterElements(); // 孤立ノードなどを削除
}

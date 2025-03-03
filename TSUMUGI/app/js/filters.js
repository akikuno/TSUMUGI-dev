
// フィルタリング関数（遺伝型 + 性別）
export function filterElementsByGenotypeAndSex(elements, target_phenotype, cy, filterElements) {
    let targetElements;

    // "Female" と "Male" の両方が選択された場合、性別フィルターを適用しない
    if (checkedSexs.includes("Female") && checkedSexs.includes("Male")) {
        targetElements = elements;
    } else {
        // 性別フィルター適用
        targetElements = elements.map(item => {
            if (item.data.annotation) {
                const filteredAnnotations = item.data.annotation.filter(annotation =>
                    checkedSexs.some(sex => annotation.includes(`${sex}`))
                );

                return { ...item, data: { ...item.data, annotation: filteredAnnotations } };
            }
            return item;
        }).filter(item => item.data.annotation && item.data.annotation.length > 0);
    }

    // 遺伝型フィルター適用
    let filteredElements = targetElements.map(item => {
        if (item.data.annotation) {
            const filteredAnnotations = item.data.annotation.filter(annotation =>
                checkedGenotypes.some(genotype => annotation.includes(`${genotype}`))
            );

            return { ...item, data: { ...item.data, annotation: filteredAnnotations } };
        }
        return item;
    }).filter(item => item.data.annotation && item.data.annotation.length > 0);

    // `targetPhenotype` が指定されている場合、表現型フィルターを適用
    if (targetPhenotype) {
        filteredElements = filteredElements.filter(item =>
            item.data.annotation?.some(annotation => annotation.includes(target_phenotype))
        ).filter(item => item.data.annotation.length > 2); // 3つ以上の表現型を持つノードのみを表示
    }

    // Cytoscape のデータを更新
    cy.elements().remove(); // 既存の要素を削除
    cy.add(filteredElements); // 新しい要素を追加
    filterElements(); // 孤立ノードを削除し、可視化更新
}

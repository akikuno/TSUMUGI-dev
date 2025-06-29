// ############################################################
// Phenotype Search and Highlight Functions
// ############################################################

// 表現型リストを保持
let allPhenotypes = [];
let selectedPhenotypes = new Set();
let cytoscapeInstance = null;

/**
 * 表現型検索機能を初期化
 * @param {Object} params - 初期化パラメータ
 * @param {Object} params.cy - Cytoscapeインスタンス
 * @param {Array} params.elements - ネットワークデータ要素
 */
export function setupPhenotypeSearch({ cy, elements }) {
    cytoscapeInstance = cy;
    initializePhenotypeSearch(cy);
    setupPhenotypeSearchInput();

    // グローバル関数として定義（HTML内のonclickで使用）
    window.removeSelectedPhenotype = removeSelectedPhenotype;

    // updatePhenotypeHighlight関数をグローバルに公開（他のモジュールから呼び出し可能）
    window.updatePhenotypeHighlight = () => updatePhenotypeHighlight(cy);

    // refreshPhenotypeList関数をグローバルに公開（フィルター変更時に呼び出し可能）
    window.refreshPhenotypeList = () => refreshPhenotypeList();
}

/**
 * 現在表示されている遺伝子から表現型を抽出してリストを作成
 * @param {Object} cy - Cytoscapeインスタンス
 */
function initializePhenotypeSearch(cy) {
    const phenotypeSet = new Set();

    // 現在表示されているノードのみから表現型を抽出
    cy.nodes().forEach((node) => {
        // ノードが表示されているかチェック
        if (node.style("display") !== "none" && !node.hidden()) {
            const nodeData = node.data();
            if (nodeData.phenotype) {
                const phenotypes = Array.isArray(nodeData.phenotype) ? nodeData.phenotype : [nodeData.phenotype];
                phenotypes.forEach((phenotype) => {
                    if (phenotype && phenotype.trim() !== "") {
                        phenotypeSet.add(phenotype.trim());
                    }
                });
            }
        }
    });

    allPhenotypes = Array.from(phenotypeSet).sort();
}

/**
 * 表現型検索入力フィールドのイベントリスナーを設定
 */
function setupPhenotypeSearchInput() {
    const searchInput = document.getElementById("phenotype-search");
    const suggestionsList = document.getElementById("phenotype-suggestions");

    if (!searchInput || !suggestionsList) {
        console.warn("Phenotype search elements not found in DOM");
        return;
    }

    searchInput.addEventListener("input", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            suggestionsList.hidden = true;
            return;
        }

        // 既に選択されているものを除外して検索
        const filteredPhenotypes = allPhenotypes.filter(
            (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
        );

        displayPhenotypeSuggestions(filteredPhenotypes);
    });

    // クリック時に候補を表示
    searchInput.addEventListener("click", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            // 入力が空の場合は全ての表現型を表示（選択済みを除く）
            const availablePhenotypes = allPhenotypes.filter((phenotype) => !selectedPhenotypes.has(phenotype));
            displayPhenotypeSuggestions(availablePhenotypes);
        } else {
            // 入力がある場合は検索結果を表示
            const filteredPhenotypes = allPhenotypes.filter(
                (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
            );
            displayPhenotypeSuggestions(filteredPhenotypes);
        }
    });

    // フォーカス時にも候補を表示
    searchInput.addEventListener("focus", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            // 入力が空の場合は全ての表現型を表示（選択済みを除く）
            const availablePhenotypes = allPhenotypes.filter((phenotype) => !selectedPhenotypes.has(phenotype));
            displayPhenotypeSuggestions(availablePhenotypes);
        }
    });

    // 入力フィールド外をクリックしたら候補を隠す
    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
            suggestionsList.hidden = true;
        }
    });
}

/**
 * 表現型候補リストを表示
 * @param {Array} phenotypes - 表示する表現型のリスト
 */
function displayPhenotypeSuggestions(phenotypes) {
    const suggestionsList = document.getElementById("phenotype-suggestions");
    suggestionsList.innerHTML = "";

    if (phenotypes.length === 0) {
        suggestionsList.hidden = true;
        return;
    }

    // 全て表示（スクロール可能）
    const displayPhenotypes = phenotypes;

    displayPhenotypes.forEach((phenotype) => {
        const li = document.createElement("li");
        li.textContent = phenotype;
        li.addEventListener("click", function () {
            addSelectedPhenotype(phenotype);
            document.getElementById("phenotype-search").value = "";
            suggestionsList.hidden = true;
        });
        suggestionsList.appendChild(li);
    });

    suggestionsList.hidden = false;
}

/**
 * 選択された表現型を追加
 * @param {string} phenotype - 追加する表現型
 */
function addSelectedPhenotype(phenotype) {
    if (selectedPhenotypes.has(phenotype)) return;

    selectedPhenotypes.add(phenotype);
    displaySelectedPhenotypes();

    // グローバルに公開されたupdatePhenotypeHighlight関数を呼び出し
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * 選択された表現型を削除（グローバル関数）
 * @param {string} phenotype - 削除する表現型
 */
function removeSelectedPhenotype(phenotype) {
    selectedPhenotypes.delete(phenotype);
    displaySelectedPhenotypes();

    // グローバルに公開されたupdatePhenotypeHighlight関数を呼び出し
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * 選択された表現型をタグとして表示
 */
function displaySelectedPhenotypes() {
    const container = document.getElementById("selected-phenotypes");
    if (!container) return;

    container.innerHTML = "";

    selectedPhenotypes.forEach((phenotype) => {
        const tag = document.createElement("div");
        tag.className = "selected-phenotype-tag";
        tag.innerHTML = `
            <span class="phenotype-text">${phenotype}</span>
            <button class="remove-btn" onclick="removeSelectedPhenotype('${phenotype.replace(/'/g, "\\'")}')">×</button>
        `;
        container.appendChild(tag);
    });
}

/**
 * 選択された表現型に基づいて遺伝子をハイライト
 * @param {Object} cy - Cytoscapeインスタンス
 */
function updatePhenotypeHighlight(cy) {
    // 既存のハイライトをリセット
    cy.nodes().removeClass("phenotype-highlight");

    if (selectedPhenotypes.size === 0) {
        return; // 何も選択されていない場合は何もしない
    }

    // 選択された表現型を持つ遺伝子をハイライト
    cy.nodes().forEach((node) => {
        const nodeData = node.data();

        if (nodeData.phenotype) {
            const nodePhenotypes = Array.isArray(nodeData.phenotype) ? nodeData.phenotype : [nodeData.phenotype];

            // 選択された表現型のいずれかがノードの表現型リストに含まれているかチェック
            const hasSelectedPhenotype = Array.from(selectedPhenotypes).some((selectedPhenotype) =>
                nodePhenotypes.some(
                    (nodePhenotype) => nodePhenotype && nodePhenotype.trim() === selectedPhenotype.trim(),
                ),
            );

            if (hasSelectedPhenotype) {
                node.addClass("phenotype-highlight");
            }
        }
    });
}

/**
 * 選択された表現型のリストを取得
 * @returns {Set} 選択された表現型のセット
 */
export function getSelectedPhenotypes() {
    return new Set(selectedPhenotypes);
}

/**
 * 表現型選択をクリア
 */
export function clearSelectedPhenotypes() {
    selectedPhenotypes.clear();
    displaySelectedPhenotypes();

    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * フィルター変更時に表現型リストを更新
 */
function refreshPhenotypeList() {
    if (!cytoscapeInstance) return;

    // 現在の検索入力値を保存
    const searchInput = document.getElementById("phenotype-search");
    const currentSearchValue = searchInput ? searchInput.value : "";

    // 表現型リストを再初期化
    initializePhenotypeSearch(cytoscapeInstance);

    // 選択済み表現型のうち、もう存在しないものを削除
    const updatedSelectedPhenotypes = new Set();
    selectedPhenotypes.forEach((phenotype) => {
        if (allPhenotypes.includes(phenotype)) {
            updatedSelectedPhenotypes.add(phenotype);
        }
    });
    selectedPhenotypes = updatedSelectedPhenotypes;

    // 表示を更新
    displaySelectedPhenotypes();

    // 検索中だった場合は候補を更新
    if (searchInput && currentSearchValue.trim().length > 0) {
        const searchTerm = currentSearchValue.toLowerCase().trim();
        const filteredPhenotypes = allPhenotypes.filter(
            (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
        );
        displayPhenotypeSuggestions(filteredPhenotypes);
    }

    // ハイライトを更新
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

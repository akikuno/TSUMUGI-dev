// 検索モードの選択用変数 (初期状態を 'phenotype')
let searchMode = "phenotype";

const geneListPlaceHolder = "Asxl1\r\nRab10\r\nDdx46\r\nAp3b2\r\nKcnma1"; // プレースホルダーとして例を入力

// ====================================================================
// タブ切り替え + searchMode の更新
// ====================================================================
function setSearchMode(mode) {
    searchMode = mode;

    document.getElementById("phenotypeSection").style.display = mode === "phenotype" ? "block" : "none";
    document.getElementById("geneSection").style.display = mode === "gene" ? "block" : "none";
    document.getElementById("geneListSection").style.display = mode === "geneList" ? "block" : "none";

    // タブボタンのスタイル変更
    document.querySelectorAll(".Tab").forEach((tabButton) => {
        tabButton.classList.remove("active-tab");
    });
    document.querySelectorAll(`button[data-tab="${mode}"]`).forEach((tabButton) => {
        tabButton.classList.add("active-tab");
    });

    // 入力欄の初期化
    document.querySelectorAll('input[type="text"], textarea').forEach((input) => {
        input.value = "";
    });
    document.querySelectorAll("ul.suggestions").forEach((ul) => {
        ul.innerHTML = "";
    });

    // Gene List のタブが押されたときにプレースホルダーを設定
    const geneListTextarea = document.getElementById("geneList");
    if (mode === "geneList") {
        geneListTextarea.value = geneListPlaceHolder;
    }

    // Submit ボタンの切り替え
    const submitBtn = document.getElementById("submitBtn");
    const submitBtnList = document.getElementById("submitBtn_List");

    submitBtn.style.display = mode === "geneList" ? "none" : "inline-block";
    submitBtnList.style.display = mode === "geneList" ? "inline-block" : "none";

    // 各モードに応じて Submit ボタンを無効化して初期化
    if (mode === "geneList") {
        submitBtnList.disabled = true;
    } else {
        submitBtn.disabled = true;
    }

    if (mode === "geneList") {
        checkGeneListInput();
    } else {
        checkValidInput();
    }
}

// Gene Listが空の場合、Submitボタンを無効化する
function checkGeneListInput() {
    const geneListTextarea = document.getElementById("geneList");
    const submitBtnList = document.getElementById("submitBtn_List");

    if (geneListTextarea.value.trim() === "") {
        submitBtnList.disabled = true;
    } else {
        submitBtnList.disabled = false;
    }
}

// 初期表示
setSearchMode("phenotype");

// タブボタンのクリックイベント
document.querySelectorAll(".Tab").forEach((button) => {
    button.addEventListener("click", () => setSearchMode(button.dataset.tab));
});

// Gene List のテキストエリアが変更されたらボタンを更新
document.getElementById("geneList").addEventListener("input", checkGeneListInput);

// ====================================================================
// Fetch JSON data from the URL and assign to phenotypes
// ====================================================================

const URL_MP_TERMS = "./data/available_mp_terms.json";
const URL_GENE_SYMBOLS = "./data/available_gene_symbols.txt";

// データ取得の完了を管理する Promise
let phenotypesLoaded = fetch(URL_MP_TERMS)
    .then((response) => response.json())
    .then((data) => {
        phenotypes = data;
    })
    .catch((error) => console.error("Error fetching phenotypes:", error));

let geneSymbolsLoaded = fetch(URL_GENE_SYMBOLS)
    .then((response) => response.text())
    .then((data) => {
        geneSymbols = data.split("\n").reduce((acc, symbol) => {
            acc[symbol.trim()] = null;
            return acc;
        }, {});
    })
    .catch((error) => console.error("Error fetching gene symbols:", error));

// 両方のデータがロードされたことを確認する関数
async function ensureDataLoaded() {
    await Promise.all([phenotypesLoaded, geneSymbolsLoaded]);
}

// ====================================================================
// Input handling
// ====================================================================

// --------------------------------------------------------------------
// 入力内容に基づいた検索候補を表示する
// --------------------------------------------------------------------

async function handleInput(event) {
    await ensureDataLoaded(); // データのロードを保証

    const userInput = event.target.value.toLowerCase();
    const suggestionList =
        searchMode === "phenotype"
            ? document.getElementById("phenotypeSuggestions")
            : document.getElementById("geneSuggestions");

    const submitButton = document.getElementById("submitBtn");

    if (!submitButton) {
        console.error(`submitButton not found`);
        return;
    }

    suggestionList.innerHTML = "";

    let isValidSelection = false;
    if (userInput) {
        const dataDictionary = searchMode === "phenotype" ? phenotypes : geneSymbols;
        let matchingCandidates = Object.keys(dataDictionary)
            .map((candidate) => ({
                text: candidate,
                score: wordMatchScore(userInput, candidate),
            }))
            .sort((a, b) => b.score - a.score)
            .filter((candidate) => candidate.score > 0)
            .slice(0, 10);

        matchingCandidates.forEach((candidate) => {
            const listItem = document.createElement("li");
            listItem.textContent = candidate.text;
            listItem.addEventListener("click", function () {
                event.target.value = candidate.text;
                suggestionList.innerHTML = "";
                checkValidInput();
            });
            suggestionList.appendChild(listItem);
        });

        isValidSelection = matchingCandidates.some((candidate) => candidate.text.toLowerCase() === userInput);
    }

    submitButton.disabled = !isValidSelection;
}

// --------------------------------------------------------------------
// 入力の有効性を確認する関数
// --------------------------------------------------------------------
async function checkValidInput() {
    await ensureDataLoaded();

    const userInput =
        searchMode === "phenotype" ? document.getElementById("phenotype") : document.getElementById("gene");

    let isEmptyInput = userInput.value.trim() === "";

    let isValidSelection = false;
    if (searchMode === "phenotype") {
        isValidSelection = phenotypes.hasOwnProperty(userInput.value);
    } else if (searchMode === "gene") {
        isValidSelection = geneSymbols.hasOwnProperty(userInput.value);
    }

    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = !isValidSelection || isEmptyInput;
}

// --------------------------------------------------------------------
// データ取得後にイベントリスナーを登録
// --------------------------------------------------------------------
ensureDataLoaded().then(() => {
    document.getElementById("phenotype").addEventListener("input", handleInput);
    document.getElementById("gene").addEventListener("input", handleInput);
    document.getElementById("phenotype").addEventListener("blur", checkValidInput);
    document.getElementById("gene").addEventListener("blur", checkValidInput);
});

// ====================================================================
// フォームで選択された表現型に対応する詳細ページを新しいタブで表示する
// ====================================================================
function handleFormSubmit(event) {
    event.preventDefault();

    const mode = searchMode;

    // geneListのときには、直接関数を実行を取得
    if (mode === "geneList") {
        fetchGeneData(); // 🔥 ここで直接呼び出す
        return;
    }

    // phenotype / gene のときには、特定のページを出力
    const userInput = mode === "phenotype" ? document.getElementById("phenotype") : document.getElementById("gene");
    const submitBtn = document.getElementById("submitBtn");
    const selectedData = mode === "phenotype" ? phenotypes[userInput.value] : userInput.value;
    const path = mode === "phenotype" ? "phenotype" : "genesymbol";

    if (!submitBtn.disabled) {
        window.open(`app/${path}/${selectedData}.html`, "_blank");
    }
}

// フォームの submit イベントを監視
document.getElementById("searchForm").addEventListener("submit", handleFormSubmit);

// ====================================================================
// 入力された文字列との類似性スコアを計算
// ====================================================================

function jaroWinkler(s1, s2) {
    const m = 0.1;
    const scalingFactor = 0.1;
    const s1Len = s1.length;
    const s2Len = s2.length;

    if (s1Len === 0 || s2Len === 0) return 0;

    const matchWindow = Math.floor(Math.max(s1Len, s2Len) / 2) - 1;
    const s1Matches = new Array(s1Len).fill(false);
    const s2Matches = new Array(s2Len).fill(false);
    let matches = 0;

    for (let i = 0; i < s1Len; i++) {
        const start = Math.max(0, i - matchWindow);
        const end = Math.min(i + matchWindow + 1, s2Len);

        for (let j = start; j < end; j++) {
            if (s2Matches[j]) continue;
            if (s1[i] !== s2[j]) continue;
            s1Matches[i] = true;
            s2Matches[j] = true;
            matches++;
            break;
        }
    }

    if (matches === 0) return 0;

    let transpositions = 0;
    let k = 0;

    for (let i = 0; i < s1Len; i++) {
        if (!s1Matches[i]) continue;
        while (!s2Matches[k]) k++;
        if (s1[i] !== s2[k]) transpositions++;
        k++;
    }

    transpositions /= 2;

    const jaroScore = (matches / s1Len + matches / s2Len + (matches - transpositions) / matches) / 3;

    let prefixLength = 0;
    for (let i = 0; i < Math.min(4, s1Len, s2Len); i++) {
        if (s1[i] === s2[i]) prefixLength++;
        else break;
    }

    return jaroScore + prefixLength * scalingFactor * (1 - jaroScore);
}

function wordMatchScore(term1, term2) {
    const term1Words = term1.split(" ").filter(Boolean);
    const term2Words = term2.split(" ").filter(Boolean);
    let score = 0;

    term1Words.forEach((word1) => {
        let maxScore = 0;
        term2Words.forEach((word2) => {
            const similarity = jaroWinkler(word1.toLowerCase(), word2.toLowerCase());
            maxScore = Math.max(maxScore, similarity);
        });

        score += maxScore;
    });

    return score;
}

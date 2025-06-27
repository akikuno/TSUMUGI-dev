export function setupGeneSearch({
    cy,
    inputId = "gene-search",
    listId = "suggestions",
    // buttonId = "search-button",
}) {
    const input = document.getElementById(inputId);
    const suggestionsList = document.getElementById(listId);

    // 🔍 共通の検索処理を関数にまとめる
    function performSearch(query) {
        const normalized = query.trim().toLowerCase();
        const matchedNode = cy.nodes().filter((node) => node.data("label").toLowerCase() === normalized);

        if (matchedNode.length > 0) {
            matchedNode.addClass("gene-highlight");
            cy.center(matchedNode);
            cy.animate({
                center: { eles: matchedNode },
                zoom: 5,
                duration: 500,
            });
        } else {
            alert("Gene not found in the network.");
        }
    }

    // 🔍 候補を表示する共通関数
    function showSuggestions(query = "") {
        const normalizedQuery = query.trim().toLowerCase();
        suggestionsList.innerHTML = "";

        const visibleLabels = cy
            .nodes()
            .filter((n) => n.style("display") !== "none")
            .map((n) => n.data("label"));

        const matched = visibleLabels
            .filter((label) => (normalizedQuery ? label.toLowerCase().includes(normalizedQuery) : true))
            .sort()
            .slice(0, 10);

        if (matched.length === 0) {
            suggestionsList.hidden = true;
            return;
        }

        matched.forEach((label) => {
            const li = document.createElement("li");
            li.textContent = label;

            // ✅ 候補をクリックした時に検索実行
            li.addEventListener("mousedown", () => {
                input.value = label;
                suggestionsList.hidden = true;
                performSearch(label); // 🔥 検索発火
            });

            suggestionsList.appendChild(li);
        });

        suggestionsList.hidden = false;
    }

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();

        if (!query) {
            suggestionsList.hidden = true;
            return;
        }

        showSuggestions(query);
    });

    // クリック時に候補を表示
    input.addEventListener("click", () => {
        const query = input.value.trim().toLowerCase();
        showSuggestions(query);
    });

    // フォーカス時にも候補を表示
    input.addEventListener("focus", () => {
        const query = input.value.trim().toLowerCase();
        showSuggestions(query);
    });

    input.addEventListener("blur", () => {
        setTimeout(() => {
            suggestionsList.hidden = true;
        }, 100);
    });
}

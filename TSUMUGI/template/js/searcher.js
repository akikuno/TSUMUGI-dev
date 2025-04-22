export function setupGeneSearch({ cy, inputId = "gene-search", listId = "suggestions", buttonId = "search-button" }) {
    const input = document.getElementById(inputId);
    const suggestionsList = document.getElementById(listId);

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        suggestionsList.innerHTML = "";

        if (!query) {
            suggestionsList.hidden = true;
            return;
        }

        // いま現在表示されているノードだけに限定
        const visibleLabels = cy
            .nodes()
            .filter((n) => n.style("display") !== "none")
            .map((n) => n.data("label"));

        const matched = visibleLabels.filter((label) => label.toLowerCase().includes(query)).slice(0, 10);

        if (matched.length === 0) {
            suggestionsList.hidden = true;
            return;
        }

        matched.forEach((label) => {
            const li = document.createElement("li");
            li.textContent = label;
            li.addEventListener("mousedown", () => {
                input.value = label;
                suggestionsList.hidden = true;
            });
            suggestionsList.appendChild(li);
        });

        suggestionsList.hidden = false;
    });

    // 入力欄からフォーカスを外したら非表示
    input.addEventListener("blur", () => {
        setTimeout(() => {
            suggestionsList.hidden = true;
        }, 100);
    });

    document.getElementById(buttonId).addEventListener("click", () => {
        const query = input.value.trim().toLowerCase();

        // すべてのノードのハイライトをリセット
        cy.nodes().forEach((node) => {
            node.style("border-width", 0);
            node.style("border-color", "transparent");
        });

        // 遺伝子名でノードを検索し、見つけたらハイライト
        const matchedNode = cy.nodes().filter((node) => node.data("label").toLowerCase() === query);
        if (matchedNode.length > 0) {
            matchedNode.style("border-width", 3);
            matchedNode.style("border-color", "#fc4c00");

            // Zoom in and center with animation
            cy.center(matchedNode);
            cy.animate({
                center: { eles: matchedNode },
                zoom: 5,
                duration: 500,
            });
        } else {
            alert("Gene not found in the network.");
        }
    });
}

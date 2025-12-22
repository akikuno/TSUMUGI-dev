export function setupGeneSearch({
    cy,
    inputId = "gene-search",
    listId = "suggestions",
    // buttonId = "search-button",
}) {
    const input = document.getElementById(inputId);
    const suggestionsList = document.getElementById(listId);

    // Shared helper that performs the gene search
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

    // Shared helper that renders suggestion items
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

            // Trigger a search when the suggestion is clicked
            li.addEventListener("mousedown", () => {
                input.value = label;
                suggestionsList.hidden = true;
                performSearch(label); // Fire the search immediately
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

    // Show suggestions on click
    input.addEventListener("click", () => {
        const query = input.value.trim().toLowerCase();
        showSuggestions(query);
    });

    // Show suggestions when the field gains focus
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

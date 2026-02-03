// Track which search mode is active (defaults to 'phenotype')
let searchMode = "phenotype";

const geneListPlaceHolder = "Trappc11\r\nRab10\r\nInts8\r\nFah\r\nSox4"; // Example content for the placeholder

// ====================================================================
// Handle tab switching and keep searchMode in sync
// ====================================================================
function setSearchMode(mode) {
    searchMode = mode;

    document.getElementById("phenotypeSection").style.display = mode === "phenotype" ? "block" : "none";
    document.getElementById("geneSection").style.display = mode === "gene" ? "block" : "none";
    document.getElementById("geneListSection").style.display = mode === "geneList" ? "block" : "none";

    // Update tab button styles
    document.querySelectorAll(".Tab").forEach((tabButton) => {
        tabButton.classList.remove("active-tab");
    });
    document.querySelectorAll(`button[data-tab="${mode}"]`).forEach((tabButton) => {
        tabButton.classList.add("active-tab");
    });

    // Reset all input fields
    document.querySelectorAll('input[type="text"], textarea').forEach((input) => {
        input.value = "";
    });
    document.querySelectorAll("ul.suggestions").forEach((ul) => {
        ul.innerHTML = "";
    });

    // Prefill the textarea when the Gene List tab is selected
    const geneListTextarea = document.getElementById("geneList");
    if (mode === "geneList") {
        geneListTextarea.value = geneListPlaceHolder;
    }

    // Toggle the correct submit button
    const submitBtn = document.getElementById("submitBtn");
    const submitBtnList = document.getElementById("submitBtn_List");

    submitBtn.style.display = mode === "geneList" ? "none" : "inline-block";
    submitBtnList.style.display = mode === "geneList" ? "inline-block" : "none";

    // Reset the submit buttons according to the active mode
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

// Disable the submit button when the Gene List textarea is empty
function checkGeneListInput() {
    const geneListTextarea = document.getElementById("geneList");
    const submitBtnList = document.getElementById("submitBtn_List");

    if (geneListTextarea.value.trim() === "") {
        submitBtnList.disabled = true;
    } else {
        submitBtnList.disabled = false;
    }
}

// ====================================================================
// Fetch JSON data from the URL and assign to phenotypes
// ====================================================================

const URL_MP_TERMS = "./data/available_mp_terms.json";
const URL_GENE_SYMBOLS = "./data/available_gene_symbols.txt";

// Track when loading the supporting data completes
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

// Initialize with the phenotype search mode
setSearchMode("phenotype");

// Attach click handlers to the tab buttons
document.querySelectorAll(".Tab").forEach((button) => {
    button.addEventListener("click", () => setSearchMode(button.dataset.tab));
});

// Update the button whenever the Gene List textarea changes
document.getElementById("geneList").addEventListener("input", checkGeneListInput);

// Helper that waits for all prerequisite data to load
async function ensureDataLoaded() {
    await Promise.all([phenotypesLoaded, geneSymbolsLoaded]);
}

// ====================================================================
// Input handling
// ====================================================================

// --------------------------------------------------------------------
// Display search suggestions based on the user's input
// --------------------------------------------------------------------

async function handleInput(event) {
    await ensureDataLoaded(); // Ensure reference data has finished loading

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
// Validate the current input field
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
// Register input listeners once the datasets are ready
// --------------------------------------------------------------------
ensureDataLoaded().then(() => {
    document.getElementById("phenotype").addEventListener("input", handleInput);
    document.getElementById("gene").addEventListener("input", handleInput);
    document.getElementById("phenotype").addEventListener("blur", checkValidInput);
    document.getElementById("gene").addEventListener("blur", checkValidInput);
});

// ====================================================================
// Open the detail page that corresponds to the form selection in a new tab
// ====================================================================
function handleFormSubmit(event) {
    event.preventDefault();

    const rawMode = searchMode;
    const mode = rawMode === "gene" ? "genesymbol" : rawMode === "geneList" ? "genelist" : rawMode;

    // Run the Gene List workflow directly
    if (rawMode === "geneList") {
        fetchGeneData(); // Trigger immediately for gene lists
        return;
    }

    // For phenotype/gene searches, navigate to the dedicated page
    const userInput = mode === "phenotype" ? document.getElementById("phenotype") : document.getElementById("gene");
    const submitBtn = document.getElementById("submitBtn");
    const selectedData = mode === "phenotype" ? phenotypes[userInput.value] : userInput.value;

    if (!submitBtn.disabled) {
        const query = new URLSearchParams({
            mode,
            name: selectedData,
            title: userInput.value,
        });
        window.open(`app/viewer.html?${query.toString()}`, "_blank");
    }
}

// Listen for the form's submit event
document.getElementById("searchForm").addEventListener("submit", handleFormSubmit);

// ====================================================================
// Calculate similarity scores between the input strings
// ====================================================================

function jaroWinkler(s1, s2) {
    const m = 0.1;
    const scalingFactor = 0.1;
    const s1Len = s1.length;
    const s2Len = s2.length;

    if (s1Len === 0 || s2Len === 0) return 0;

    const matchWindow = Math.max(0, Math.floor(Math.max(s1Len, s2Len) / 2) - 1);
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

// ====================================================================
// Info Tooltip Functionality
// ====================================================================

// Initialize tooltips when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    // Handle tooltip click interactions for mobile devices
    const tooltipIcons = document.querySelectorAll(".info-tooltip-icon");

    tooltipIcons.forEach((icon) => {
        icon.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            const container = this.parentElement;
            container.classList.toggle("active");

            // Close other active tooltips
            document.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
                if (el !== container) {
                    el.classList.remove("active");
                }
            });
        });
    });

    // Close tooltips when clicking outside
    document.addEventListener("click", function () {
        document.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
            el.classList.remove("active");
        });
    });
});

// Variable that tracks the selected search mode (default 'phenotype')
let searchMode = 'phenotype';

// ====================================================================
// Tab switching plus updating searchMode
// ====================================================================
function setSearchMode(mode) {
    searchMode = mode;

    document.getElementById('phenotypeSection').style.display = mode === 'phenotype' ? 'block' : 'none';
    document.getElementById('geneSection').style.display = mode === 'gene' ? 'block' : 'none';
    document.getElementById('geneListSection').style.display = mode === 'geneList' ? 'block' : 'none';

    // Update tab button styles
    document.querySelectorAll('.Tab').forEach(tabButton => {
        tabButton.classList.remove('active-tab');
    });
    document.querySelectorAll(`button[data-tab="${mode}"]`).forEach(tabButton => {
        tabButton.classList.add('active-tab');
    });

    // Reset input fields
    document.querySelectorAll('input[type="text"], textarea').forEach(input => {
        input.value = '';
    });
    document.querySelectorAll('ul.suggestions').forEach(ul => {
        ul.innerHTML = '';
    });

    // Set placeholder content when the Gene List tab is selected
    const geneListTextarea = document.getElementById("geneList");
    if (mode === 'geneList') {
        geneListTextarea.value = "Asxl1\nRab10\nDdx46";  // Provide sample text as a placeholder
    } else {
        geneListTextarea.value = '';  // Clear it for other tabs
    }

    // Toggle Submit buttons
    document.getElementById('submitBtn').style.display = mode === 'geneList' ? 'none' : 'inline-block';
    document.getElementById('submitBtn_List').style.display = mode === 'geneList' ? 'inline-block' : 'none';

    // Run the Gene List input validation
    checkGeneListInput();
}

// Validate Gene List input and toggle button enabled state
function checkGeneListInput() {
    const geneListTextarea = document.getElementById("geneList");
    const submitBtnList = document.getElementById("submitBtn_List");

    if (geneListTextarea.value.trim() === "") {
        submitBtnList.disabled = true;
    } else {
        submitBtnList.disabled = false;
    }
}

// Initial display
setSearchMode('phenotype');

// Tab button click events
document.querySelectorAll('.Tab').forEach(button => {
    button.addEventListener('click', () => setSearchMode(button.dataset.tab));
});

// Update the button when the Gene List textarea changes
document.getElementById("geneList").addEventListener("input", checkGeneListInput);

// ====================================================================
// Fetch JSON data from the URL and assign to phenotypes
// ====================================================================

/* REMOVE_THIS_LINE
const URL_MP_TERMS = "./data/available_mp_terms.json";
const URL_GENE_SYMBOLS = "./data/available_gene_symbols.txt";
REMOVE_THIS_LINE */

const URL_MP_TERMS = "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/1fc723ee0ba29a7162fd56394f2d30751d752e4c/gist_available_mp_terms.json"; // REMOVE_THIS_LINE
const URL_GENE_SYMBOLS = "https://gist.githubusercontent.com/akikuno/831ec21615501cc7bd1d381c5e56ebd2/raw/63468d6537120107ddf77568e5dabaaf59044902/gist_available_gene_symbols.txt"; // REMOVE_THIS_LINE

// Promise that tracks data fetch completion
let phenotypesLoaded = fetch(URL_MP_TERMS)
    .then(response => response.json())
    .then(data => {
        phenotypes = data;
    })
    .catch(error => console.error('Error fetching phenotypes:', error));

let geneSymbolsLoaded = fetch(URL_GENE_SYMBOLS)
    .then(response => response.text())
    .then(data => {
        geneSymbols = data.split('\n').reduce((acc, symbol) => {
            acc[symbol.trim()] = null;
            return acc;
        }, {});
    })
    .catch(error => console.error('Error fetching gene symbols:', error));

// Function to ensure both data sources are loaded
async function ensureDataLoaded() {
    await Promise.all([phenotypesLoaded, geneSymbolsLoaded]);
}

// ====================================================================
// Input handling
// ====================================================================

// --------------------------------------------------------------------
// Show search suggestions based on the input
// --------------------------------------------------------------------

async function handleInput(event) {
    await ensureDataLoaded(); // Ensure the data has loaded

    const userInput = event.target.value.toLowerCase();
    const suggestionList = searchMode === 'phenotype'
        ? document.getElementById('phenotypeSuggestions')
        : document.getElementById('geneSuggestions');

    const submitButton = document.getElementById('submitBtn');

    if (!submitButton) {
        console.error(`submitButton not found`);
        return;
    }

    suggestionList.innerHTML = '';

    let isValidSelection = false;
    if (userInput) {
        const dataDictionary = searchMode === 'phenotype' ? phenotypes : geneSymbols;
        let matchingCandidates = Object.keys(dataDictionary)
            .map(candidate => ({
                text: candidate,
                score: wordMatchScore(userInput, candidate)
            }))
            .sort((a, b) => b.score - a.score)
            .filter(candidate => candidate.score > 0)
            .slice(0, 10);

        matchingCandidates.forEach(candidate => {
            const listItem = document.createElement('li');
            listItem.textContent = candidate.text;
            listItem.addEventListener('click', function () {
                event.target.value = candidate.text;
                suggestionList.innerHTML = '';
                checkValidInput();
            });
            suggestionList.appendChild(listItem);
        });

        isValidSelection = matchingCandidates.some(candidate => candidate.text.toLowerCase() === userInput);
    }

    submitButton.disabled = !isValidSelection;
}


// --------------------------------------------------------------------
// Function to validate the current input
// --------------------------------------------------------------------
async function checkValidInput() {
    await ensureDataLoaded();

    const userInput = searchMode === 'phenotype'
        ? document.getElementById('phenotype')
        : document.getElementById('gene');

    const submitBtn = document.getElementById('submitBtn');

    let isValidSelection = false;
    if (searchMode === 'phenotype') {
        isValidSelection = phenotypes.hasOwnProperty(userInput.value);
    } else if (searchMode === 'gene') {
        isValidSelection = geneSymbols.hasOwnProperty(userInput.value);
    }
    // console.log(`isValidSelection: ${isValidSelection}`);
    submitBtn.disabled = !isValidSelection;
}


// --------------------------------------------------------------------
// Register event listeners after the data loads
// --------------------------------------------------------------------
ensureDataLoaded().then(() => {
    document.getElementById('phenotype').addEventListener('input', handleInput);
    document.getElementById('gene').addEventListener('input', handleInput);
    document.getElementById('phenotype').addEventListener('blur', checkValidInput);
    document.getElementById('gene').addEventListener('blur', checkValidInput);
});

// ====================================================================
// Open a detail page for the selected phenotype in a new tab
// ====================================================================
function handleFormSubmit(event) {
    event.preventDefault();

    const mode = searchMode;  // Grab the latest searchMode
    const userInput = mode === 'phenotype' ? document.getElementById('phenotype') : document.getElementById('gene');
    const submitBtn = document.getElementById('submitBtn');
    const selectedData = mode === 'phenotype' ? phenotypes[userInput.value] : userInput.value;
    const path = mode === 'phenotype' ? 'phenotype' : 'genesymbol';

    // console.log(`Submitting form with mode: ${mode}`);
    // console.log(`path: ${path}`);
    // console.log(`name: ${selectedData}`);

    if (!submitBtn.disabled) {
        window.open(`app/${path}/${selectedData}.html`, '_blank');
    }
}

// Listen for the form submit event
document.getElementById('searchForm').addEventListener('submit', handleFormSubmit);

// ====================================================================
// Calculate similarity scores with the provided strings
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

    const jaroScore = ((matches / s1Len) + (matches / s2Len) + ((matches - transpositions) / matches)) / 3;

    let prefixLength = 0;
    for (let i = 0; i < Math.min(4, s1Len, s2Len); i++) {
        if (s1[i] === s2[i]) prefixLength++;
        else break;
    }

    return jaroScore + (prefixLength * scalingFactor * (1 - jaroScore));
}

function wordMatchScore(term1, term2) {
    const term1Words = term1.split(' ').filter(Boolean);
    const term2Words = term2.split(' ').filter(Boolean);
    let score = 0;

    term1Words.forEach(word1 => {
        let maxScore = 0;
        term2Words.forEach(word2 => {
            const similarity = jaroWinkler(word1.toLowerCase(), word2.toLowerCase());
            maxScore = Math.max(maxScore, similarity);
        });

        score += maxScore;
    });

    return score;
}

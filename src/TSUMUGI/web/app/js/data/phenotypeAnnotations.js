const PHENOTYPE_GENOTYPES = new Set(["Homo", "Hetero", "Hemi"]);
const PHENOTYPE_METADATA_VALUES = new Set([
    ...PHENOTYPE_GENOTYPES,
    "Embryo",
    "Early",
    "Interval",
    "Late",
    "Female",
    "Male",
]);

/**
 * Return phenotype annotations as a non-empty array.
 * @param {string|string[]|null|undefined} value - Phenotype annotation value
 * @returns {string[]} Phenotype annotations
 */
export function normalizePhenotypes(value) {
    if (Array.isArray(value)) return value.filter(Boolean);
    return value ? [value] : [];
}

/**
 * Remove a generated genotype, life-stage, and sex suffix from a phenotype annotation.
 * Parenthetical text is preserved unless the suffix starts with a known genotype and
 * every comma-separated value is known phenotype metadata.
 * @param {string} annotation - Phenotype annotation
 * @returns {string} Phenotype term name
 */
export function getPhenotypeTermName(annotation) {
    const text = String(annotation || "").trim();
    const suffixMatch = text.match(/^(.*)\s+\(([^()]*)\)$/);
    if (!suffixMatch) return text;

    const metadataValues = suffixMatch[2]
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
    const isGeneratedMetadata =
        metadataValues.length > 0 &&
        PHENOTYPE_GENOTYPES.has(metadataValues[0]) &&
        metadataValues.every((value) => PHENOTYPE_METADATA_VALUES.has(value));

    return isGeneratedMetadata ? suffixMatch[1].trim() : text;
}

/**
 * Return phenotype term names without generated metadata.
 * @param {string|string[]|null|undefined} value - Phenotype annotations
 * @returns {string[]} Phenotype term names
 */
export function getPhenotypeTermNames(value) {
    return normalizePhenotypes(value)
        .map((annotation) => getPhenotypeTermName(annotation))
        .filter(Boolean);
}

/**
 * Return whether any phenotype annotation matches a selected phenotype term.
 * @param {string|string[]|null|undefined} value - Phenotype annotations
 * @param {Set<string>|string[]} selectedPhenotypes - Selected phenotype terms
 * @returns {boolean} Whether a selected phenotype is present
 */
export function hasSelectedPhenotype(value, selectedPhenotypes) {
    const selected =
        selectedPhenotypes instanceof Set ? selectedPhenotypes : new Set(selectedPhenotypes || []);
    return getPhenotypeTermNames(value).some((phenotype) => selected.has(phenotype));
}

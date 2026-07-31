# TSUMUGI FAQ

## Network Visualization

### Q: What does the 1–100 Effect size value mean?

**A:** It is a page-specific display value, not the raw IMPC effect size. TSUMUGI takes the absolute effect size, applies a `log1p` transformation, and rescales the values for the target phenotype to 1–100. Use it to compare nodes within the same phenotype page. Do not compare it as a common effect-size scale across pages.

### Q: Does TSUMUGI keep a gene pair visible when a filter would otherwise return no results?

**A:** No. Current filters apply the selected ranges directly, and the network can become empty. Widen the Effect size or Phenotypes similarity range, or reset the metadata filters, when no nodes or edges remain.

### Q: Why does a tooltip show `Effect size: N/A`?

**A:** The source IMPC record has no finite effect-size value. Missing effect sizes are stored as JSON `null` and are not converted to zero.

### Q: Why is Effect size absent from some pages or tooltips?

**A:** TSUMUGI hides the Effect size control where the value is not informative for the view, including binary phenotype pages and Gene or Gene List views.

### Q: What does the 1–100 Phenotypes similarity value mean?

**A:** The distributed `phenotype_similarity_score` is a 0–100 Phenodigm score. The web app rescales the scores available in each network to 1–100 for display and filtering. Values shown on different pages are therefore not directly comparable.

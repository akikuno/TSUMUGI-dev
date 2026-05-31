# TSUMUGI FAQ

## Network Visualization

### Q: Why do I see nodes with low effect-size scores (e.g., 5.1/10) when I set the Effect size slider to 9-10?

**A:** This is an intended behavior designed to ensure that at least one gene pair remains visible in the network visualization, even when using extreme filter values. 

When you adjust the effect-size slider to a very narrow range (like 9-10), the system automatically adjusts the filtering range to guarantee that:
- At least one edge (gene-gene connection) is displayed
- The nodes (genes) connected by that edge remain visible

This prevents the network from becoming completely empty when applying strict filters. The implementation (referenced as Issue #72 in the codebase) uses a ranking system to identify the most relevant gene pairs and ensures they remain visible regardless of the slider settings.

This design choice prioritizes usability by always showing some meaningful results rather than displaying an empty network when filter criteria are too restrictive.

### Q: Why don't I see effect-size scores in some tooltips when clicking on nodes?

**A:** Effect-size scores are only displayed when there is meaningful variability in the IMPC-derived effect size data. Effect-size scores are NOT displayed in the following cases:

1. **Binary phenotypes**: When all node color values are exclusively 0 or 1 (representing absence/presence only)
2. **Uniform effect size**: When all nodes have the exact same effect-size value
3. **Gene-centric views**: Often in gene-specific network visualizations where phenotypes are binary

The effect-size score is not meaningful in these cases and therefore omitted from the tooltip. This design choice ensures that effect-size scores are only shown when they provide quantitative information about the magnitude of genotype-associated phenotypic differences.

When effect-size scores are available, they appear as "(Effect size: X.X/10)" in the node tooltip. When they're not applicable, the tooltip simply shows the phenotype information without an effect-size score.

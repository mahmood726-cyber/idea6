"""
Example: Multiverse Analysis for Sensitivity Testing

This example demonstrates how to use MultiverseAnalyzer to:
1. Systematically explore all analytical paths
2. Assess sensitivity to analytical decisions
3. Calculate fragility metrics
4. Identify influential choices
5. Export comprehensive results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from robuststat import MultiverseAnalyzer

# Set random seed for reproducibility
np.random.seed(42)


def simulate_complex_dataset(n=400, true_effect=0.25):
    """
    Simulate a complex dataset with outliers, missing data, and multiple variables.
    """
    data = pd.DataFrame({
        # Main variables
        'treatment': np.random.choice([0, 1], n),
        'outcome': np.random.normal(50, 15, n),

        # Covariates
        'x1_age': np.random.uniform(18, 70, n),
        'x2_baseline': np.random.normal(100, 20, n),
        'x3_severity': np.random.poisson(3, n),
        'x4_comorbidity': np.random.choice([0, 1], n, p=[0.7, 0.3]),
    })

    # Add true treatment effect
    data.loc[data['treatment'] == 1, 'outcome'] += true_effect * 10

    # Add some outliers (5%)
    n_outliers = int(0.05 * n)
    outlier_idx = np.random.choice(n, n_outliers, replace=False)
    data.loc[outlier_idx, 'outcome'] += np.random.normal(0, 50, n_outliers)

    # Add missing data (10%)
    missing_idx = np.random.choice(n, int(0.1 * n), replace=False)
    data.loc[missing_idx, 'x2_baseline'] = np.nan

    missing_idx2 = np.random.choice(n, int(0.05 * n), replace=False)
    data.loc[missing_idx2, 'outcome'] = np.nan

    return data


# ============================================================================
# Example 1: Basic Multiverse Analysis
# ============================================================================

print("=" * 80)
print("EXAMPLE 1: Basic Multiverse Analysis")
print("=" * 80)

# Generate data
data = simulate_complex_dataset(n=400, true_effect=0.25)

print(f"\nDataset shape: {data.shape}")
print(f"Missing values per column:")
print(data.isnull().sum())
print(f"\nOutcome statistics:")
print(data['outcome'].describe())

# Define the analytical universe
universe = {
    'data_processing': {
        'outlier_removal': [None, 'iqr', 'z_score', 'percentile'],
        'missing_data': ['listwise', 'mean_impute'],
        'transformations': [None, 'standardize'],
    },
    'model_specification': {
        'covariates': [
            [],
            ['x1_age'],
            ['x1_age', 'x2_baseline'],
            ['x1_age', 'x2_baseline', 'x3_severity'],
            ['x1_age', 'x2_baseline', 'x3_severity', 'x4_comorbidity'],
        ],
        'model_type': ['ols', 'robust'],
        'interactions': [False],
    },
    'inference': {
        'alpha': [0.05],
        'adjustment': [None],
    },
}

print("\n" + "=" * 80)
print("ANALYTICAL UNIVERSE SPECIFICATION")
print("=" * 80)
for category, choices in universe.items():
    print(f"\n{category.upper()}:")
    for choice, options in choices.items():
        print(f"  {choice}: {len(options)} options")

# Create multiverse analyzer
multiverse = MultiverseAnalyzer(
    data=data,
    universe_spec=universe,
    outcome='outcome',
    predictor='treatment'
)

# Explore the multiverse
print("\n" + "=" * 80)
print("EXPLORING THE MULTIVERSE")
print("=" * 80)

results = multiverse.explore(verbose=True)

print(f"\nCompleted exploration of {len(results)} analytical paths")

# Get summary
summary = multiverse.get_summary()
print("\n" + "=" * 80)
print("MULTIVERSE SUMMARY")
print("=" * 80)
print(summary.to_string())

# ============================================================================
# Example 2: Fragility Analysis
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 2: Analytical Fragility Assessment")
print("=" * 80)

# Calculate fragility metrics
fragility = multiverse.calculate_fragility()

print("\nFRAGILITY METRICS:")
for metric, value in fragility.items():
    print(f"  {metric}: {value:.4f}")

# Interpretation
print("\nINTERPRETATION:")
if fragility['inferential_fragility'] < 0.3:
    print("  ✓ LOW INFERENTIAL FRAGILITY: Results are robust to analytical choices")
elif fragility['inferential_fragility'] < 0.5:
    print("  ⚠ MODERATE INFERENTIAL FRAGILITY: Some sensitivity to choices")
else:
    print("  ✗ HIGH INFERENTIAL FRAGILITY: Results highly dependent on choices")

if fragility['sign_fragility'] < 0.1:
    print("  ✓ LOW SIGN FRAGILITY: Effect direction is consistent")
elif fragility['sign_fragility'] < 0.3:
    print("  ⚠ MODERATE SIGN FRAGILITY: Some inconsistency in effect direction")
else:
    print("  ✗ HIGH SIGN FRAGILITY: Effect direction flips frequently")

# ============================================================================
# Example 3: Identifying Influential Choices
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 3: Identifying Influential Analytical Choices")
print("=" * 80)

# Identify which choices matter most
influential = multiverse.identify_influential_choices(n=10)

print("\nMOST INFLUENTIAL CHOICES (ranked by impact on results):")
print(influential.to_string())

# ============================================================================
# Example 4: Multiverse Visualization
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 4: Multiverse Visualization")
print("=" * 80)

print("\nGenerating comprehensive multiverse visualization...")
fig1 = multiverse.visualize_multiverse(figsize=(18, 12), show=False)
plt.savefig('/home/user/idea6/examples/multiverse_comprehensive.png', dpi=150, bbox_inches='tight')
plt.close()

print("Visualization saved to: examples/multiverse_comprehensive.png")

# ============================================================================
# Example 5: Subset Analysis by Specification Choices
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 5: Comparing Results by Analytical Choices")
print("=" * 80)

# Compare results by outlier removal method
print("\nEffect of OUTLIER REMOVAL on results:")
print("-" * 60)

for method in universe['data_processing']['outlier_removal']:
    col_name = 'choice_data_processing.outlier_removal'
    if col_name in results.columns:
        subset = results[results[col_name] == str(method)]

        if len(subset) > 0:
            print(f"\n{method if method else 'None'}:")
            print(f"  N paths: {len(subset)}")
            print(f"  Median coefficient: {subset['coefficient'].median():.4f}")
            print(f"  % Significant: {100 * subset['significant'].mean():.1f}%")

# Compare by covariate choice
print("\n\nEffect of COVARIATES on results:")
print("-" * 60)

col_name = 'choice_model_specification.covariates'
if col_name in results.columns:
    for cov_set in results[col_name].unique():
        subset = results[results[col_name] == cov_set]
        print(f"\n{cov_set}:")
        print(f"  N paths: {len(subset)}")
        print(f"  Median coefficient: {subset['coefficient'].median():.4f}")
        print(f"  % Significant: {100 * subset['significant'].mean():.1f}%")

# ============================================================================
# Example 6: Grid Visualization
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 6: Grid Visualization of Two-Way Interactions")
print("=" * 80)

from robuststat.visualization import plot_multiverse_grid

# Create grid plot for two key dimensions
if 'choice_data_processing.outlier_removal' in results.columns and \
   'choice_model_specification.model_type' in results.columns:

    print("\nCreating grid visualization...")
    fig2 = plot_multiverse_grid(
        results,
        x_dimension='choice_model_specification.model_type',
        y_dimension='choice_data_processing.outlier_removal',
        metric='coefficient',
        figsize=(12, 8)
    )

    plt.savefig('/home/user/idea6/examples/multiverse_grid.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Grid plot saved to: examples/multiverse_grid.png")

# ============================================================================
# Example 7: Export Results
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 7: Exporting Multiverse Results")
print("=" * 80)

# Export to different formats
print("\nExporting results...")

# CSV
multiverse.export_multiverse('/home/user/idea6/examples/multiverse_results.csv')

# Excel (with multiple sheets)
try:
    multiverse.export_multiverse('/home/user/idea6/examples/multiverse_results.xlsx')
    print("  ✓ Excel file created with multiple sheets")
except Exception as e:
    print(f"  ⚠ Excel export failed: {e}")

# JSON
multiverse.export_multiverse('/home/user/idea6/examples/multiverse_results.json')

print("\nExport complete!")

# ============================================================================
# Example 8: Focused Multiverse (Smaller Universe)
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 8: Focused Multiverse Analysis")
print("=" * 80)

# Sometimes you want to focus on a smaller set of key decisions
focused_universe = {
    'data_processing': {
        'outlier_removal': [None, 'iqr'],
        'missing_data': ['listwise'],
        'transformations': [None],
    },
    'model_specification': {
        'covariates': [
            ['x1_age'],
            ['x1_age', 'x2_baseline'],
        ],
        'model_type': ['ols', 'robust'],
        'interactions': [False],
    },
    'inference': {
        'alpha': [0.05],
        'adjustment': [None],
    },
}

print("Running focused multiverse with fewer specifications...")

multiverse_focused = MultiverseAnalyzer(
    data=data,
    universe_spec=focused_universe,
    outcome='outcome',
    predictor='treatment'
)

results_focused = multiverse_focused.explore(verbose=False)

summary_focused = multiverse_focused.get_summary()
fragility_focused = multiverse_focused.calculate_fragility()

print("\nFOCUSED MULTIVERSE SUMMARY:")
print(summary_focused.to_string())

print("\nFRAGILITY COMPARISON:")
print(f"Full multiverse:")
print(f"  Inferential fragility: {fragility['inferential_fragility']:.3f}")
print(f"  Sign fragility: {fragility['sign_fragility']:.3f}")
print(f"\nFocused multiverse:")
print(f"  Inferential fragility: {fragility_focused['inferential_fragility']:.3f}")
print(f"  Sign fragility: {fragility_focused['sign_fragility']:.3f}")

# ============================================================================
# Summary and Best Practices
# ============================================================================

print("\n" + "=" * 80)
print("MULTIVERSE ANALYSIS - BEST PRACTICES")
print("=" * 80)

best_practices = """
1. DEFINE THE UNIVERSE CAREFULLY:
   - Include all defensible analytical choices
   - Don't include arbitrary or unreasonable choices
   - Document rationale for each decision

2. CATEGORIZE CHOICES:
   - Data processing: outliers, missing data, transformations
   - Model specification: covariates, model types, interactions
   - Inference: significance levels, multiple testing corrections

3. INTERPRET RESULTS:
   - Median effect: Central estimate across all paths
   - Fragility metrics: How sensitive are conclusions?
   - Influential choices: Which decisions matter most?
   - Sign consistency: Does effect direction flip?

4. REPORT TRANSPARENTLY:
   - Show the full specification curve
   - Report fragility metrics
   - Identify and discuss influential choices
   - Acknowledge when results are fragile

5. USE APPROPRIATELY:
   - Multiverse analysis is for SENSITIVITY testing
   - Not for finding the "best" specification
   - Should be planned prospectively when possible
   - Complements (doesn't replace) pre-registration

KEY METRICS:
- Inferential Fragility: 1 - (% significant)
  → Low = robust, High = fragile
- Descriptive Fragility: CV of coefficients
  → Low = stable, High = variable
- Sign Fragility: % with different sign from median
  → Low = consistent, High = inconsistent
- Vibration of Effects: p95/p5 ratio
  → Low = tight, High = spread out

WHEN TO WORRY:
⚠ >50% paths non-significant
⚠ >20% paths have opposite sign
⚠ Wide range of effect sizes (e.g., [-0.5, +0.5])
⚠ Single choice dramatically changes results
"""

print(best_practices)

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

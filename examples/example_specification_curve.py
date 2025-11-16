"""
Example: Specification Curve Analysis for Robustness Assessment

This example demonstrates how to use SpecificationCurve to:
1. Test robustness across analytical choices
2. Visualize the specification curve
3. Identify influential specification decisions
4. Conduct inferential tests
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from robuststat import SpecificationCurve

# Set random seed for reproducibility
np.random.seed(42)


def simulate_research_data(n=500, true_effect=0.3, noise_level=1.0):
    """
    Simulate a dataset for research.

    The true effect of X on Y is 0.3, controlling for other variables.
    """
    data = pd.DataFrame({
        # Main predictor
        'X': np.random.normal(0, 1, n),

        # Confounders
        'age': np.random.uniform(18, 65, n),
        'gender': np.random.choice([0, 1], n),
        'education': np.random.choice([0, 1, 2], n),
        'income': np.random.lognormal(10, 1, n),

        # Additional covariates
        'baseline_measure': np.random.normal(50, 10, n),
        'health_status': np.random.uniform(0, 100, n),
    })

    # Generate outcome with true effect
    data['Y'] = (
        true_effect * data['X'] +
        0.1 * data['age'] +
        0.2 * data['gender'] +
        0.15 * data['education'] +
        0.0001 * data['income'] +
        0.3 * data['baseline_measure'] +
        np.random.normal(0, noise_level, n)
    )

    # Alternative outcomes (transformed)
    data['Y_log'] = np.log(data['Y'] - data['Y'].min() + 1)
    data['Y_binary'] = (data['Y'] > data['Y'].median()).astype(int)

    return data


# ============================================================================
# Example 1: Basic Specification Curve Analysis
# ============================================================================

print("=" * 80)
print("EXAMPLE 1: Basic Specification Curve Analysis")
print("=" * 80)

# Generate data
data = simulate_research_data(n=500, true_effect=0.3)

print(f"\nDataset shape: {data.shape}")
print(f"Outcome mean: {data['Y'].mean():.2f}")
print(f"Predictor mean: {data['X'].mean():.2f}")

# Define specification choices
specifications = {
    'controls': [
        [],                                          # No controls
        ['age', 'gender'],                          # Basic demographics
        ['age', 'gender', 'education'],             # + education
        ['age', 'gender', 'education', 'income'],   # + income
        ['age', 'gender', 'baseline_measure'],      # Alternative controls
    ],
    'models': [
        'ols',      # Regular OLS
        'robust',   # Robust standard errors
    ],
    'transformations': [
        None,         # No transformation
        'standardize', # Standardized outcome
    ],
}

print(f"\nSpecification dimensions:")
print(f"  Controls: {len(specifications['controls'])} options")
print(f"  Models: {len(specifications['models'])} options")
print(f"  Transformations: {len(specifications['transformations'])} options")
print(f"  Total specifications: {len(specifications['controls']) * len(specifications['models']) * len(specifications['transformations'])}")

# Create specification curve
spec_curve = SpecificationCurve(
    data=data,
    outcome='Y',
    predictor='X',
    specifications=specifications
)

# Run all specifications
print("\nRunning all specifications...")
results = spec_curve.run_all_specifications(verbose=True)

print(f"\nCompleted {len(results)} specifications")

# Get summary
summary = spec_curve.get_summary()
print("\n" + "=" * 80)
print("SPECIFICATION CURVE SUMMARY")
print("=" * 80)
print(summary.to_string())

# Plot specification curve
print("\nGenerating specification curve plot...")
fig1 = spec_curve.plot(show=False)
plt.savefig('/home/user/idea6/examples/spec_curve_basic.png', dpi=150, bbox_inches='tight')
plt.close()

print("Plot saved to: examples/spec_curve_basic.png")

# ============================================================================
# Example 2: Identifying Influential Specifications
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 2: Identifying Influential Specification Choices")
print("=" * 80)

# Identify which choices matter most
influential = spec_curve.get_influential_specs(n=10)

print("\nMost Influential Specification Choices:")
print(influential.to_string())

# ============================================================================
# Example 3: Specification Curve with Subsets
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 3: Specification Curve with Data Subsetting")
print("=" * 80)

# Define specifications with subsetting
specifications_subset = {
    'controls': [
        ['age', 'gender'],
        ['age', 'gender', 'education'],
    ],
    'models': ['ols', 'robust'],
    'subsets': [
        None,                                # Full sample
        lambda df: df['age'] < 40,          # Younger participants
        lambda df: df['age'] >= 40,         # Older participants
        lambda df: df['gender'] == 1,       # Gender subgroup
    ],
}

spec_curve_subset = SpecificationCurve(
    data=data,
    outcome='Y',
    predictor='X',
    specifications=specifications_subset
)

print("\nRunning specifications with subsetting...")
results_subset = spec_curve_subset.run_all_specifications(verbose=True)

summary_subset = spec_curve_subset.get_summary()
print("\nSummary with subsetting:")
print(summary_subset.to_string())

# Plot
fig2 = spec_curve_subset.plot(show=False)
plt.savefig('/home/user/idea6/examples/spec_curve_subsets.png', dpi=150, bbox_inches='tight')
plt.close()

print("Plot saved to: examples/spec_curve_subsets.png")

# ============================================================================
# Example 4: Advanced Visualization
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 4: Advanced Specification Curve Visualization")
print("=" * 80)

from robuststat.visualization import plot_specification_curve_advanced

# Run original analysis
results_for_viz = spec_curve.results

# Create advanced plot
print("\nCreating advanced visualization...")
fig3 = plot_specification_curve_advanced(
    results_for_viz,
    groupby='spec_models',
    figsize=(16, 12)
)

plt.savefig('/home/user/idea6/examples/spec_curve_advanced.png', dpi=150, bbox_inches='tight')
plt.close()

print("Advanced plot saved to: examples/spec_curve_advanced.png")

# ============================================================================
# Example 5: Multiple Outcomes
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 5: Specification Curve with Multiple Outcomes")
print("=" * 80)

specifications_multi = {
    'controls': [
        ['age', 'gender'],
        ['age', 'gender', 'education'],
    ],
    'models': ['ols'],
}

# Test across different outcome measures
outcomes = ['Y', 'Y_log']

all_results = []

for outcome in outcomes:
    print(f"\nAnalyzing outcome: {outcome}")

    spec_curve_outcome = SpecificationCurve(
        data=data,
        outcome=outcome,
        predictor='X',
        specifications=specifications_multi
    )

    results_outcome = spec_curve_outcome.run_all_specifications(verbose=False)
    results_outcome['outcome_type'] = outcome

    all_results.append(results_outcome)

# Combine results
combined_results = pd.concat(all_results, ignore_index=True)

print("\n" + "=" * 80)
print("COMPARISON ACROSS OUTCOMES")
print("=" * 80)

for outcome in outcomes:
    subset = combined_results[combined_results['outcome_type'] == outcome]
    print(f"\n{outcome}:")
    print(f"  Median coefficient: {subset['coefficient'].median():.4f}")
    print(f"  % Significant: {100 * subset['significant'].mean():.1f}%")
    print(f"  Range: [{subset['coefficient'].min():.4f}, {subset['coefficient'].max():.4f}]")

# ============================================================================
# Example 6: Robustness Assessment
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 6: Robustness Assessment")
print("=" * 80)

# Assess how robust the findings are

results_main = spec_curve.results

# Calculate robustness metrics
pct_significant = 100 * results_main['significant'].mean()
pct_positive = 100 * (results_main['coefficient'] > 0).mean()
pct_same_sign_as_median = 100 * (
    np.sign(results_main['coefficient']) ==
    np.sign(results_main['coefficient'].median())
).mean()

median_coef = results_main['coefficient'].median()
q25 = results_main['coefficient'].quantile(0.25)
q75 = results_main['coefficient'].quantile(0.75)

print("\nROBUSTNESS METRICS:")
print(f"  Percentage of specifications significant (p < .05): {pct_significant:.1f}%")
print(f"  Percentage of specifications with positive effect: {pct_positive:.1f}%")
print(f"  Percentage with same sign as median: {pct_same_sign_as_median:.1f}%")
print(f"\n  Median effect: {median_coef:.4f}")
print(f"  Interquartile range: [{q25:.4f}, {q75:.4f}]")
print(f"  Range: [{results_main['coefficient'].min():.4f}, {results_main['coefficient'].max():.4f}]")

# Robustness interpretation
if pct_significant > 90 and pct_same_sign_as_median > 95:
    print("\n  ✓ ROBUST: Findings are highly robust across specifications")
elif pct_significant > 70 and pct_same_sign_as_median > 80:
    print("\n  ✓ MODERATELY ROBUST: Findings show reasonable robustness")
elif pct_significant > 50:
    print("\n  ⚠ WEAK ROBUSTNESS: Findings are sensitive to specification choices")
else:
    print("\n  ✗ NOT ROBUST: Findings are highly sensitive to analytical choices")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION GUIDE - SPECIFICATION CURVE ANALYSIS")
print("=" * 80)

guide = """
KEY PRINCIPLES:
1. Run ALL reasonable specifications, not just those that "work"
2. Display results as a curve sorted by effect size
3. Show which specifications were used for each estimate
4. Conduct inferential tests (if needed)

WHAT TO LOOK FOR:
- Median effect: Central tendency of effect across specifications
- Range: How much does the effect vary?
- % Significant: Are most/all specifications significant?
- Influential choices: Which decisions matter most?

ROBUSTNESS CRITERIA:
✓ Strong: >90% specifications significant, consistent sign
✓ Moderate: 70-90% significant, mostly consistent sign
⚠ Weak: 50-70% significant, some inconsistency
✗ Fragile: <50% significant, sign flips common

BEST PRACTICES:
- Pre-register specification choices when possible
- Include all defensible specifications
- Report both descriptive and inferential statistics
- Identify and discuss influential decisions
- Be transparent about excluded specifications
"""

print(guide)

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

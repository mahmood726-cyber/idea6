"""
Example: Integrated Robustness Analysis

This example demonstrates how to use all three methods together:
1. P-Curve Analysis for evidential value
2. Specification Curve Analysis for robustness
3. Multiverse Analysis for sensitivity

Use case: Meta-science investigation of a research literature
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from robuststat import PCurveAnalyzer, SpecificationCurve, MultiverseAnalyzer
from robuststat.visualization import plot_robustness_dashboard

# Set random seed
np.random.seed(42)


def simulate_literature_and_data(n_studies=25, n_per_study=100):
    """
    Simulate a research literature with multiple published studies
    and a new dataset for replication.
    """
    # Simulate published p-values from literature
    p_values = []
    true_effect = 0.35  # True effect size

    for i in range(n_studies):
        # Simulate varying power across studies
        study_n = np.random.randint(50, 200)
        study_effect = true_effect + np.random.normal(0, 0.1)  # Heterogeneity

        # Generate data
        control = np.random.normal(0, 1, study_n)
        treatment = np.random.normal(study_effect, 1, study_n)

        # T-test
        from scipy.stats import ttest_ind
        t_stat, p_val = ttest_ind(control, treatment)

        # Publication bias: only significant results published (file drawer)
        if p_val < 0.05 or np.random.random() < 0.1:  # 10% null results published
            p_values.append(p_val)

    # Simulate new dataset for replication
    n_total = n_per_study * 4  # 4 conditions

    data = pd.DataFrame({
        'participant_id': range(n_total),
        'condition': np.repeat(['control', 'treatment_low', 'treatment_med', 'treatment_high'], n_per_study),

        # Outcome measures (multiple operationalizations)
        'outcome_primary': np.random.normal(50, 15, n_total),
        'outcome_secondary': np.random.normal(100, 25, n_total),
        'outcome_alternative': np.random.poisson(5, n_total),

        # Covariates
        'age': np.random.uniform(18, 65, n_total),
        'gender': np.random.choice(['M', 'F'], n_total),
        'baseline_score': np.random.normal(50, 10, n_total),
        'site': np.random.choice(['Site_A', 'Site_B', 'Site_C'], n_total),
    })

    # Add treatment effects
    for i, cond in enumerate(['treatment_low', 'treatment_med', 'treatment_high']):
        mask = data['condition'] == cond
        effect_size = (i + 1) * true_effect * 5  # Escalating doses

        data.loc[mask, 'outcome_primary'] += effect_size
        data.loc[mask, 'outcome_secondary'] += effect_size * 1.5
        data.loc[mask, 'outcome_alternative'] += effect_size / 5

    # Add outliers and missing data
    outlier_idx = np.random.choice(n_total, int(0.03 * n_total), replace=False)
    data.loc[outlier_idx, 'outcome_primary'] += np.random.normal(0, 50, len(outlier_idx))

    missing_idx = np.random.choice(n_total, int(0.08 * n_total), replace=False)
    data.loc[missing_idx, 'baseline_score'] = np.nan

    return np.array(p_values), data


print("=" * 80)
print("INTEGRATED ROBUSTNESS ANALYSIS")
print("Research Question: Does Treatment X affect Outcome Y?")
print("=" * 80)

# ============================================================================
# Step 1: Generate Literature and Data
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Simulating Research Literature and Replication Data")
print("=" * 80)

p_values_literature, replication_data = simulate_literature_and_data(
    n_studies=25,
    n_per_study=100
)

print(f"\nLiterature meta-analysis:")
print(f"  {len(p_values_literature)} published studies found")
print(f"  Significant studies: {sum(p < 0.05 for p in p_values_literature)}")
print(f"  Mean p-value: {np.mean(p_values_literature):.4f}")

print(f"\nReplication dataset:")
print(f"  N = {len(replication_data)}")
print(f"  Conditions: {replication_data['condition'].unique()}")
print(f"  Outcome measures: 3 different operationalizations")

# ============================================================================
# Step 2: P-Curve Analysis of Existing Literature
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: P-Curve Analysis of Published Literature")
print("=" * 80)

# Filter to significant findings only
sig_p = p_values_literature[p_values_literature < 0.05]

print(f"\nAnalyzing {len(sig_p)} significant findings from literature")

# Run p-curve analysis
pcurve = PCurveAnalyzer(sig_p)
pcurve_results = pcurve.analyze()

print(pcurve.get_interpretation())

# Plot p-curve
fig_pcurve = pcurve.plot(show=False)
plt.savefig('/home/user/idea6/examples/integrated_pcurve.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nP-curve plot saved to: examples/integrated_pcurve.png")

# Decision point based on p-curve
has_evidential_value = pcurve_results['evidential_value']

if has_evidential_value:
    print("\n✓ DECISION: Literature shows evidential value. Proceed with replication.")
else:
    print("\n✗ DECISION: Literature lacks evidential value. Replication may not be worthwhile.")

# ============================================================================
# Step 3: Specification Curve Analysis of Replication
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: Specification Curve Analysis of Replication Study")
print("=" * 80)

# Create treatment variable (binary: control vs any treatment)
replication_data['treatment'] = (replication_data['condition'] != 'control').astype(int)

# Also create dose variable
dose_map = {'control': 0, 'treatment_low': 1, 'treatment_med': 2, 'treatment_high': 3}
replication_data['dose'] = replication_data['condition'].map(dose_map)

# Encode categorical variables
replication_data['gender_numeric'] = (replication_data['gender'] == 'M').astype(int)
replication_data['site_numeric'] = pd.Categorical(replication_data['site']).codes

# Define specification choices
spec_choices = {
    'controls': [
        [],
        ['age'],
        ['age', 'gender_numeric'],
        ['age', 'gender_numeric', 'baseline_score'],
        ['age', 'gender_numeric', 'baseline_score', 'site_numeric'],
    ],
    'models': ['ols', 'robust'],
    'transformations': [None, 'standardize'],
}

# Test primary outcome with binary treatment
print("\nRunning specification curve for primary outcome...")

spec_curve_primary = SpecificationCurve(
    data=replication_data.dropna(),  # For simplicity
    outcome='outcome_primary',
    predictor='treatment',
    specifications=spec_choices
)

spec_results_primary = spec_curve_primary.run_all_specifications(verbose=True)

spec_summary = spec_curve_primary.get_summary()
print("\nSpecification Curve Summary:")
print(spec_summary.to_string())

# Plot specification curve
fig_spec = spec_curve_primary.plot(show=False)
plt.savefig('/home/user/idea6/examples/integrated_spec_curve.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nSpecification curve plot saved to: examples/integrated_spec_curve.png")

# Assess robustness
pct_sig = 100 * spec_results_primary['significant'].mean()
print(f"\n{pct_sig:.1f}% of specifications are significant")

if pct_sig > 90:
    print("✓ DECISION: Effect is highly robust across specifications")
    spec_robust = True
elif pct_sig > 70:
    print("⚠ DECISION: Effect shows moderate robustness")
    spec_robust = True
else:
    print("✗ DECISION: Effect is not robust to specification choices")
    spec_robust = False

# ============================================================================
# Step 4: Multiverse Analysis for Sensitivity
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: Multiverse Analysis for Comprehensive Sensitivity Testing")
print("=" * 80)

# Define full analytical universe
universe_spec = {
    'data_processing': {
        'outlier_removal': [None, 'iqr', 'z_score'],
        'missing_data': ['listwise', 'mean_impute'],
        'transformations': [None, 'standardize'],
    },
    'model_specification': {
        'covariates': [
            [],
            ['age', 'gender_numeric'],
            ['age', 'gender_numeric', 'baseline_score'],
        ],
        'model_type': ['ols', 'robust'],
        'interactions': [False],
    },
    'inference': {
        'alpha': [0.05],
        'adjustment': [None],
    },
}

print("\nExploring analytical multiverse...")

multiverse = MultiverseAnalyzer(
    data=replication_data,
    universe_spec=universe_spec,
    outcome='outcome_primary',
    predictor='treatment'
)

multiverse_results = multiverse.explore(verbose=True)

multiverse_summary = multiverse.get_summary()
print("\nMultiverse Summary:")
print(multiverse_summary.to_string())

# Calculate fragility
fragility = multiverse.calculate_fragility()
print("\nFragility Metrics:")
for metric, value in fragility.items():
    print(f"  {metric}: {value:.4f}")

# Plot multiverse
fig_multiverse = multiverse.visualize_multiverse(figsize=(18, 12), show=False)
plt.savefig('/home/user/idea6/examples/integrated_multiverse.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nMultiverse plot saved to: examples/integrated_multiverse.png")

# Identify influential choices
influential = multiverse.identify_influential_choices(n=5)
print("\nMost Influential Analytical Choices:")
print(influential.to_string())

# Assessment
if fragility['inferential_fragility'] < 0.3:
    print("\n✓ DECISION: Results are robust to analytical choices")
    multiverse_robust = True
else:
    print("\n✗ DECISION: Results are fragile to analytical choices")
    multiverse_robust = False

# ============================================================================
# Step 5: Integrated Dashboard
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: Creating Integrated Robustness Dashboard")
print("=" * 80)

fig_dashboard = plot_robustness_dashboard(
    pcurve_results=pcurve_results,
    spec_curve_results=spec_results_primary,
    multiverse_results=multiverse_results,
    figsize=(20, 14)
)

plt.savefig('/home/user/idea6/examples/integrated_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nIntegrated dashboard saved to: examples/integrated_dashboard.png")

# ============================================================================
# Step 6: Overall Assessment and Recommendations
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: Overall Assessment and Recommendations")
print("=" * 80)

print("\nSUMMARY OF ANALYSES:")
print("-" * 80)
print(f"1. P-Curve Analysis:")
print(f"   Evidential value in literature: {'YES' if has_evidential_value else 'NO'}")
print(f"   Estimated power: {pcurve_results['power_estimate']['estimated_power']:.0%}")

print(f"\n2. Specification Curve Analysis:")
print(f"   Specifications significant: {pct_sig:.1f}%")
print(f"   Median effect: {spec_results_primary['coefficient'].median():.4f}")
print(f"   Robustness: {'HIGH' if pct_sig > 90 else 'MODERATE' if pct_sig > 70 else 'LOW'}")

print(f"\n3. Multiverse Analysis:")
print(f"   Total paths analyzed: {len(multiverse_results)}")
print(f"   Inferential fragility: {fragility['inferential_fragility']:.3f}")
print(f"   Sign fragility: {fragility['sign_fragility']:.3f}")
print(f"   Robustness: {'HIGH' if multiverse_robust else 'LOW'}")

# Overall conclusion
print("\n" + "=" * 80)
print("OVERALL CONCLUSION")
print("=" * 80)

if has_evidential_value and spec_robust and multiverse_robust:
    conclusion = """
✓✓✓ STRONG EVIDENCE FOR EFFECT

The effect is:
1. Supported by evidential value in the literature (p-curve)
2. Robust across reasonable specification choices
3. Not fragile to analytical decisions

RECOMMENDATION: High confidence in the existence of this effect.
Suitable for publication and practical application.
"""
elif has_evidential_value and (spec_robust or multiverse_robust):
    conclusion = """
✓✓ MODERATE EVIDENCE FOR EFFECT

The effect is:
1. Supported by evidential value in the literature
2. Shows some robustness, but also some sensitivity

RECOMMENDATION: Moderate confidence. Consider additional replication
or focus on conditions where effect is most robust.
"""
else:
    conclusion = """
⚠ WEAK OR QUESTIONABLE EVIDENCE

Concerns:
- Lack of evidential value in literature, OR
- High sensitivity to analytical choices, OR
- Fragile to data processing decisions

RECOMMENDATION: Low confidence. Need for:
1. More rigorous, pre-registered studies
2. Investigation of moderators
3. Better measurement/methodology
"""

print(conclusion)

# ============================================================================
# Step 7: Export Comprehensive Report
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: Exporting Comprehensive Report")
print("=" * 80)

# Create summary report
report = {
    'Literature': {
        'n_studies': len(p_values_literature),
        'evidential_value': has_evidential_value,
        'power_estimate': pcurve_results['power_estimate']['estimated_power'],
    },
    'Specification_Curve': {
        'n_specifications': len(spec_results_primary),
        'pct_significant': pct_sig,
        'median_effect': float(spec_results_primary['coefficient'].median()),
        'effect_range': [
            float(spec_results_primary['coefficient'].min()),
            float(spec_results_primary['coefficient'].max())
        ],
    },
    'Multiverse': {
        'n_paths': len(multiverse_results),
        'fragility_metrics': fragility,
        'median_effect': float(multiverse_results['coefficient'].median()),
    },
}

# Save report
import json
with open('/home/user/idea6/examples/integrated_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print("\nComprehensive report saved to: examples/integrated_report.json")

# Export multiverse results
multiverse.export_multiverse('/home/user/idea6/examples/integrated_multiverse_results.csv')

# Save specification curve results
spec_results_primary.to_csv('/home/user/idea6/examples/integrated_spec_curve_results.csv', index=False)

# Save p-curve results
pcurve_df = pcurve.to_dataframe()
pcurve_df.to_csv('/home/user/idea6/examples/integrated_pcurve_results.csv', index=False)

print("\nAll results exported!")

print("\n" + "=" * 80)
print("INTEGRATED ANALYSIS COMPLETE")
print("=" * 80)

print("""
This integrated approach provides:
1. Evidence for the existence of an effect (p-curve)
2. Assessment of robustness (specification curve)
3. Quantification of fragility (multiverse)

Together, these methods offer a comprehensive evaluation of
research claims that goes beyond traditional meta-analysis or
single-study replication.
""")

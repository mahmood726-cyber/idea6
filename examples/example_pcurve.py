"""
Example: P-Curve Analysis for Evidential Value Assessment

This example demonstrates how to use the PCurveAnalyzer to:
1. Test for evidential value in a set of significant findings
2. Detect potential p-hacking
3. Estimate statistical power
4. Visualize the p-curve
"""

import numpy as np
import matplotlib.pyplot as plt
from robuststat import PCurveAnalyzer

# Set random seed for reproducibility
np.random.seed(42)


def simulate_real_effects(n_studies=20, true_effect_size=0.5, sample_size=50):
    """Simulate p-values from studies with real effects."""
    p_values = []

    for _ in range(n_studies):
        # Generate data with true effect
        group1 = np.random.normal(0, 1, sample_size)
        group2 = np.random.normal(true_effect_size, 1, sample_size)

        # Two-sample t-test
        from scipy.stats import ttest_ind
        t_stat, p_val = ttest_ind(group1, group2)
        p_values.append(p_val)

    # Keep only significant ones (file-drawer effect)
    sig_p = [p for p in p_values if p < 0.05]

    return np.array(sig_p)


def simulate_p_hacked_effects(n_studies=20, sample_size=50):
    """Simulate p-values from p-hacked studies (no real effect)."""
    p_values = []

    for _ in range(n_studies):
        # Keep collecting data until p < 0.05 (p-hacking)
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            group1 = np.random.normal(0, 1, sample_size)
            group2 = np.random.normal(0, 1, sample_size)  # No real difference

            from scipy.stats import ttest_ind
            t_stat, p_val = ttest_ind(group1, group2)

            if p_val < 0.05:
                p_values.append(p_val)
                break

            attempts += 1

    return np.array(p_values)


# ============================================================================
# Example 1: P-Curve with Real Effects (High Power)
# ============================================================================

print("=" * 80)
print("EXAMPLE 1: P-Curve Analysis - Studies with Real Effects (High Power)")
print("=" * 80)

# Simulate p-values from studies with real, large effects
p_values_real = simulate_real_effects(n_studies=30, true_effect_size=0.8, sample_size=80)

print(f"\nSimulated {len(p_values_real)} significant p-values from studies with real effects")
print(f"P-values: {p_values_real[:5]}...")

# Create analyzer
analyzer_real = PCurveAnalyzer(p_values_real)

# Run analysis
results_real = analyzer_real.analyze()

# Print interpretation
print("\n" + analyzer_real.get_interpretation())

# Plot
fig1 = analyzer_real.plot(show=False)
plt.savefig('/home/user/idea6/examples/pcurve_real_effects.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nPlot saved to: examples/pcurve_real_effects.png")

# ============================================================================
# Example 2: P-Curve with P-Hacked Results (No Real Effect)
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 2: P-Curve Analysis - P-Hacked Studies (No Real Effect)")
print("=" * 80)

# Simulate p-hacked p-values
p_values_hacked = simulate_p_hacked_effects(n_studies=25, sample_size=50)

print(f"\nSimulated {len(p_values_hacked)} p-hacked p-values")
print(f"P-values: {p_values_hacked[:5]}...")

# Create analyzer
analyzer_hacked = PCurveAnalyzer(p_values_hacked)

# Run analysis
results_hacked = analyzer_hacked.analyze()

# Print interpretation
print("\n" + analyzer_hacked.get_interpretation())

# Plot
fig2 = analyzer_hacked.plot(show=False)
plt.savefig('/home/user/idea6/examples/pcurve_p_hacked.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nPlot saved to: examples/pcurve_p_hacked.png")

# ============================================================================
# Example 3: Comparison of Multiple P-Curves
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 3: Comparing Multiple P-Curves")
print("=" * 80)

# Simulate different scenarios
p_high_power = simulate_real_effects(n_studies=30, true_effect_size=0.8, sample_size=80)
p_low_power = simulate_real_effects(n_studies=30, true_effect_size=0.3, sample_size=40)
p_hacked = simulate_p_hacked_effects(n_studies=25, sample_size=50)

from robuststat.visualization import plot_pcurve_comparison

fig3 = plot_pcurve_comparison({
    'High Power (d=0.8)': p_high_power,
    'Low Power (d=0.3)': p_low_power,
    'P-Hacked (d=0)': p_hacked,
}, figsize=(14, 6))

plt.savefig('/home/user/idea6/examples/pcurve_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nComparison plot saved to: examples/pcurve_comparison.png")

# ============================================================================
# Example 4: Real-World Example - Meta-Analysis
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 4: Real-World Application - Meta-Analysis")
print("=" * 80)

# Simulate p-values from a real meta-analysis
# Let's say we collected 15 studies investigating the effect of intervention X

# Some studies have real effects, some are p-hacked
real_studies = simulate_real_effects(n_studies=10, true_effect_size=0.4, sample_size=60)
questionable_studies = simulate_p_hacked_effects(n_studies=5, sample_size=40)

# Combine them (as would happen in a real literature)
all_studies = np.concatenate([real_studies, questionable_studies])

print(f"\nAnalyzing {len(all_studies)} studies from literature")

# Analyze
analyzer_meta = PCurveAnalyzer(all_studies)
results_meta = analyzer_meta.analyze()

print("\n" + analyzer_meta.get_interpretation())

# Get results as DataFrame
results_df = analyzer_meta.to_dataframe()
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(results_df.to_string())

# Plot
fig4 = analyzer_meta.plot(show=False)
plt.savefig('/home/user/idea6/examples/pcurve_meta_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nPlot saved to: examples/pcurve_meta_analysis.png")

# ============================================================================
# Summary and Interpretation Guide
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION GUIDE")
print("=" * 80)

interpretation_guide = """
1. RIGHT-SKEWED P-CURVE (More small p-values)
   → Indicates EVIDENTIAL VALUE
   → Studies contain real effects
   → Example: Studies with high statistical power

2. FLAT P-CURVE (Uniform distribution)
   → Indicates NO EVIDENTIAL VALUE
   → Cannot distinguish from chance
   → May indicate publication bias or p-hacking

3. LEFT-SKEWED P-CURVE (More p-values near 0.05)
   → Indicates P-HACKING
   → Studies show signs of selective reporting
   → Red flag for data manipulation

KEY METRICS:
- Full p-curve test: Tests if p < .05 results are right-skewed
- Half p-curve test: Tests if p < .025 results are right-skewed (more powerful)
- Both tests significant (p < .05) → Strong evidence for real effects
- Estimated power: Higher power → More convincing evidence

RECOMMENDATIONS:
- Use p-curve BEFORE conducting a meta-analysis
- Require at least 5-10 significant findings for reliable analysis
- Consider pre-registration to prevent p-hacking
- Report both full and half p-curve tests
"""

print(interpretation_guide)

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

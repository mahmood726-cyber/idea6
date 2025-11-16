"""
P-Curve Analyzer

Implementation of Simonsohn, Nelson, & Simmons (2014) p-curve methodology
for detecting evidential value and p-hacking in sets of significant findings.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Dict, Optional, Union, Tuple
import warnings


class PCurveAnalyzer:
    """
    P-Curve Analyzer for evidential value assessment.

    Based on Simonsohn, U., Nelson, L. D., & Simmons, J. P. (2014).
    P-curve: A key to the file-drawer. Journal of Experimental Psychology: General, 143(2), 534-547.

    The p-curve is the distribution of statistically significant p-values for a set of
    independent findings. It can be used to:
    1. Detect evidential value (right-skewed p-curve)
    2. Identify p-hacking (left-skewed or flat p-curve)
    3. Estimate statistical power

    Parameters
    ----------
    p_values : array-like
        Array of p-values from significant findings (should be < 0.05)
    test_statistics : array-like, optional
        Test statistics corresponding to p-values (for power estimation)
    df : array-like, optional
        Degrees of freedom for each test (for power estimation)
    """

    def __init__(
        self,
        p_values: Union[List[float], np.ndarray],
        test_statistics: Optional[Union[List[float], np.ndarray]] = None,
        df: Optional[Union[List[int], np.ndarray]] = None,
    ):
        self.p_values = np.array(p_values)
        self.test_statistics = np.array(test_statistics) if test_statistics is not None else None
        self.df = np.array(df) if df is not None else None

        # Validate inputs
        self._validate_inputs()

        # Results storage
        self.results = {}

    def _validate_inputs(self):
        """Validate input p-values and parameters."""
        # Check for valid p-values
        if np.any(self.p_values <= 0) or np.any(self.p_values > 1):
            raise ValueError("All p-values must be between 0 and 1")

        # Warn if p-values are not significant
        if np.any(self.p_values >= 0.05):
            warnings.warn(
                f"{np.sum(self.p_values >= 0.05)} p-values are >= 0.05. "
                "P-curve analysis is designed for significant findings only.",
                UserWarning
            )

        # Check minimum number of p-values
        if len(self.p_values) < 3:
            warnings.warn(
                "P-curve analysis with fewer than 3 p-values may be unreliable.",
                UserWarning
            )

    def analyze(self, alpha: float = 0.05) -> Dict:
        """
        Run complete p-curve analysis.

        Parameters
        ----------
        alpha : float
            Significance level for tests (default: 0.05)

        Returns
        -------
        dict
            Dictionary containing:
            - 'full_pcurve_test': Results of full p-curve test
            - 'half_pcurve_test': Results of half p-curve test
            - 'flatness_test': Test for flat p-curve
            - 'power_estimate': Estimated statistical power
            - 'evidential_value': Boolean indicating presence of evidential value
            - 'p_hacking_detected': Boolean indicating potential p-hacking
        """
        # Filter to significant p-values only
        sig_p = self.p_values[self.p_values < alpha]

        if len(sig_p) == 0:
            raise ValueError("No significant p-values to analyze")

        # Run tests
        full_test = self._test_right_skewness(sig_p, range_cutoff=alpha)
        half_test = self._test_right_skewness(sig_p, range_cutoff=0.025)
        flatness = self._test_flatness(sig_p, alpha)
        power_est = self._estimate_power(sig_p)

        # Determine evidential value
        # Evidential value if either full or half p-curve is right-skewed
        has_evidential_value = (full_test['p_value'] < 0.05) or (half_test['p_value'] < 0.05)

        # P-hacking suggested if p-curve is left-skewed or flat
        p_hacking = flatness['left_skewed'] or not has_evidential_value

        self.results = {
            'n_studies': len(sig_p),
            'full_pcurve_test': full_test,
            'half_pcurve_test': half_test,
            'flatness_test': flatness,
            'power_estimate': power_est,
            'evidential_value': has_evidential_value,
            'p_hacking_detected': p_hacking,
        }

        return self.results

    def _test_right_skewness(
        self,
        p_values: np.ndarray,
        range_cutoff: float = 0.05
    ) -> Dict:
        """
        Test if p-curve is right-skewed (indicating evidential value).

        Under the null hypothesis of no effect, p-values are uniformly distributed.
        Under the alternative hypothesis of true effects, p-curve is right-skewed.

        Parameters
        ----------
        p_values : np.ndarray
            Array of p-values to test
        range_cutoff : float
            Upper bound for p-values to include (0.05 for full, 0.025 for half)

        Returns
        -------
        dict
            Test statistics and p-value
        """
        # Filter to range
        p_in_range = p_values[p_values < range_cutoff]

        if len(p_in_range) == 0:
            return {
                'test_type': f'Right-skewness (p < {range_cutoff})',
                'test_statistic': np.nan,
                'p_value': 1.0,
                'significant': False,
            }

        # Convert p-values to uniform distribution under null
        # pp values are the percentiles of p-values under null uniform(0, range_cutoff)
        pp_values = p_in_range / range_cutoff

        # Binomial test: count how many p-values fall in lower half
        # Under right skew, more should be in lower half (pp < 0.5)
        n_lower = np.sum(pp_values < 0.5)
        n_total = len(pp_values)

        # One-sided binomial test
        # H0: p = 0.5 (uniform), H1: p > 0.5 (right-skewed)
        binom_p = 1 - stats.binom.cdf(n_lower - 1, n_total, 0.5)

        # Also calculate chi-square test for better power with continuous test
        # Use Stouffer's method to combine p-values
        # Convert pp values to z-scores under uniform null
        z_scores = stats.norm.ppf(1 - pp_values)
        z_combined = np.sum(z_scores) / np.sqrt(len(z_scores))
        chi_square_p = 1 - stats.norm.cdf(z_combined)

        # Use more conservative (higher) p-value
        final_p = max(binom_p, chi_square_p)

        return {
            'test_type': f'Right-skewness (p < {range_cutoff})',
            'n_tests': len(p_in_range),
            'n_lower_half': n_lower,
            'binomial_p': binom_p,
            'stouffer_z': z_combined,
            'stouffer_p': chi_square_p,
            'p_value': final_p,
            'significant': final_p < 0.05,
        }

    def _test_flatness(self, p_values: np.ndarray, alpha: float = 0.05) -> Dict:
        """
        Test if p-curve is flat (indicating absence of evidential value).

        Parameters
        ----------
        p_values : np.ndarray
            Array of p-values
        alpha : float
            Significance level

        Returns
        -------
        dict
            Flatness test results
        """
        # Test against uniform distribution using Kolmogorov-Smirnov test
        p_in_range = p_values[p_values < alpha]

        # Rescale to 0-1 range
        pp_values = p_in_range / alpha

        # KS test against uniform
        ks_stat, ks_p = stats.kstest(pp_values, 'uniform')

        # Chi-square goodness of fit test
        bins = np.linspace(0, alpha, 11)  # 10 bins
        observed, _ = np.histogram(p_in_range, bins=bins)
        expected = np.full(10, len(p_in_range) / 10)

        chi2_stat, chi2_p = stats.chisquare(observed, expected)

        # Test for left-skewness (p-hacking signature)
        # Count p-values in upper half vs lower half
        n_upper = np.sum(pp_values >= 0.5)
        n_total = len(pp_values)

        # One-sided binomial test for left skew
        # H1: more values in upper half (left-skewed)
        left_skew_p = 1 - stats.binom.cdf(n_upper - 1, n_total, 0.5)
        left_skewed = left_skew_p < 0.05

        return {
            'ks_statistic': ks_stat,
            'ks_p_value': ks_p,
            'chi2_statistic': chi2_stat,
            'chi2_p_value': chi2_p,
            'is_flat': ks_p > 0.05,  # Fail to reject uniformity
            'left_skewed': left_skewed,
            'left_skew_p': left_skew_p,
        }

    def _estimate_power(self, p_values: np.ndarray) -> Dict:
        """
        Estimate the statistical power of studies based on p-curve.

        Parameters
        ----------
        p_values : np.ndarray
            Array of significant p-values

        Returns
        -------
        dict
            Power estimates
        """
        # Power estimation using the p-curve method
        # Based on the distribution of p-values, estimate what power would
        # generate this distribution

        # Simple method: median p-value approach
        # Lower median p suggests higher power
        median_p = np.median(p_values)

        # Estimate power from median p-value
        # This is a simplified approximation
        # For a z-test, we can back out approximate power

        if median_p < 0.001:
            est_power = 0.99
        elif median_p < 0.01:
            est_power = 0.90
        elif median_p < 0.02:
            est_power = 0.75
        elif median_p < 0.03:
            est_power = 0.60
        elif median_p < 0.04:
            est_power = 0.45
        else:
            est_power = 0.30

        # More sophisticated power estimation using test statistics if available
        if self.test_statistics is not None and self.df is not None:
            # Back-calculate effect sizes and estimate power
            # This would require more detailed implementation
            power_from_stats = self._power_from_test_statistics()
        else:
            power_from_stats = None

        return {
            'estimated_power': est_power,
            'median_p': median_p,
            'mean_p': np.mean(p_values),
            'power_from_statistics': power_from_stats,
        }

    def _power_from_test_statistics(self) -> Optional[float]:
        """
        Estimate power from test statistics (if available).

        Returns
        -------
        float or None
            Estimated power
        """
        # This is a placeholder for more sophisticated power estimation
        # Would require specific test type information
        return None

    def get_interpretation(self) -> str:
        """
        Get a text interpretation of the p-curve analysis results.

        Returns
        -------
        str
            Interpretation of results
        """
        if not self.results:
            return "No analysis has been run yet. Call analyze() first."

        interpretation = []
        interpretation.append("=" * 60)
        interpretation.append("P-CURVE ANALYSIS RESULTS")
        interpretation.append("=" * 60)
        interpretation.append(f"\nNumber of studies analyzed: {self.results['n_studies']}")
        interpretation.append(f"\nEstimated power: {self.results['power_estimate']['estimated_power']:.2f}")
        interpretation.append(f"Median p-value: {self.results['power_estimate']['median_p']:.4f}")

        interpretation.append("\n" + "-" * 60)
        interpretation.append("EVIDENTIAL VALUE TEST")
        interpretation.append("-" * 60)

        if self.results['evidential_value']:
            interpretation.append("\n✓ EVIDENTIAL VALUE DETECTED")
            interpretation.append("The p-curve is right-skewed, indicating the presence of")
            interpretation.append("evidential value. The set of findings contains real effects.")
        else:
            interpretation.append("\n✗ NO EVIDENTIAL VALUE DETECTED")
            interpretation.append("The p-curve is not significantly right-skewed.")
            interpretation.append("Cannot rule out that findings are solely due to chance/p-hacking.")

        interpretation.append("\n" + "-" * 60)
        interpretation.append("P-HACKING TEST")
        interpretation.append("-" * 60)

        if self.results['p_hacking_detected']:
            interpretation.append("\n⚠ WARNING: Potential p-hacking detected")
            interpretation.append("The p-curve shows signs of selective reporting or p-hacking.")
        else:
            interpretation.append("\n✓ No strong evidence of p-hacking")

        interpretation.append("\n" + "-" * 60)
        interpretation.append("DETAILED TEST RESULTS")
        interpretation.append("-" * 60)

        full = self.results['full_pcurve_test']
        interpretation.append(f"\nFull p-curve test (p < .05):")
        interpretation.append(f"  p-value: {full['p_value']:.4f} {'*' if full['significant'] else ''}")

        half = self.results['half_pcurve_test']
        interpretation.append(f"\nHalf p-curve test (p < .025):")
        interpretation.append(f"  p-value: {half['p_value']:.4f} {'*' if half['significant'] else ''}")

        flat = self.results['flatness_test']
        interpretation.append(f"\nFlatness test:")
        interpretation.append(f"  KS p-value: {flat['ks_p_value']:.4f}")
        interpretation.append(f"  Is flat: {flat['is_flat']}")

        interpretation.append("\n" + "=" * 60)

        return "\n".join(interpretation)

    def plot(self, ax=None, show: bool = True):
        """
        Plot the p-curve.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to plot on
        show : bool
            Whether to display the plot

        Returns
        -------
        matplotlib.axes.Axes
        """
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        # Get significant p-values
        sig_p = self.p_values[self.p_values < 0.05]

        # Create bins
        bins = np.arange(0, 0.051, 0.01)

        # Plot histogram
        counts, edges, patches = ax.hist(
            sig_p,
            bins=bins,
            density=True,
            alpha=0.7,
            color='steelblue',
            edgecolor='black',
            label='Observed p-curve'
        )

        # Plot expected distribution under null (uniform)
        ax.axhline(
            y=20,  # 1/0.05 for uniform distribution
            color='red',
            linestyle='--',
            linewidth=2,
            label='Expected under H₀ (no effect)',
            alpha=0.7
        )

        # Plot expected under power = 33% (benchmark)
        x_vals = np.linspace(0.001, 0.05, 100)
        # Right-skewed distribution (simplified)
        y_vals = 40 * (1 - x_vals / 0.05) ** 2
        ax.plot(x_vals, y_vals, 'g--', linewidth=2,
                label='Expected under power = 33%', alpha=0.7)

        ax.set_xlabel('p-value', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title('P-Curve Analysis', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 0.05)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add interpretation box
        if self.results:
            ev_status = "YES" if self.results['evidential_value'] else "NO"
            power_est = self.results['power_estimate']['estimated_power']

            textstr = f'Evidential Value: {ev_status}\nEst. Power: {power_est:.0%}'
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', horizontalalignment='right', bbox=props)

        plt.tight_layout()

        if show:
            plt.show()

        return ax

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert results to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            Results as a DataFrame
        """
        if not self.results:
            raise ValueError("No analysis has been run yet. Call analyze() first.")

        data = {
            'Metric': [
                'Number of Studies',
                'Evidential Value',
                'P-hacking Detected',
                'Estimated Power',
                'Median p-value',
                'Full P-curve p-value',
                'Half P-curve p-value',
                'Flatness (KS) p-value',
            ],
            'Value': [
                self.results['n_studies'],
                'Yes' if self.results['evidential_value'] else 'No',
                'Yes' if self.results['p_hacking_detected'] else 'No',
                f"{self.results['power_estimate']['estimated_power']:.2%}",
                f"{self.results['power_estimate']['median_p']:.4f}",
                f"{self.results['full_pcurve_test']['p_value']:.4f}",
                f"{self.results['half_pcurve_test']['p_value']:.4f}",
                f"{self.results['flatness_test']['ks_p_value']:.4f}",
            ]
        }

        return pd.DataFrame(data)

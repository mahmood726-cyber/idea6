"""
Statistical tests for P-Curve Analysis

Additional statistical test implementations for p-curve analysis.
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple


class PCurveTests:
    """
    Collection of statistical tests for p-curve analysis.
    """

    @staticmethod
    def binomial_test(p_values: np.ndarray, cutoff: float = 0.05) -> Dict:
        """
        Binomial test for right-skewness.

        Parameters
        ----------
        p_values : np.ndarray
            Array of p-values
        cutoff : float
            Cutoff for p-value range

        Returns
        -------
        dict
            Test results
        """
        p_in_range = p_values[p_values < cutoff]
        pp_values = p_in_range / cutoff

        # Count in lower half
        n_lower = np.sum(pp_values < 0.5)
        n_total = len(pp_values)

        # Binomial test
        p_value = 1 - stats.binom.cdf(n_lower - 1, n_total, 0.5)

        return {
            'n_lower': n_lower,
            'n_total': n_total,
            'p_value': p_value,
            'significant': p_value < 0.05,
        }

    @staticmethod
    def stouffer_test(p_values: np.ndarray, cutoff: float = 0.05) -> Dict:
        """
        Stouffer's method for combining p-values.

        Parameters
        ----------
        p_values : np.ndarray
            Array of p-values
        cutoff : float
            Cutoff for p-value range

        Returns
        -------
        dict
            Test results
        """
        p_in_range = p_values[p_values < cutoff]
        pp_values = p_in_range / cutoff

        # Convert to z-scores
        z_scores = stats.norm.ppf(1 - pp_values)

        # Combine
        z_combined = np.sum(z_scores) / np.sqrt(len(z_scores))
        p_value = 1 - stats.norm.cdf(z_combined)

        return {
            'z_combined': z_combined,
            'p_value': p_value,
            'significant': p_value < 0.05,
        }

    @staticmethod
    def fisher_test(p_values: np.ndarray) -> Dict:
        """
        Fisher's method for combining p-values.

        Parameters
        ----------
        p_values : np.ndarray
            Array of p-values

        Returns
        -------
        dict
            Test results
        """
        # Fisher's method
        chi2_stat = -2 * np.sum(np.log(p_values))
        df = 2 * len(p_values)
        p_value = 1 - stats.chi2.cdf(chi2_stat, df)

        return {
            'chi2_statistic': chi2_stat,
            'df': df,
            'p_value': p_value,
            'significant': p_value < 0.05,
        }

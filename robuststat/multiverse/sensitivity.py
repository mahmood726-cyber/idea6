"""
Sensitivity analysis tools for multiverse analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from scipy import stats


class SensitivityAnalyzer:
    """
    Tools for sensitivity analysis in multiverse framework.
    """

    @staticmethod
    def variance_decomposition(
        results: pd.DataFrame,
        choice_columns: List[str]
    ) -> pd.DataFrame:
        """
        Decompose variance in results by analytical choices.

        Parameters
        ----------
        results : pd.DataFrame
            Multiverse results
        choice_columns : list
            Columns representing analytical choices

        Returns
        -------
        pd.DataFrame
            Variance decomposition
        """
        decomposition = []

        total_var = results['coefficient'].var()

        for col in choice_columns:
            # Between-group variance
            group_means = results.groupby(col)['coefficient'].mean()
            group_sizes = results.groupby(col).size()

            between_var = np.sum(
                group_sizes * (group_means - results['coefficient'].mean()) ** 2
            ) / (len(results) - 1)

            pct_explained = (between_var / total_var) * 100 if total_var > 0 else 0

            decomposition.append({
                'Choice': col,
                'Between_Variance': between_var,
                'Percent_Explained': pct_explained,
            })

        return pd.DataFrame(decomposition).sort_values('Percent_Explained', ascending=False)

    @staticmethod
    def leave_one_out_analysis(
        results: pd.DataFrame,
        choice_column: str
    ) -> Dict:
        """
        Leave-one-out sensitivity analysis.

        Parameters
        ----------
        results : pd.DataFrame
            Multiverse results
        choice_column : str
            Choice to analyze

        Returns
        -------
        dict
            Leave-one-out statistics
        """
        unique_choices = results[choice_column].unique()

        loo_stats = {}

        for choice in unique_choices:
            # Remove this choice
            subset = results[results[choice_column] != choice]

            if len(subset) > 0:
                loo_stats[str(choice)] = {
                    'median': subset['coefficient'].median(),
                    'mean': subset['coefficient'].mean(),
                    'pct_sig': subset['significant'].mean() * 100,
                }

        return loo_stats

    @staticmethod
    def calculate_voe(coefficients: np.ndarray) -> float:
        """
        Calculate Vibration of Effects.

        Parameters
        ----------
        coefficients : np.ndarray
            Array of effect estimates

        Returns
        -------
        float
            VoE metric
        """
        p5 = np.percentile(coefficients, 5)
        p95 = np.percentile(coefficients, 95)

        if p5 != 0:
            return abs(p95 / p5)
        else:
            return np.inf

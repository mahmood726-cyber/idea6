"""
Multiverse Analysis Framework

Implementation of multiverse analysis (Steegen et al., 2016) for systematic
exploration of analytical decisions and sensitivity analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from itertools import product
import warnings
from scipy import stats
from tqdm import tqdm
import json


class MultiverseAnalyzer:
    """
    Multiverse Analysis Framework for sensitivity analysis.

    Based on Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016).
    Increasing transparency through a multiverse analysis.
    Perspectives on Psychological Science, 11(5), 702-712.

    Multiverse analysis explores all reasonable ways of analyzing data to assess
    how sensitive conclusions are to arbitrary analytical decisions.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset to analyze
    universe_spec : dict
        Dictionary specifying the analytical universe:
        {
            'data_processing': {
                'outlier_removal': [None, 'iqr', 'z_score', 'custom'],
                'missing_data': ['listwise', 'mean_impute', 'mice'],
                'transformations': [None, 'log', 'sqrt']
            },
            'model_specification': {
                'covariates': [['x1'], ['x1', 'x2'], ['x1', 'x2', 'x3']],
                'model_type': ['ols', 'robust', 'mixed'],
                'interactions': [False, True]
            },
            'inference': {
                'alpha': [0.05, 0.01],
                'adjustment': [None, 'bonferroni', 'fdr']
            }
        }
    outcome : str
        Outcome variable
    predictor : str
        Main predictor of interest
    """

    def __init__(
        self,
        data: pd.DataFrame,
        universe_spec: Dict[str, Dict[str, List[Any]]],
        outcome: str,
        predictor: str,
    ):
        self.data = data.copy()
        self.universe_spec = universe_spec
        self.outcome = outcome
        self.predictor = predictor

        # Results storage
        self.multiverse_results = None
        self.universe_paths = []

    def generate_universe(self) -> List[Dict]:
        """
        Generate all possible analytical paths in the multiverse.

        Returns
        -------
        list of dict
            Each dict represents one complete analytical path
        """
        # Flatten the nested universe specification
        all_choices = {}

        for category, choices in self.universe_spec.items():
            for choice_name, options in choices.items():
                key = f"{category}.{choice_name}"
                all_choices[key] = options

        # Generate all combinations
        keys = list(all_choices.keys())
        values = list(all_choices.values())

        all_paths = []
        for combo in product(*values):
            path = dict(zip(keys, combo))
            all_paths.append(path)

        print(f"Generated {len(all_paths)} analytical paths in the multiverse")
        return all_paths

    def explore(
        self,
        analysis_func: Optional[Callable] = None,
        parallel: bool = False,
        n_jobs: int = -1,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Explore the entire multiverse of analyses.

        Parameters
        ----------
        analysis_func : callable, optional
            Custom analysis function. Should take (data, path) and return dict of results
        parallel : bool
            Whether to run in parallel (requires joblib)
        n_jobs : int
            Number of parallel jobs (-1 = all cores)
        verbose : bool
            Whether to show progress

        Returns
        -------
        pd.DataFrame
            Results from all analytical paths
        """
        all_paths = self.generate_universe()
        self.universe_paths = all_paths

        if parallel:
            try:
                from joblib import Parallel, delayed
                results_list = Parallel(n_jobs=n_jobs)(
                    delayed(self._run_path)(path, analysis_func)
                    for path in tqdm(all_paths, disable=not verbose, desc="Exploring multiverse")
                )
            except ImportError:
                warnings.warn("joblib not installed. Running sequentially.")
                parallel = False

        if not parallel:
            results_list = []
            iterator = tqdm(all_paths, desc="Exploring multiverse") if verbose else all_paths

            for path_idx, path in enumerate(iterator):
                try:
                    result = self._run_path(path, analysis_func)
                    result['path_id'] = path_idx
                    results_list.append(result)
                except Exception as e:
                    warnings.warn(f"Path {path_idx} failed: {str(e)}")
                    continue

        self.multiverse_results = pd.DataFrame(results_list)
        return self.multiverse_results

    def _run_path(
        self,
        path: Dict,
        analysis_func: Optional[Callable] = None
    ) -> Dict:
        """
        Execute one analytical path through the multiverse.

        Parameters
        ----------
        path : dict
            Analytical choices for this path
        analysis_func : callable, optional
            Custom analysis function

        Returns
        -------
        dict
            Results from this path
        """
        # Process data according to path
        processed_data = self._process_data(path)

        # Run analysis
        if analysis_func is not None:
            result = analysis_func(processed_data, path)
        else:
            result = self._default_analysis(processed_data, path)

        # Add path information to results
        for key, value in path.items():
            result[f'choice_{key}'] = str(value)

        return result

    def _process_data(self, path: Dict) -> pd.DataFrame:
        """
        Process data according to analytical path choices.

        Parameters
        ----------
        path : dict
            Analytical choices

        Returns
        -------
        pd.DataFrame
            Processed data
        """
        data = self.data.copy()

        # Outlier removal
        outlier_method = path.get('data_processing.outlier_removal')
        if outlier_method == 'iqr':
            data = self._remove_outliers_iqr(data, self.outcome)
        elif outlier_method == 'z_score':
            data = self._remove_outliers_zscore(data, self.outcome)
        elif outlier_method == 'percentile':
            data = self._remove_outliers_percentile(data, self.outcome)

        # Missing data handling
        missing_method = path.get('data_processing.missing_data')
        if missing_method == 'listwise':
            data = data.dropna()
        elif missing_method == 'mean_impute':
            data = data.fillna(data.mean())
        elif missing_method == 'median_impute':
            data = data.fillna(data.median())

        # Transformations
        transform = path.get('data_processing.transformations')
        if transform == 'log':
            data[self.outcome] = np.log(data[self.outcome] + 1)
        elif transform == 'sqrt':
            data[self.outcome] = np.sqrt(np.abs(data[self.outcome]))
        elif transform == 'standardize':
            data[self.outcome] = (data[self.outcome] - data[self.outcome].mean()) / data[self.outcome].std()

        return data

    def _remove_outliers_iqr(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return data[(data[column] >= lower) & (data[column] <= upper)]

    def _remove_outliers_zscore(self, data: pd.DataFrame, column: str, threshold: float = 3) -> pd.DataFrame:
        """Remove outliers using z-score method."""
        z_scores = np.abs(stats.zscore(data[column].dropna()))
        return data[z_scores < threshold]

    def _remove_outliers_percentile(self, data: pd.DataFrame, column: str, lower: float = 1, upper: float = 99) -> pd.DataFrame:
        """Remove outliers using percentile method."""
        lower_bound = data[column].quantile(lower / 100)
        upper_bound = data[column].quantile(upper / 100)
        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

    def _default_analysis(self, data: pd.DataFrame, path: Dict) -> Dict:
        """
        Default analysis function (OLS regression).

        Parameters
        ----------
        data : pd.DataFrame
            Processed data
        path : dict
            Analytical path

        Returns
        -------
        dict
            Analysis results
        """
        import statsmodels.formula.api as smf

        # Build model formula
        covariates = path.get('model_specification.covariates', [])
        interactions = path.get('model_specification.interactions', False)

        if isinstance(covariates, str):
            covariates = eval(covariates)  # Convert string representation back to list

        formula_parts = [self.predictor]

        if covariates:
            formula_parts.extend(covariates)

        if interactions and len(covariates) > 0:
            formula_parts.append(f"{self.predictor}:{covariates[0]}")

        formula = f"{self.outcome} ~ " + " + ".join(formula_parts)

        # Fit model
        model_type = path.get('model_specification.model_type', 'ols')

        try:
            if model_type == 'ols':
                model = smf.ols(formula, data=data).fit()
            elif model_type == 'robust':
                model = smf.ols(formula, data=data).fit(cov_type='HC3')
            elif model_type == 'logit':
                model = smf.logit(formula, data=data).fit(disp=False)
            else:
                model = smf.ols(formula, data=data).fit()

            # Extract results
            coef = model.params[self.predictor]
            se = model.bse[self.predictor]
            t_stat = model.tvalues[self.predictor]
            p_value = model.pvalues[self.predictor]
            ci = model.conf_int().loc[self.predictor]

            # Apply multiple testing correction if specified
            alpha = path.get('inference.alpha', 0.05)
            adjustment = path.get('inference.adjustment')

            if adjustment == 'bonferroni':
                adjusted_alpha = alpha / len(self.universe_paths) if self.universe_paths else alpha
                significant = p_value < adjusted_alpha
            elif adjustment == 'fdr':
                # Would need all p-values for FDR, so skip for now
                significant = p_value < alpha
            else:
                significant = p_value < alpha

            return {
                'coefficient': coef,
                'std_error': se,
                't_statistic': t_stat,
                'p_value': p_value,
                'ci_lower': ci[0],
                'ci_upper': ci[1],
                'significant': significant,
                'n_obs': int(model.nobs),
                'r_squared': getattr(model, 'rsquared', np.nan),
            }

        except Exception as e:
            return {
                'coefficient': np.nan,
                'std_error': np.nan,
                't_statistic': np.nan,
                'p_value': np.nan,
                'ci_lower': np.nan,
                'ci_upper': np.nan,
                'significant': False,
                'n_obs': len(data),
                'r_squared': np.nan,
                'error': str(e),
            }

    def get_summary(self) -> pd.DataFrame:
        """
        Get summary of multiverse results.

        Returns
        -------
        pd.DataFrame
            Summary statistics
        """
        if self.multiverse_results is None:
            raise ValueError("No results available. Run explore() first.")

        summary = {
            'Total Paths': len(self.multiverse_results),
            'Median Coefficient': self.multiverse_results['coefficient'].median(),
            'Mean Coefficient': self.multiverse_results['coefficient'].mean(),
            'SD Coefficient': self.multiverse_results['coefficient'].std(),
            'Min Coefficient': self.multiverse_results['coefficient'].min(),
            'Max Coefficient': self.multiverse_results['coefficient'].max(),
            'Percent Significant': 100 * self.multiverse_results['significant'].mean(),
            'Percent Positive Effect': 100 * (self.multiverse_results['coefficient'] > 0).mean(),
            'Percent Negative Effect': 100 * (self.multiverse_results['coefficient'] < 0).mean(),
            'Median p-value': self.multiverse_results['p_value'].median(),
            '25th Percentile Coef': self.multiverse_results['coefficient'].quantile(0.25),
            '75th Percentile Coef': self.multiverse_results['coefficient'].quantile(0.75),
        }

        return pd.DataFrame([summary]).T.rename(columns={0: 'Value'})

    def calculate_fragility(self) -> Dict:
        """
        Calculate analytical fragility metrics.

        Fragility measures how sensitive conclusions are to analytical choices.

        Returns
        -------
        dict
            Fragility metrics
        """
        if self.multiverse_results is None:
            raise ValueError("No results available.")

        results = self.multiverse_results

        # Inferential fragility: % of paths that are significant
        inferential_fragility = 1 - results['significant'].mean()

        # Descriptive fragility: coefficient of variation
        descriptive_fragility = results['coefficient'].std() / abs(results['coefficient'].mean()) if results['coefficient'].mean() != 0 else np.inf

        # Sign fragility: % of paths with different sign from median
        median_sign = np.sign(results['coefficient'].median())
        sign_agreement = (np.sign(results['coefficient']) == median_sign).mean()
        sign_fragility = 1 - sign_agreement

        # Vibration of Effects (VoE): ratio of 95th to 5th percentile
        p95 = results['coefficient'].quantile(0.95)
        p5 = results['coefficient'].quantile(0.05)
        voe = abs(p95 / p5) if p5 != 0 else np.inf

        return {
            'inferential_fragility': inferential_fragility,
            'descriptive_fragility': descriptive_fragility,
            'sign_fragility': sign_fragility,
            'vibration_of_effects': voe,
            'coefficient_range': results['coefficient'].max() - results['coefficient'].min(),
            'iqr_coefficient': results['coefficient'].quantile(0.75) - results['coefficient'].quantile(0.25),
        }

    def visualize_multiverse(self, figsize: Tuple[int, int] = (16, 10), show: bool = True):
        """
        Create comprehensive multiverse visualization.

        Parameters
        ----------
        figsize : tuple
            Figure size
        show : bool
            Whether to display the plot

        Returns
        -------
        matplotlib.figure.Figure
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        if self.multiverse_results is None:
            raise ValueError("No results to plot. Run explore() first.")

        results = self.multiverse_results.sort_values('coefficient').reset_index(drop=True)

        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], width_ratios=[3, 1])

        # Main multiverse plot
        ax1 = fig.add_subplot(gs[0, 0])
        x = np.arange(len(results))
        y = results['coefficient']

        # Color by significance
        colors = ['red' if not sig else 'blue' for sig in results['significant']]
        ax1.scatter(x, y, c=colors, alpha=0.6, s=20)

        # Add confidence intervals
        if 'ci_lower' in results.columns and 'ci_upper' in results.columns:
            ax1.fill_between(x, results['ci_lower'], results['ci_upper'],
                           alpha=0.2, color='gray')

        ax1.axhline(y=0, color='black', linestyle='--', linewidth=2, alpha=0.7)
        ax1.axhline(y=results['coefficient'].median(), color='green',
                   linestyle='-', linewidth=2,
                   label=f'Median = {results["coefficient"].median():.3f}')

        ax1.set_ylabel('Effect Size (Coefficient)', fontsize=12, fontweight='bold')
        ax1.set_title('Multiverse Analysis: All Analytical Paths', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Distribution of coefficients
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(results['coefficient'], bins=30, orientation='horizontal',
                alpha=0.7, color='steelblue', edgecolor='black')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.axhline(y=results['coefficient'].median(), color='green',
                   linestyle='-', linewidth=2, alpha=0.7)
        ax2.set_xlabel('Frequency', fontsize=10)
        ax2.set_ylabel('Coefficient', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Specification choices heatmap
        ax3 = fig.add_subplot(gs[1, :])
        choice_cols = [col for col in results.columns if col.startswith('choice_')]

        if choice_cols:
            # Create binary matrix for visualization
            n_choices = min(len(choice_cols), 6)
            choice_matrix = np.zeros((n_choices, len(results)))

            for i, col in enumerate(choice_cols[:n_choices]):
                unique_vals = results[col].unique()
                for j, val in enumerate(unique_vals):
                    mask = results[col] == val
                    choice_matrix[i, mask] = j

            im = ax3.imshow(choice_matrix, aspect='auto', cmap='tab20', interpolation='nearest')
            ax3.set_yticks(range(n_choices))
            ax3.set_yticklabels([col.replace('choice_', '').replace('.', '\n')
                                for col in choice_cols[:n_choices]], fontsize=8)
            ax3.set_ylabel('Analytical Choices', fontsize=10, fontweight='bold')
            ax3.set_xlabel('Analytical Paths (sorted by effect size)', fontsize=10)

        # P-value distribution
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.hist(results['p_value'], bins=50, alpha=0.7, color='coral', edgecolor='black')
        ax4.axvline(x=0.05, color='red', linestyle='--', linewidth=2,
                   label='α = 0.05')
        ax4.set_xlabel('P-value', fontsize=10)
        ax4.set_ylabel('Frequency', fontsize=10)
        ax4.set_title('Distribution of P-values Across Multiverse', fontsize=11, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # Summary statistics box
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')

        fragility = self.calculate_fragility()
        summary_text = f"""
        MULTIVERSE SUMMARY
        {'='*25}
        Total Paths: {len(results):,}

        Median β: {results['coefficient'].median():.3f}
        Range: [{results['coefficient'].min():.3f},
                {results['coefficient'].max():.3f}]

        % Significant: {100*results['significant'].mean():.1f}%

        Fragility Metrics:
        • Inferential: {fragility['inferential_fragility']:.2f}
        • Descriptive: {fragility['descriptive_fragility']:.2f}
        • Sign: {fragility['sign_fragility']:.2f}
        """

        ax5.text(0.1, 0.9, summary_text, transform=ax5.transAxes,
                fontsize=9, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if show:
            plt.show()

        return fig

    def identify_influential_choices(self, n: int = 5) -> pd.DataFrame:
        """
        Identify which analytical choices most influence results.

        Parameters
        ----------
        n : int
            Number of top influential choices to return

        Returns
        -------
        pd.DataFrame
            Most influential choices ranked by impact
        """
        if self.multiverse_results is None:
            raise ValueError("No results available.")

        choice_cols = [col for col in self.multiverse_results.columns
                      if col.startswith('choice_')]

        influence = []

        for col in choice_cols:
            # ANOVA-style analysis
            groups = self.multiverse_results.groupby(col)['coefficient']

            # Between-group variance
            overall_mean = self.multiverse_results['coefficient'].mean()
            between_var = sum(
                len(group) * (group.mean() - overall_mean) ** 2
                for _, group in groups
            ) / (len(groups) - 1)

            # Within-group variance
            within_var = sum(
                sum((val - group.mean()) ** 2 for val in group)
                for _, group in groups
            ) / (len(self.multiverse_results) - len(groups))

            # F-statistic
            if within_var > 0:
                f_stat = between_var / within_var
                # Approximate p-value
                df1 = len(groups) - 1
                df2 = len(self.multiverse_results) - len(groups)
                p_value = 1 - stats.f.cdf(f_stat, df1, df2)
            else:
                f_stat = np.inf
                p_value = 0.0

            influence.append({
                'Choice': col.replace('choice_', ''),
                'F-statistic': f_stat,
                'P-value': p_value,
                'Between-group var': between_var,
                'Effect size (η²)': between_var / (between_var + within_var) if (between_var + within_var) > 0 else 0,
                'N options': len(groups),
            })

        influence_df = pd.DataFrame(influence).sort_values('F-statistic', ascending=False)

        return influence_df.head(n)

    def export_multiverse(self, filepath: str):
        """
        Export complete multiverse results and specification to file.

        Parameters
        ----------
        filepath : str
            Path to save results (supports .csv, .xlsx, .json)
        """
        if self.multiverse_results is None:
            raise ValueError("No results to export.")

        if filepath.endswith('.csv'):
            self.multiverse_results.to_csv(filepath, index=False)
        elif filepath.endswith('.xlsx'):
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                self.multiverse_results.to_excel(writer, sheet_name='Results', index=False)
                self.get_summary().to_excel(writer, sheet_name='Summary')
                self.identify_influential_choices(10).to_excel(writer, sheet_name='Influential Choices', index=False)
        elif filepath.endswith('.json'):
            export_data = {
                'universe_specification': self.universe_spec,
                'results': self.multiverse_results.to_dict('records'),
                'summary': self.get_summary().to_dict(),
                'fragility': self.calculate_fragility(),
            }
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        else:
            raise ValueError("Unsupported file format. Use .csv, .xlsx, or .json")

        print(f"Multiverse results exported to {filepath}")

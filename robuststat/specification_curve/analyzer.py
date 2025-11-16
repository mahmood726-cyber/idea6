"""
Specification Curve Analysis

Implementation of specification curve analysis (Simonsohn, Simmons, & Nelson, 2020)
for assessing robustness of findings across analytical choices.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from itertools import product
import warnings
from scipy import stats
from tqdm import tqdm
import statsmodels.api as sm
import statsmodels.formula.api as smf


class SpecificationCurve:
    """
    Specification Curve Analyzer for robustness assessment.

    Based on Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020).
    Specification curve analysis. Nature Human Behaviour, 4(11), 1208-1214.

    Specification curve analysis involves:
    1. Identifying all reasonable specifications
    2. Running all specifications
    3. Displaying results as a specification curve
    4. Conducting inferential tests

    Parameters
    ----------
    data : pd.DataFrame
        The dataset to analyze
    outcome : str or list
        Outcome variable(s) to test
    predictor : str
        Main predictor of interest
    specifications : dict
        Dictionary of specification choices:
        {
            'controls': [list of control variable sets],
            'subsets': [list of data subsetting rules],
            'models': [list of model types],
            'transformations': [list of transformations]
        }
    """

    def __init__(
        self,
        data: pd.DataFrame,
        outcome: Union[str, List[str]],
        predictor: str,
        specifications: Dict[str, List[Any]],
    ):
        self.data = data.copy()
        self.outcome = [outcome] if isinstance(outcome, str) else outcome
        self.predictor = predictor
        self.specifications = specifications

        # Results storage
        self.results = None
        self.specification_details = []

    def generate_all_specifications(self) -> List[Dict]:
        """
        Generate all combinations of specifications.

        Returns
        -------
        list of dict
            Each dict contains one specification combination
        """
        # Extract specification dimensions
        spec_dict = {}

        # Outcomes
        spec_dict['outcome'] = self.outcome

        # Controls
        if 'controls' in self.specifications:
            spec_dict['controls'] = self.specifications['controls']
        else:
            spec_dict['controls'] = [[]]  # No controls

        # Subsets/samples
        if 'subsets' in self.specifications:
            spec_dict['subsets'] = self.specifications['subsets']
        else:
            spec_dict['subsets'] = [None]

        # Models
        if 'models' in self.specifications:
            spec_dict['models'] = self.specifications['models']
        else:
            spec_dict['models'] = ['ols']

        # Transformations
        if 'transformations' in self.specifications:
            spec_dict['transformations'] = self.specifications['transformations']
        else:
            spec_dict['transformations'] = [None]

        # Additional custom specifications
        other_specs = {}
        for key in self.specifications:
            if key not in ['controls', 'subsets', 'models', 'transformations']:
                other_specs[key] = self.specifications[key]

        # Generate all combinations
        keys = list(spec_dict.keys()) + list(other_specs.keys())
        values = list(spec_dict.values()) + list(other_specs.values())

        all_specs = []
        for combo in product(*values):
            spec = dict(zip(keys, combo))
            all_specs.append(spec)

        print(f"Generated {len(all_specs)} total specifications")
        return all_specs

    def run_all_specifications(
        self,
        custom_model_func: Optional[Callable] = None,
        n_bootstrap: int = 0,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Run all specifications and collect results.

        Parameters
        ----------
        custom_model_func : callable, optional
            Custom function to run models. Should take (data, spec) and return result dict
        n_bootstrap : int
            Number of bootstrap iterations for inference (0 = no bootstrap)
        verbose : bool
            Whether to show progress bar

        Returns
        -------
        pd.DataFrame
            Results from all specifications
        """
        all_specs = self.generate_all_specifications()

        results_list = []

        iterator = tqdm(all_specs, desc="Running specifications") if verbose else all_specs

        for spec_idx, spec in enumerate(iterator):
            try:
                if custom_model_func is not None:
                    result = custom_model_func(self.data, spec)
                else:
                    result = self._run_specification(spec)

                result['spec_id'] = spec_idx
                result['specification'] = str(spec)

                # Add specification details
                for key, value in spec.items():
                    result[f'spec_{key}'] = str(value)

                results_list.append(result)

            except Exception as e:
                warnings.warn(f"Specification {spec_idx} failed: {str(e)}")
                continue

        self.results = pd.DataFrame(results_list)
        self.specification_details = all_specs

        # Run inference if requested
        if n_bootstrap > 0:
            self._run_inference(n_bootstrap)

        return self.results

    def _run_specification(self, spec: Dict) -> Dict:
        """
        Run a single specification.

        Parameters
        ----------
        spec : dict
            Specification parameters

        Returns
        -------
        dict
            Results including coefficient, SE, p-value, etc.
        """
        # Get data subset
        data = self._apply_subset(self.data, spec.get('subsets'))

        # Apply transformations
        data = self._apply_transformation(data, spec)

        # Build model formula
        outcome = spec['outcome']
        controls = spec.get('controls', [])
        model_type = spec.get('models', 'ols')

        # Create formula
        if controls:
            controls_str = ' + '.join(controls)
            formula = f"{outcome} ~ {self.predictor} + {controls_str}"
        else:
            formula = f"{outcome} ~ {self.predictor}"

        # Fit model
        if model_type == 'ols':
            model = smf.ols(formula, data=data).fit()
        elif model_type == 'robust':
            model = smf.ols(formula, data=data).fit(cov_type='HC3')
        elif model_type == 'logit':
            model = smf.logit(formula, data=data).fit(disp=False)
        elif model_type == 'poisson':
            model = smf.poisson(formula, data=data).fit(disp=False)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Extract results for predictor of interest
        coef = model.params[self.predictor]
        se = model.bse[self.predictor]
        t_stat = model.tvalues[self.predictor]
        p_value = model.pvalues[self.predictor]

        # Confidence interval
        ci = model.conf_int().loc[self.predictor]

        return {
            'coefficient': coef,
            'std_error': se,
            't_statistic': t_stat,
            'p_value': p_value,
            'ci_lower': ci[0],
            'ci_upper': ci[1],
            'n_obs': int(model.nobs),
            'r_squared': getattr(model, 'rsquared', np.nan),
            'significant': p_value < 0.05,
        }

    def _apply_subset(self, data: pd.DataFrame, subset_rule: Optional[Any]) -> pd.DataFrame:
        """Apply data subsetting rule."""
        if subset_rule is None:
            return data

        if callable(subset_rule):
            return data[subset_rule(data)]
        elif isinstance(subset_rule, str):
            # Assume it's a query string
            return data.query(subset_rule)
        else:
            return data

    def _apply_transformation(self, data: pd.DataFrame, spec: Dict) -> pd.DataFrame:
        """Apply variable transformations."""
        data = data.copy()
        transform = spec.get('transformations')

        if transform is None or transform == 'none':
            return data

        outcome = spec['outcome']

        if transform == 'log':
            data[outcome] = np.log(data[outcome] + 1)
        elif transform == 'sqrt':
            data[outcome] = np.sqrt(data[outcome])
        elif transform == 'standardize':
            data[outcome] = (data[outcome] - data[outcome].mean()) / data[outcome].std()
        elif callable(transform):
            data[outcome] = transform(data[outcome])

        return data

    def _run_inference(self, n_bootstrap: int = 1000):
        """
        Run permutation-based inference for specification curve.

        Tests whether the median/mean coefficient is significantly different from zero.

        Parameters
        ----------
        n_bootstrap : int
            Number of permutations
        """
        print(f"Running inference with {n_bootstrap} permutations...")

        # Observed median coefficient
        obs_median = self.results['coefficient'].median()
        obs_mean = self.results['coefficient'].mean()

        # Permutation test
        null_medians = []
        null_means = []

        for _ in tqdm(range(n_bootstrap), desc="Permutation test"):
            # Permute the predictor
            permuted_data = self.data.copy()
            permuted_data[self.predictor] = np.random.permutation(permuted_data[self.predictor])

            # Run random subset of specifications (for speed)
            sample_specs = np.random.choice(
                len(self.specification_details),
                size=min(100, len(self.specification_details)),
                replace=False
            )

            coeffs = []
            for idx in sample_specs:
                spec = self.specification_details[idx]
                try:
                    # Save original data
                    original_data = self.data
                    self.data = permuted_data

                    result = self._run_specification(spec)
                    coeffs.append(result['coefficient'])

                    # Restore original data
                    self.data = original_data
                except:
                    continue

            if coeffs:
                null_medians.append(np.median(coeffs))
                null_means.append(np.mean(coeffs))

        # Calculate p-values
        null_medians = np.array(null_medians)
        null_means = np.array(null_means)

        p_median = np.mean(np.abs(null_medians) >= np.abs(obs_median))
        p_mean = np.mean(np.abs(null_means) >= np.abs(obs_mean))

        self.inference_results = {
            'observed_median': obs_median,
            'observed_mean': obs_mean,
            'p_value_median': p_median,
            'p_value_mean': p_mean,
            'null_distribution_median': null_medians,
            'null_distribution_mean': null_means,
        }

        print(f"Inference complete:")
        print(f"  Median coefficient: {obs_median:.4f}, p = {p_median:.4f}")
        print(f"  Mean coefficient: {obs_mean:.4f}, p = {p_mean:.4f}")

    def plot(self, figsize: Tuple[int, int] = (14, 10), show: bool = True):
        """
        Create specification curve plot.

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

        if self.results is None:
            raise ValueError("No results to plot. Run run_all_specifications() first.")

        # Sort by coefficient
        results_sorted = self.results.sort_values('coefficient').reset_index(drop=True)

        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.05)

        # Top panel: Specification curve
        ax1 = fig.add_subplot(gs[0])

        x = np.arange(len(results_sorted))
        y = results_sorted['coefficient']
        colors = ['red' if not sig else 'blue'
                 for sig in results_sorted['significant']]

        ax1.scatter(x, y, c=colors, alpha=0.6, s=10)
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)

        # Add confidence intervals
        ax1.fill_between(
            x,
            results_sorted['ci_lower'],
            results_sorted['ci_upper'],
            alpha=0.2,
            color='gray'
        )

        # Add median line
        median_coef = results_sorted['coefficient'].median()
        ax1.axhline(y=median_coef, color='green', linestyle='-',
                   linewidth=2, label=f'Median = {median_coef:.3f}', alpha=0.7)

        ax1.set_ylabel('Effect Size (Coefficient)', fontsize=12, fontweight='bold')
        ax1.set_title('Specification Curve Analysis', fontsize=14, fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticklabels([])

        # Middle panel: Specification choices (e.g., controls)
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # Show which specifications include different choices
        spec_cols = [col for col in results_sorted.columns if col.startswith('spec_')]

        if spec_cols:
            # Create binary indicator matrix
            n_specs = len(results_sorted)
            n_choices = min(len(spec_cols), 5)  # Limit to 5 for visibility

            choice_matrix = np.zeros((n_choices, n_specs))

            for i, col in enumerate(spec_cols[:n_choices]):
                unique_vals = results_sorted[col].unique()
                if len(unique_vals) > 1:
                    # Binary encoding
                    for j, val in enumerate(unique_vals):
                        mask = results_sorted[col] == val
                        choice_matrix[i, mask] = j + 1

            ax2.imshow(choice_matrix, aspect='auto', cmap='Set3', interpolation='nearest')
            ax2.set_yticks(range(n_choices))
            ax2.set_yticklabels([col.replace('spec_', '') for col in spec_cols[:n_choices]])
            ax2.set_ylabel('Specification\nChoices', fontsize=10, fontweight='bold')
            ax2.set_xticklabels([])

        # Bottom panel: Sample size
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        if 'n_obs' in results_sorted.columns:
            ax3.bar(x, results_sorted['n_obs'], color='steelblue', alpha=0.6)
            ax3.set_ylabel('Sample Size', fontsize=10, fontweight='bold')
            ax3.set_xlabel('Specifications (sorted by effect size)', fontsize=12)

        plt.tight_layout()

        if show:
            plt.show()

        return fig

    def get_summary(self) -> pd.DataFrame:
        """
        Get summary statistics of specification curve.

        Returns
        -------
        pd.DataFrame
            Summary statistics
        """
        if self.results is None:
            raise ValueError("No results available. Run run_all_specifications() first.")

        summary = {
            'Total Specifications': len(self.results),
            'Median Coefficient': self.results['coefficient'].median(),
            'Mean Coefficient': self.results['coefficient'].mean(),
            'SD Coefficient': self.results['coefficient'].std(),
            'Min Coefficient': self.results['coefficient'].min(),
            'Max Coefficient': self.results['coefficient'].max(),
            'Percent Significant (p<.05)': 100 * self.results['significant'].mean(),
            'Percent Positive': 100 * (self.results['coefficient'] > 0).mean(),
            'Median p-value': self.results['p_value'].median(),
            'Mean Sample Size': self.results['n_obs'].mean(),
        }

        return pd.DataFrame([summary]).T.rename(columns={0: 'Value'})

    def get_influential_specs(self, n: int = 10) -> pd.DataFrame:
        """
        Identify most influential specification choices.

        Parameters
        ----------
        n : int
            Number of top choices to return

        Returns
        -------
        pd.DataFrame
            Most influential specification choices
        """
        if self.results is None:
            raise ValueError("No results available.")

        spec_cols = [col for col in self.results.columns if col.startswith('spec_')]

        influence = []

        for col in spec_cols:
            unique_vals = self.results[col].unique()

            if len(unique_vals) > 1:
                # Calculate variance in coefficients explained by this choice
                groups = self.results.groupby(col)['coefficient']
                between_var = groups.mean().var()
                within_var = groups.apply(lambda x: x.var()).mean()

                # F-statistic like measure
                if within_var > 0:
                    f_stat = between_var / within_var
                else:
                    f_stat = np.inf

                influence.append({
                    'Specification': col.replace('spec_', ''),
                    'Between-group variance': between_var,
                    'Within-group variance': within_var,
                    'F-statistic': f_stat,
                    'N unique values': len(unique_vals),
                })

        influence_df = pd.DataFrame(influence).sort_values('F-statistic', ascending=False)

        return influence_df.head(n)

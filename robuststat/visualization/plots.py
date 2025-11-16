"""
Advanced visualization functions for robustness analyses
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional, Tuple, Any
import warnings


def plot_pcurve_comparison(
    p_value_sets: Dict[str, np.ndarray],
    figsize: Tuple[int, int] = (14, 6),
    colors: Optional[List[str]] = None
) -> plt.Figure:
    """
    Plot multiple p-curves for comparison.

    Parameters
    ----------
    p_value_sets : dict
        Dictionary mapping labels to arrays of p-values
    figsize : tuple
        Figure size
    colors : list, optional
        Colors for each p-curve

    Returns
    -------
    matplotlib.figure.Figure
    """
    n_sets = len(p_value_sets)

    if colors is None:
        colors = plt.cm.Set2(np.linspace(0, 1, n_sets))

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Left panel: Overlaid histograms
    bins = np.arange(0, 0.051, 0.005)

    for (label, p_vals), color in zip(p_value_sets.items(), colors):
        sig_p = p_vals[p_vals < 0.05]

        axes[0].hist(sig_p, bins=bins, density=True, alpha=0.5,
                    label=label, color=color, edgecolor='black', linewidth=0.5)

    # Add null expectation
    axes[0].axhline(y=20, color='red', linestyle='--', linewidth=2,
                   label='H₀ (uniform)', alpha=0.7)

    axes[0].set_xlabel('p-value', fontsize=12)
    axes[0].set_ylabel('Density', fontsize=12)
    axes[0].set_title('P-Curve Comparison', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Right panel: Cumulative distributions
    for (label, p_vals), color in zip(p_value_sets.items(), colors):
        sig_p = np.sort(p_vals[p_vals < 0.05])
        cumulative = np.arange(1, len(sig_p) + 1) / len(sig_p)

        axes[1].plot(sig_p, cumulative, label=label, color=color,
                    linewidth=2, alpha=0.7)

    # Uniform null
    axes[1].plot([0, 0.05], [0, 1], 'r--', linewidth=2,
                label='H₀ (uniform)', alpha=0.7)

    axes[1].set_xlabel('p-value', fontsize=12)
    axes[1].set_ylabel('Cumulative Proportion', fontsize=12)
    axes[1].set_title('Cumulative P-Curves', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(0, 0.05)
    axes[1].set_ylim(0, 1)

    plt.tight_layout()
    return fig


def plot_specification_curve_advanced(
    results: pd.DataFrame,
    groupby: Optional[str] = None,
    figsize: Tuple[int, int] = (16, 12)
) -> plt.Figure:
    """
    Advanced specification curve plot with grouping and annotations.

    Parameters
    ----------
    results : pd.DataFrame
        Results from SpecificationCurve analysis
    groupby : str, optional
        Column to group specifications by
    figsize : tuple
        Figure size

    Returns
    -------
    matplotlib.figure.Figure
    """
    results_sorted = results.sort_values('coefficient').reset_index(drop=True)

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.08)

    # Panel 1: Main specification curve
    ax1 = fig.add_subplot(gs[0])

    x = np.arange(len(results_sorted))
    y = results_sorted['coefficient']

    if groupby and groupby in results_sorted.columns:
        # Color by group
        groups = results_sorted[groupby].unique()
        colors_map = dict(zip(groups, plt.cm.tab10(np.linspace(0, 1, len(groups)))))
        colors = [colors_map[g] for g in results_sorted[groupby]]

        for group in groups:
            mask = results_sorted[groupby] == group
            ax1.scatter(x[mask], y[mask], c=[colors_map[group]],
                       label=str(group), alpha=0.7, s=30)
    else:
        colors = ['red' if not sig else 'steelblue'
                 for sig in results_sorted['significant']]
        ax1.scatter(x, y, c=colors, alpha=0.6, s=30)

    # Confidence intervals
    if 'ci_lower' in results_sorted.columns:
        ax1.fill_between(x, results_sorted['ci_lower'], results_sorted['ci_upper'],
                        alpha=0.2, color='gray')

    # Reference lines
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.7)

    # Median and quartiles
    median = results_sorted['coefficient'].median()
    q25 = results_sorted['coefficient'].quantile(0.25)
    q75 = results_sorted['coefficient'].quantile(0.75)

    ax1.axhline(y=median, color='green', linestyle='-', linewidth=2.5,
               label=f'Median = {median:.3f}', alpha=0.8)
    ax1.axhline(y=q25, color='orange', linestyle='--', linewidth=1.5,
               label=f'Q1 = {q25:.3f}', alpha=0.6)
    ax1.axhline(y=q75, color='orange', linestyle='--', linewidth=1.5,
               label=f'Q3 = {q75:.3f}', alpha=0.6)

    ax1.set_ylabel('Effect Size', fontsize=13, fontweight='bold')
    ax1.set_title('Specification Curve Analysis', fontsize=15, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_xticklabels([])

    # Panel 2: Sample size
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    if 'n_obs' in results_sorted.columns:
        ax2.bar(x, results_sorted['n_obs'], color='steelblue', alpha=0.6, width=1)
        ax2.set_ylabel('N', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xticklabels([])

    # Panel 3: P-values (log scale)
    ax3 = fig.add_subplot(gs[2], sharex=ax1)

    if 'p_value' in results_sorted.columns:
        # Plot -log10(p) for better visualization
        log_p = -np.log10(results_sorted['p_value'].clip(lower=1e-10))
        ax3.bar(x, log_p, color='coral', alpha=0.7, width=1)
        ax3.axhline(y=-np.log10(0.05), color='red', linestyle='--',
                   linewidth=2, label='p = 0.05', alpha=0.7)
        ax3.set_ylabel('-log₁₀(p)', fontsize=10, fontweight='bold')
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_xticklabels([])

    # Panel 4: R-squared
    ax4 = fig.add_subplot(gs[3], sharex=ax1)

    if 'r_squared' in results_sorted.columns:
        ax4.bar(x, results_sorted['r_squared'], color='seagreen', alpha=0.6, width=1)
        ax4.set_ylabel('R²', fontsize=10, fontweight='bold')
        ax4.set_xlabel('Specifications (sorted by effect size)', fontsize=11)
        ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    return fig


def plot_multiverse_grid(
    results: pd.DataFrame,
    x_dimension: str,
    y_dimension: str,
    metric: str = 'coefficient',
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Create a grid visualization of multiverse results across two dimensions.

    Parameters
    ----------
    results : pd.DataFrame
        Results from MultiverseAnalyzer
    x_dimension : str
        Column name for x-axis grouping
    y_dimension : str
        Column name for y-axis grouping
    metric : str
        Metric to visualize (default: 'coefficient')
    figsize : tuple
        Figure size

    Returns
    -------
    matplotlib.figure.Figure
    """
    # Aggregate results by the two dimensions
    pivot = results.pivot_table(
        index=y_dimension,
        columns=x_dimension,
        values=metric,
        aggfunc='mean'
    )

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Heatmap
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
               ax=axes[0], cbar_kws={'label': metric})
    axes[0].set_title(f'Mean {metric} across Analytical Choices',
                     fontsize=12, fontweight='bold')
    axes[0].set_xlabel(x_dimension, fontsize=11)
    axes[0].set_ylabel(y_dimension, fontsize=11)

    # Count heatmap (significance)
    if 'significant' in results.columns:
        sig_pivot = results.pivot_table(
            index=y_dimension,
            columns=x_dimension,
            values='significant',
            aggfunc='mean'
        )

        sns.heatmap(sig_pivot, annot=True, fmt='.2%', cmap='YlGnBu',
                   ax=axes[1], cbar_kws={'label': '% Significant'}, vmin=0, vmax=1)
        axes[1].set_title('Proportion Significant (p < .05)',
                         fontsize=12, fontweight='bold')
        axes[1].set_xlabel(x_dimension, fontsize=11)
        axes[1].set_ylabel(y_dimension, fontsize=11)

    plt.tight_layout()
    return fig


def plot_robustness_dashboard(
    pcurve_results: Optional[Dict] = None,
    spec_curve_results: Optional[pd.DataFrame] = None,
    multiverse_results: Optional[pd.DataFrame] = None,
    figsize: Tuple[int, int] = (18, 12)
) -> plt.Figure:
    """
    Create a comprehensive robustness analysis dashboard.

    Parameters
    ----------
    pcurve_results : dict, optional
        Results from PCurveAnalyzer
    spec_curve_results : pd.DataFrame, optional
        Results from SpecificationCurve
    multiverse_results : pd.DataFrame, optional
        Results from MultiverseAnalyzer
    figsize : tuple
        Figure size

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    row = 0

    # P-Curve section
    if pcurve_results is not None:
        ax1 = fig.add_subplot(gs[row, 0])
        ax2 = fig.add_subplot(gs[row, 1])
        ax3 = fig.add_subplot(gs[row, 2])

        # P-curve histogram (simplified, would need actual p-values)
        ax1.text(0.5, 0.5, 'P-Curve Analysis\n\nEvidential Value: {}\nPower: {:.0%}'.format(
            'Yes' if pcurve_results.get('evidential_value') else 'No',
            pcurve_results.get('power_estimate', {}).get('estimated_power', 0)
        ), ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax1.set_title('P-Curve Summary', fontweight='bold')
        ax1.axis('off')

        # Test results
        full_p = pcurve_results.get('full_pcurve_test', {}).get('p_value', 1)
        half_p = pcurve_results.get('half_pcurve_test', {}).get('p_value', 1)

        tests = ['Full\n(p<.05)', 'Half\n(p<.025)']
        p_vals = [full_p, half_p]
        colors_test = ['green' if p < 0.05 else 'red' for p in p_vals]

        ax2.bar(tests, [-np.log10(p) for p in p_vals], color=colors_test, alpha=0.7)
        ax2.axhline(y=-np.log10(0.05), color='black', linestyle='--',
                   label='p = .05')
        ax2.set_ylabel('-log₁₀(p-value)', fontweight='bold')
        ax2.set_title('P-Curve Tests', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Power indicator
        power = pcurve_results.get('power_estimate', {}).get('estimated_power', 0)
        ax3.barh(['Estimated\nPower'], [power], color='steelblue', alpha=0.7)
        ax3.set_xlim(0, 1)
        ax3.set_xlabel('Power', fontweight='bold')
        ax3.set_title('Statistical Power', fontweight='bold')
        ax3.axvline(x=0.33, color='orange', linestyle='--', label='33% threshold')
        ax3.axvline(x=0.80, color='green', linestyle='--', label='80% target')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3, axis='x')

        row += 1

    # Specification Curve section
    if spec_curve_results is not None:
        ax4 = fig.add_subplot(gs[row, :2])
        ax5 = fig.add_subplot(gs[row, 2])

        # Mini specification curve
        results_sorted = spec_curve_results.sort_values('coefficient')
        x = np.arange(len(results_sorted))
        y = results_sorted['coefficient']

        colors_spec = ['red' if not sig else 'blue'
                      for sig in results_sorted['significant']]
        ax4.scatter(x, y, c=colors_spec, alpha=0.5, s=10)
        ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax4.axhline(y=results_sorted['coefficient'].median(), color='green',
                   linestyle='-', linewidth=2)

        ax4.set_ylabel('Coefficient', fontweight='bold')
        ax4.set_xlabel('Specifications', fontweight='bold')
        ax4.set_title('Specification Curve', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        # Distribution
        ax5.hist(spec_curve_results['coefficient'], bins=30,
                orientation='horizontal', alpha=0.7, color='steelblue',
                edgecolor='black')
        ax5.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax5.set_xlabel('Frequency', fontweight='bold')
        ax5.set_ylabel('Coefficient', fontweight='bold')
        ax5.set_title('Distribution', fontweight='bold')
        ax5.grid(True, alpha=0.3)

        row += 1

    # Multiverse section
    if multiverse_results is not None:
        ax6 = fig.add_subplot(gs[row, :2])
        ax7 = fig.add_subplot(gs[row, 2])

        # Multiverse curve
        results_sorted = multiverse_results.sort_values('coefficient')
        x = np.arange(len(results_sorted))
        y = results_sorted['coefficient']

        colors_multi = ['red' if not sig else 'blue'
                       for sig in results_sorted['significant']]
        ax6.scatter(x, y, c=colors_multi, alpha=0.5, s=10)
        ax6.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax6.axhline(y=results_sorted['coefficient'].median(), color='green',
                   linestyle='-', linewidth=2)

        ax6.set_ylabel('Coefficient', fontweight='bold')
        ax6.set_xlabel('Analytical Paths', fontweight='bold')
        ax6.set_title('Multiverse Analysis', fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')

        # Fragility metrics
        fragility_data = {
            'Sign\nConsistency': 1 - (1 - (np.sign(multiverse_results['coefficient']) ==
                                          np.sign(multiverse_results['coefficient'].median())).mean()),
            'Inferential\nConsistency': multiverse_results['significant'].mean(),
        }

        ax7.bar(fragility_data.keys(), fragility_data.values(),
               color=['coral', 'seagreen'], alpha=0.7)
        ax7.set_ylim(0, 1)
        ax7.set_ylabel('Proportion', fontweight='bold')
        ax7.set_title('Robustness Metrics', fontweight='bold')
        ax7.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        ax7.grid(True, alpha=0.3, axis='y')

    fig.suptitle('ROBUSTNESS ANALYSIS DASHBOARD', fontsize=16, fontweight='bold', y=0.995)

    return fig


def plot_effect_stability(
    results: pd.DataFrame,
    rolling_window: int = 50,
    figsize: Tuple[int, int] = (14, 6)
) -> plt.Figure:
    """
    Plot the stability of effect estimates across specifications.

    Parameters
    ----------
    results : pd.DataFrame
        Results with coefficients
    rolling_window : int
        Window size for rolling statistics
    figsize : tuple
        Figure size

    Returns
    -------
    matplotlib.figure.Figure
    """
    results_sorted = results.sort_values('coefficient').reset_index(drop=True)

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Cumulative mean and variance
    cumulative_mean = results_sorted['coefficient'].expanding().mean()
    cumulative_std = results_sorted['coefficient'].expanding().std()

    axes[0].plot(cumulative_mean, label='Cumulative Mean', linewidth=2)
    axes[0].fill_between(
        range(len(cumulative_mean)),
        cumulative_mean - cumulative_std,
        cumulative_mean + cumulative_std,
        alpha=0.3,
        label='±1 SD'
    )
    axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Number of Specifications', fontsize=11)
    axes[0].set_ylabel('Effect Size', fontsize=11)
    axes[0].set_title('Cumulative Effect Estimate', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Rolling statistics
    rolling_mean = results_sorted['coefficient'].rolling(window=rolling_window).mean()
    rolling_std = results_sorted['coefficient'].rolling(window=rolling_window).std()

    axes[1].plot(rolling_mean, label=f'{rolling_window}-spec Moving Avg', linewidth=2)
    axes[1].fill_between(
        range(len(rolling_mean)),
        rolling_mean - rolling_std,
        rolling_mean + rolling_std,
        alpha=0.3,
        label='±1 SD'
    )
    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1].set_xlabel('Specification Index', fontsize=11)
    axes[1].set_ylabel('Effect Size', fontsize=11)
    axes[1].set_title(f'Rolling Effect Estimate (window={rolling_window})',
                     fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

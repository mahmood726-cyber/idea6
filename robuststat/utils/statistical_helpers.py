"""Statistical helper functions"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional


def calculate_effect_size(
    group1: np.ndarray,
    group2: np.ndarray,
    method: str = 'cohen_d'
) -> float:
    """
    Calculate effect size between two groups.

    Parameters
    ----------
    group1 : np.ndarray
        First group
    group2 : np.ndarray
        Second group
    method : str
        Method: 'cohen_d', 'hedges_g', 'glass_delta'

    Returns
    -------
    float
        Effect size
    """
    mean1 = np.mean(group1)
    mean2 = np.mean(group2)
    std1 = np.std(group1, ddof=1)
    std2 = np.std(group2, ddof=1)

    if method == 'cohen_d':
        # Pooled standard deviation
        n1, n2 = len(group1), len(group2)
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        return (mean1 - mean2) / pooled_std

    elif method == 'hedges_g':
        # Cohen's d with small sample correction
        n1, n2 = len(group1), len(group2)
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        d = (mean1 - mean2) / pooled_std
        # Correction factor
        correction = 1 - (3 / (4 * (n1 + n2) - 9))
        return d * correction

    elif method == 'glass_delta':
        # Use control group SD
        return (mean1 - mean2) / std2

    else:
        raise ValueError(f"Unknown method: {method}")


def bootstrap_ci(
    data: np.ndarray,
    statistic: callable = np.mean,
    n_bootstrap: int = 10000,
    confidence_level: float = 0.95,
    random_state: Optional[int] = None
) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval.

    Parameters
    ----------
    data : np.ndarray
        Data to bootstrap
    statistic : callable
        Statistic function to compute
    n_bootstrap : int
        Number of bootstrap samples
    confidence_level : float
        Confidence level (e.g., 0.95 for 95%)
    random_state : int, optional
        Random seed

    Returns
    -------
    tuple
        (point_estimate, lower_ci, upper_ci)
    """
    if random_state is not None:
        np.random.seed(random_state)

    n = len(data)
    bootstrap_stats = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic(sample))

    bootstrap_stats = np.array(bootstrap_stats)

    # Calculate percentile confidence interval
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100

    ci_lower = np.percentile(bootstrap_stats, lower_percentile)
    ci_upper = np.percentile(bootstrap_stats, upper_percentile)
    point_estimate = statistic(data)

    return point_estimate, ci_lower, ci_upper


def permutation_test(
    group1: np.ndarray,
    group2: np.ndarray,
    n_permutations: int = 10000,
    statistic: callable = None,
    random_state: Optional[int] = None
) -> Tuple[float, float]:
    """
    Perform permutation test.

    Parameters
    ----------
    group1 : np.ndarray
        First group
    group2 : np.ndarray
        Second group
    n_permutations : int
        Number of permutations
    statistic : callable, optional
        Test statistic function (default: difference in means)
    random_state : int, optional
        Random seed

    Returns
    -------
    tuple
        (observed_statistic, p_value)
    """
    if random_state is not None:
        np.random.seed(random_state)

    if statistic is None:
        statistic = lambda g1, g2: np.mean(g1) - np.mean(g2)

    # Observed statistic
    observed = statistic(group1, group2)

    # Combine groups
    combined = np.concatenate([group1, group2])
    n1 = len(group1)

    # Permutation distribution
    perm_stats = []

    for _ in range(n_permutations):
        # Shuffle combined data
        shuffled = np.random.permutation(combined)

        # Split into two groups
        perm_group1 = shuffled[:n1]
        perm_group2 = shuffled[n1:]

        perm_stats.append(statistic(perm_group1, perm_group2))

    perm_stats = np.array(perm_stats)

    # Two-tailed p-value
    p_value = np.mean(np.abs(perm_stats) >= np.abs(observed))

    return observed, p_value

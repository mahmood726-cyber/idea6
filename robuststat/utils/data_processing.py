"""Data processing utilities"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union, Optional
from numbers import Real


def remove_outliers(
    data: Union[np.ndarray, pd.Series],
    method: str = 'iqr',
    threshold: float = 1.5
) -> np.ndarray:
    """
    Remove outliers from data using various methods.

    Parameters
    ----------
    data : array-like
        Data to process
    method : str
        Method to use: 'iqr', 'z_score', 'percentile'
    threshold : float
        Threshold for outlier detection

    Returns
    -------
    np.ndarray
        Boolean mask where True indicates non-outliers
    """
    if method not in ('iqr', 'z_score', 'percentile'):
        raise ValueError(f"Unknown method: {method}")
    if (isinstance(threshold, (bool, np.bool_)) or not isinstance(threshold, Real)
            or not np.isfinite(threshold)
            or threshold < 0 or (method == 'percentile' and threshold > 50)):
        raise ValueError("threshold must be finite and non-negative (at most 50 for percentile)")
    data = np.asarray(data, dtype=float)
    if data.ndim != 1:
        raise ValueError("data must be one-dimensional")
    finite = np.isfinite(data)
    data_clean = data[finite]
    mask = np.zeros(data.shape, dtype=bool)
    if not data_clean.size:
        return mask

    if method == 'iqr':
        Q1 = np.percentile(data_clean, 25)
        Q3 = np.percentile(data_clean, 75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR
        mask = (data >= lower) & (data <= upper)

    elif method == 'z_score':
        # A constant finite sample has no outliers. Keep original row positions
        # when placing scores computed only on the finite observations.
        if np.all(data_clean == data_clean[0]):
            mask[finite] = threshold > 0
        else:
            z_scores = np.abs(stats.zscore(data_clean))
            mask[finite] = z_scores < threshold

    elif method == 'percentile':
        lower = np.percentile(data_clean, threshold)
        upper = np.percentile(data_clean, 100 - threshold)
        mask = (data >= lower) & (data <= upper)

    return mask & finite


def handle_missing_data(
    data: pd.DataFrame,
    method: str = 'listwise',
    columns: Optional[list] = None
) -> pd.DataFrame:
    """
    Handle missing data using various methods.

    Parameters
    ----------
    data : pd.DataFrame
        Data with missing values
    method : str
        Method: 'listwise', 'mean_impute', 'median_impute', 'mode_impute'
    columns : list, optional
        Columns to process (default: all)

    Returns
    -------
    pd.DataFrame
        Processed data
    """
    data = data.copy()

    if columns is None:
        columns = data.columns.tolist()

    if method == 'listwise':
        data = data.dropna(subset=columns)

    elif method == 'mean_impute':
        for col in columns:
            if data[col].dtype in [np.float64, np.int64]:
                data[col] = data[col].fillna(data[col].mean())

    elif method == 'median_impute':
        for col in columns:
            if data[col].dtype in [np.float64, np.int64]:
                data[col] = data[col].fillna(data[col].median())

    elif method == 'mode_impute':
        for col in columns:
            mode_val = data[col].mode()
            if len(mode_val) > 0:
                data[col] = data[col].fillna(mode_val.iloc[0])

    else:
        raise ValueError(f"Unknown method: {method}")

    return data


def transform_variable(
    data: Union[np.ndarray, pd.Series],
    method: str = 'log'
) -> np.ndarray:
    """
    Apply transformation to variable.

    Parameters
    ----------
    data : array-like
        Data to transform
    method : str
        Transformation: 'log', 'sqrt', 'square', 'standardize', 'rank'

    Returns
    -------
    np.ndarray
        Transformed data
    """
    data = np.asarray(data)

    if method == 'log':
        # Add small constant to avoid log(0)
        min_val = np.min(data[data > 0]) if np.any(data > 0) else 1
        return np.log(data + min_val)

    elif method == 'sqrt':
        return np.sqrt(np.abs(data)) * np.sign(data)

    elif method == 'square':
        return data ** 2

    elif method == 'standardize':
        return (data - np.nanmean(data)) / np.nanstd(data)

    elif method == 'rank':
        return stats.rankdata(data, nan_policy='omit')

    else:
        raise ValueError(f"Unknown transformation: {method}")

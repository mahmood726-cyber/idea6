"""Data-cleaning regression fixtures, not research observations."""
import numpy as np
import pandas as pd
import pytest

from robuststat.utils import handle_missing_data, remove_outliers


@pytest.mark.parametrize("method,expected", [
    ("mean_impute", 3.0), ("median_impute", 3.0), ("mode_impute", 2.0),
])
def test_imputation_works_with_copy_on_write(method, expected):
    data = pd.DataFrame({"value": [2.0, np.nan, 4.0], "label": ["a", None, "b"]})
    original = data.copy(deep=True)
    with pd.option_context("mode.copy_on_write", True):
        result = handle_missing_data(data, method=method, columns=["value"])
    assert result.loc[1, "value"] == expected
    pd.testing.assert_frame_equal(data, original)
    assert result["label"].isna().equals(original["label"].isna())


def test_mode_imputation_handles_text():
    data = pd.DataFrame({"label": ["a", None, "a"]})
    with pd.option_context("mode.copy_on_write", True):
        result = handle_missing_data(data, method="mode_impute")
    assert result["label"].tolist() == ["a", "a", "a"]


def test_zscore_mask_preserves_missing_row_positions():
    data = np.array([1.0, np.nan, 2.0, 3.0, 100.0])
    mask = remove_outliers(data, method="z_score", threshold=1.5)
    np.testing.assert_array_equal(mask, [True, False, True, True, False])
    np.testing.assert_array_equal(data[mask], [1.0, 2.0, 3.0])


@pytest.mark.parametrize("method", ["iqr", "z_score", "percentile"])
def test_no_finite_values_has_aligned_false_mask(method):
    data = np.array([np.nan, np.inf, -np.inf])
    np.testing.assert_array_equal(remove_outliers(data, method=method), [False]*3)
    assert remove_outliers([], method=method).shape == (0,)


def test_constant_zscore_keeps_finite_values():
    np.testing.assert_array_equal(
        remove_outliers([4.0, np.nan, 4.0], method="z_score"), [True, False, True])


@pytest.mark.parametrize("threshold", [-1, float("nan"), float("inf"), "bad", None, True])
def test_invalid_outlier_threshold_rejected(threshold):
    with pytest.raises(ValueError, match="threshold"):
        remove_outliers([1, 2, 3], threshold=threshold)

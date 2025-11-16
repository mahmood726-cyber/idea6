"""
Tests for Multiverse Analysis
"""

import pytest
import numpy as np
import pandas as pd
from robuststat import MultiverseAnalyzer


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    np.random.seed(42)
    n = 150

    data = pd.DataFrame({
        'outcome': np.random.normal(50, 15, n),
        'treatment': np.random.choice([0, 1], n),
        'covariate1': np.random.normal(0, 1, n),
        'covariate2': np.random.uniform(0, 100, n),
    })

    # Add treatment effect
    data.loc[data['treatment'] == 1, 'outcome'] += 5

    # Add some outliers
    data.loc[data.sample(5).index, 'outcome'] += 50

    # Add missing data
    data.loc[data.sample(10).index, 'covariate1'] = np.nan

    return data


def test_multiverse_basic(sample_data):
    """Test basic multiverse analysis."""
    universe = {
        'data_processing': {
            'outlier_removal': [None, 'iqr'],
            'missing_data': ['listwise'],
            'transformations': [None],
        },
        'model_specification': {
            'covariates': [[], ['covariate1']],
            'model_type': ['ols'],
            'interactions': [False],
        },
        'inference': {
            'alpha': [0.05],
            'adjustment': [None],
        },
    }

    multiverse = MultiverseAnalyzer(
        data=sample_data,
        universe_spec=universe,
        outcome='outcome',
        predictor='treatment'
    )

    results = multiverse.explore(verbose=False)

    assert len(results) == 4  # 2 outlier * 2 covariates
    assert 'coefficient' in results.columns


def test_multiverse_generation(sample_data):
    """Test universe generation."""
    universe = {
        'data_processing': {
            'outlier_removal': [None, 'iqr', 'z_score'],
            'missing_data': ['listwise'],
            'transformations': [None],
        },
        'model_specification': {
            'covariates': [[], ['covariate1']],
            'model_type': ['ols'],
            'interactions': [False],
        },
        'inference': {
            'alpha': [0.05],
            'adjustment': [None],
        },
    }

    multiverse = MultiverseAnalyzer(
        data=sample_data,
        universe_spec=universe,
        outcome='outcome',
        predictor='treatment'
    )

    paths = multiverse.generate_universe()

    assert len(paths) == 6  # 3 * 1 * 1 * 2 * 1 * 1 * 1


def test_fragility_calculation(sample_data):
    """Test fragility metrics."""
    universe = {
        'data_processing': {
            'outlier_removal': [None, 'iqr'],
            'missing_data': ['listwise'],
            'transformations': [None],
        },
        'model_specification': {
            'covariates': [[]],
            'model_type': ['ols'],
            'interactions': [False],
        },
        'inference': {
            'alpha': [0.05],
            'adjustment': [None],
        },
    }

    multiverse = MultiverseAnalyzer(
        data=sample_data,
        universe_spec=universe,
        outcome='outcome',
        predictor='treatment'
    )

    multiverse.explore(verbose=False)
    fragility = multiverse.calculate_fragility()

    assert 'inferential_fragility' in fragility
    assert 'descriptive_fragility' in fragility
    assert 'sign_fragility' in fragility


def test_multiverse_summary(sample_data):
    """Test summary generation."""
    universe = {
        'data_processing': {
            'outlier_removal': [None],
            'missing_data': ['listwise'],
            'transformations': [None],
        },
        'model_specification': {
            'covariates': [[]],
            'model_type': ['ols'],
            'interactions': [False],
        },
        'inference': {
            'alpha': [0.05],
            'adjustment': [None],
        },
    }

    multiverse = MultiverseAnalyzer(
        data=sample_data,
        universe_spec=universe,
        outcome='outcome',
        predictor='treatment'
    )

    multiverse.explore(verbose=False)
    summary = multiverse.get_summary()

    assert summary is not None
    assert 'Median Coefficient' in summary.index


def test_influential_choices(sample_data):
    """Test identifying influential choices."""
    universe = {
        'data_processing': {
            'outlier_removal': [None, 'iqr'],
            'missing_data': ['listwise'],
            'transformations': [None],
        },
        'model_specification': {
            'covariates': [[], ['covariate1']],
            'model_type': ['ols'],
            'interactions': [False],
        },
        'inference': {
            'alpha': [0.05],
            'adjustment': [None],
        },
    }

    multiverse = MultiverseAnalyzer(
        data=sample_data,
        universe_spec=universe,
        outcome='outcome',
        predictor='treatment'
    )

    multiverse.explore(verbose=False)
    influential = multiverse.identify_influential_choices(n=5)

    assert influential is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

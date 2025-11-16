"""
Tests for Specification Curve Analysis
"""

import pytest
import numpy as np
import pandas as pd
from robuststat import SpecificationCurve


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    np.random.seed(42)
    n = 200

    data = pd.DataFrame({
        'outcome': np.random.normal(50, 10, n),
        'predictor': np.random.normal(0, 1, n),
        'control1': np.random.normal(0, 1, n),
        'control2': np.random.uniform(0, 100, n),
    })

    # Add real effect
    data['outcome'] += 0.3 * data['predictor']

    return data


def test_specification_curve_basic(sample_data):
    """Test basic specification curve."""
    specifications = {
        'controls': [[], ['control1'], ['control1', 'control2']],
        'models': ['ols', 'robust'],
    }

    spec_curve = SpecificationCurve(
        data=sample_data,
        outcome='outcome',
        predictor='predictor',
        specifications=specifications
    )

    results = spec_curve.run_all_specifications(verbose=False)

    assert len(results) == 6  # 3 control sets * 2 models
    assert 'coefficient' in results.columns
    assert 'p_value' in results.columns


def test_specification_generation(sample_data):
    """Test specification generation."""
    specifications = {
        'controls': [[], ['control1']],
        'models': ['ols'],
        'transformations': [None, 'standardize'],
    }

    spec_curve = SpecificationCurve(
        data=sample_data,
        outcome='outcome',
        predictor='predictor',
        specifications=specifications
    )

    all_specs = spec_curve.generate_all_specifications()

    assert len(all_specs) == 4  # 2 * 1 * 2


def test_specification_summary(sample_data):
    """Test summary statistics."""
    specifications = {
        'controls': [[], ['control1']],
        'models': ['ols'],
    }

    spec_curve = SpecificationCurve(
        data=sample_data,
        outcome='outcome',
        predictor='predictor',
        specifications=specifications
    )

    spec_curve.run_all_specifications(verbose=False)
    summary = spec_curve.get_summary()

    assert summary is not None
    assert 'Median Coefficient' in summary.index


def test_specification_plot(sample_data):
    """Test plotting."""
    specifications = {
        'controls': [[], ['control1']],
        'models': ['ols'],
    }

    spec_curve = SpecificationCurve(
        data=sample_data,
        outcome='outcome',
        predictor='predictor',
        specifications=specifications
    )

    spec_curve.run_all_specifications(verbose=False)
    fig = spec_curve.plot(show=False)

    assert fig is not None


def test_influential_specs(sample_data):
    """Test identifying influential specifications."""
    specifications = {
        'controls': [[], ['control1'], ['control1', 'control2']],
        'models': ['ols', 'robust'],
    }

    spec_curve = SpecificationCurve(
        data=sample_data,
        outcome='outcome',
        predictor='predictor',
        specifications=specifications
    )

    spec_curve.run_all_specifications(verbose=False)
    influential = spec_curve.get_influential_specs(n=5)

    assert influential is not None
    assert len(influential) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

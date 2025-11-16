"""
Tests for P-Curve Analysis
"""

import pytest
import numpy as np
from scipy import stats
from robuststat import PCurveAnalyzer


def test_pcurve_basic():
    """Test basic p-curve functionality."""
    # Generate p-values from studies with real effect
    np.random.seed(42)
    p_values = []

    for _ in range(20):
        # t-test with real effect
        group1 = np.random.normal(0, 1, 50)
        group2 = np.random.normal(0.5, 1, 50)
        _, p = stats.ttest_ind(group1, group2)
        if p < 0.05:
            p_values.append(p)

    analyzer = PCurveAnalyzer(np.array(p_values))
    results = analyzer.analyze()

    # Should detect evidential value
    assert isinstance(results, dict)
    assert 'evidential_value' in results
    assert 'full_pcurve_test' in results
    assert 'half_pcurve_test' in results
    assert 'power_estimate' in results


def test_pcurve_p_hacked():
    """Test p-curve with p-hacked values."""
    # P-values clustered near 0.05 (left-skewed)
    p_values = np.array([0.049, 0.047, 0.048, 0.046, 0.044, 0.042, 0.041])

    analyzer = PCurveAnalyzer(p_values)
    results = analyzer.analyze()

    # Should potentially detect p-hacking
    assert 'p_hacking_detected' in results


def test_pcurve_visualization():
    """Test p-curve plotting."""
    p_values = np.random.uniform(0, 0.05, 15)

    analyzer = PCurveAnalyzer(p_values)
    analyzer.analyze()

    # Should create plot without error
    fig = analyzer.plot(show=False)
    assert fig is not None


def test_pcurve_interpretation():
    """Test interpretation text generation."""
    p_values = np.random.uniform(0, 0.05, 10)

    analyzer = PCurveAnalyzer(p_values)
    analyzer.analyze()

    interpretation = analyzer.get_interpretation()

    assert isinstance(interpretation, str)
    assert len(interpretation) > 0
    assert 'P-CURVE ANALYSIS' in interpretation


def test_pcurve_to_dataframe():
    """Test DataFrame export."""
    p_values = np.random.uniform(0, 0.05, 10)

    analyzer = PCurveAnalyzer(p_values)
    analyzer.analyze()

    df = analyzer.to_dataframe()

    assert df is not None
    assert len(df) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

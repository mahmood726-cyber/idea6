

# RobustStat Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/mahmood726-cyber/idea6.git
cd idea6

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Examples

### P-Curve Analysis

```python
from robuststat import PCurveAnalyzer
import numpy as np

# Your significant p-values from published studies
p_values = [0.001, 0.012, 0.033, 0.045, 0.002, 0.018, 0.009]

# Run analysis
analyzer = PCurveAnalyzer(p_values)
results = analyzer.analyze()

# View results
print(analyzer.get_interpretation())

# Plot
analyzer.plot()
```

### Specification Curve Analysis

```python
from robuststat import SpecificationCurve
import pandas as pd

# Your data
data = pd.read_csv('your_data.csv')

# Define analytical choices
specifications = {
    'controls': [
        [],                              # No controls
        ['age', 'gender'],              # Basic controls
        ['age', 'gender', 'education']  # Full controls
    ],
    'models': ['ols', 'robust'],
    'transformations': [None, 'standardize']
}

# Run specification curve
spec_curve = SpecificationCurve(
    data=data,
    outcome='outcome_variable',
    predictor='treatment',
    specifications=specifications
)

results = spec_curve.run_all_specifications()

# View summary
print(spec_curve.get_summary())

# Plot
spec_curve.plot()
```

### Multiverse Analysis

```python
from robuststat import MultiverseAnalyzer

# Define your analytical universe
universe = {
    'data_processing': {
        'outlier_removal': [None, 'iqr', 'z_score'],
        'missing_data': ['listwise', 'mean_impute'],
        'transformations': [None, 'standardize']
    },
    'model_specification': {
        'covariates': [
            [],
            ['x1'],
            ['x1', 'x2']
        ],
        'model_type': ['ols', 'robust'],
        'interactions': [False]
    },
    'inference': {
        'alpha': [0.05],
        'adjustment': [None]
    }
}

# Run multiverse analysis
multiverse = MultiverseAnalyzer(
    data=data,
    universe_spec=universe,
    outcome='outcome',
    predictor='treatment'
)

results = multiverse.explore()

# View fragility metrics
fragility = multiverse.calculate_fragility()
print(fragility)

# Visualize
multiverse.visualize_multiverse()
```

### Integrated Analysis

```python
from robuststat.visualization import plot_robustness_dashboard

# Combine all three analyses
dashboard = plot_robustness_dashboard(
    pcurve_results=pcurve_results,
    spec_curve_results=spec_results,
    multiverse_results=multiverse_results
)
```

## Running Examples

```bash
# Run P-curve example
python examples/example_pcurve.py

# Run specification curve example
python examples/example_specification_curve.py

# Run multiverse analysis example
python examples/example_multiverse.py

# Run integrated analysis
python examples/example_integrated.py
```

## Running Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=robuststat --cov-report=html
```

## Next Steps

1. Read the full documentation in `docs/`
2. Explore the examples in `examples/`
3. Check out the methodology paper outline
4. Adapt the code to your own research

## Support

- GitHub Issues: https://github.com/mahmood726-cyber/idea6/issues
- Documentation: See `docs/` directory
- Examples: See `examples/` directory

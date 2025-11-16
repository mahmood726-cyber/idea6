# RobustStat: Advanced Statistical Methods for Research Robustness

A comprehensive Python package implementing state-of-the-art methods for assessing evidential value and robustness of research findings.

## Features

### 1. P-Curve Analysis
Implementation of Simonsohn, Nelson, & Simmons (2014) P-Curve methodology for:
- Detecting evidential value in sets of significant findings
- Identifying p-hacking and selective reporting
- Estimating statistical power of studies
- Full and half p-curve tests

### 2. Specification Curve Analysis
Comprehensive specification curve implementation for:
- Testing robustness across analytical choices
- Visualizing the distribution of effect sizes
- Inferential statistics for specification curves
- Identification of influential specifications

### 3. Multiverse Analysis
Advanced multiverse analysis framework for:
- Systematic exploration of analytical decisions
- Sensitivity analysis across all reasonable specifications
- Quantification of analytical fragility
- Interactive multiverse exploration

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### P-Curve Analysis

```python
from robuststat.pcurve import PCurveAnalyzer
import numpy as np

# Your set of significant p-values
p_values = [0.001, 0.012, 0.033, 0.045, 0.002]

# Run p-curve analysis
analyzer = PCurveAnalyzer(p_values)
results = analyzer.analyze()

# Visualize
analyzer.plot()
```

### Specification Curve Analysis

```python
from robuststat.specification_curve import SpecificationCurve
import pandas as pd

# Your data
data = pd.DataFrame({...})

# Define analytical choices
choices = {
    'dv': ['outcome1', 'outcome2'],
    'controls': [['age'], ['age', 'gender']],
    'model': ['ols', 'robust']
}

# Run specification curve
spec_curve = SpecificationCurve(data, choices)
results = spec_curve.run_all_specifications()
spec_curve.plot()
```

### Multiverse Analysis

```python
from robuststat.multiverse import MultiverseAnalyzer

# Define your analytical universe
universe = {
    'outlier_removal': [None, 'iqr', 'z_score'],
    'transformation': [None, 'log', 'sqrt'],
    'covariates': [['x1'], ['x1', 'x2']]
}

# Run multiverse analysis
multiverse = MultiverseAnalyzer(data, universe)
results = multiverse.explore()
multiverse.visualize_multiverse()
```

## Methodology

### P-Curve
Based on Simonsohn, U., Nelson, L. D., & Simmons, J. P. (2014). P-curve: A key to the file-drawer. *Journal of Experimental Psychology: General*, 143(2), 534-547.

### Specification Curve
Based on Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour*, 4(11), 1208-1214.

### Multiverse Analysis
Based on Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5), 702-712.

## Documentation

Full documentation is available in the `docs/` directory.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{robuststat2025,
  title={RobustStat: Advanced Statistical Methods for Research Robustness},
  author={Research Methods Lab},
  year={2025},
  url={https://github.com/mahmood726-cyber/idea6}
}
```

## License

MIT License

"""
RobustStat: Advanced Statistical Methods for Research Robustness

A comprehensive package for P-Curve Analysis, Specification Curve Analysis,
and Multiverse Analysis.
"""

__version__ = "0.1.0"
__author__ = "Research Methods Lab"

from robuststat.pcurve.analyzer import PCurveAnalyzer
from robuststat.specification_curve.analyzer import SpecificationCurve
from robuststat.multiverse.analyzer import MultiverseAnalyzer

__all__ = [
    "PCurveAnalyzer",
    "SpecificationCurve",
    "MultiverseAnalyzer",
]

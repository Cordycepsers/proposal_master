"""
Client Module

This module contains specialized sub-agents for client assessment and profiling:
- Capability Evaluator: Evaluates organizational capabilities and readiness
- Profile Comparator: Compares client profiles against project requirements
"""

from .capability_evaluator import CapabilityEvaluator
from .profile_comparator import ProfileComparator

__all__ = [
    'CapabilityEvaluator',
    'ProfileComparator'
]

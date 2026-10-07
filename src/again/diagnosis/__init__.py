"""Question-level diagnosis hypotheses. Phase 4+. Derived, not observational."""

from .engine import Diagnosis, build_diagnoses, diagnose_learning_insights

__all__ = [
    "Diagnosis",
    "build_diagnoses",
    "diagnose_learning_insights",
]

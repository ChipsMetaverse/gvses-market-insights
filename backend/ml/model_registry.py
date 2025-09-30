from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

ModelConfig = Dict[str, Any]
ModelRegistry = Dict[str, ModelConfig]

_BASE_MODELS: ModelRegistry = {
    "random_forest": {
        "class": RandomForestClassifier,
        "params": {
            "n_estimators": 300,
            "max_depth": 12,
            "min_samples_split": 4,
            "min_samples_leaf": 2,
            "random_state": 42,
            "n_jobs": -1,
        },
        "param_grid": {
            "n_estimators": [200, 300, 400],
            "max_depth": [10, 12, 14],
            "min_samples_split": [2, 4, 6],
        },
    },
    "logistic": {
        "class": LogisticRegression,
        "params": {
            "random_state": 42,
            "max_iter": 1000,
            "solver": "liblinear",
        },
        "param_grid": {
            "C": [0.1, 1.0, 10.0],
            "penalty": ["l1", "l2"],
        },
    },
}

_OPTIONAL_MODEL_BUILDERS = {
    "xgboost": (
        "xgboost",
        lambda module: {
            "class": module.XGBClassifier,
            "params": {
                "n_estimators": 300,
                "max_depth": 6,
                "learning_rate": 0.05,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "tree_method": "hist",
                "random_state": 42,
            },
            "param_grid": {
                "n_estimators": [200, 300, 400],
                "max_depth": [4, 6, 8],
                "learning_rate": [0.03, 0.05, 0.07],
            },
        },
    ),
    "lightgbm": (
        "lightgbm",
        lambda module: {
            "class": module.LGBMClassifier,
            "params": {
                "n_estimators": 400,
                "max_depth": -1,
                "learning_rate": 0.05,
                "num_leaves": 32,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "objective": "binary",
                "random_state": 42,
            },
            "param_grid": {
                "n_estimators": [300, 400, 500],
                "num_leaves": [24, 32, 40],
                "learning_rate": [0.03, 0.05, 0.07],
            },
        },
    ),
}


def _import_optional(module_name: str, log: logging.Logger) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - environment specific
        log.warning("Optional module '%s' unavailable: %s", module_name, exc)
        return None


def get_model_registry(log: Optional[logging.Logger] = None) -> ModelRegistry:
    """Return the available ML model configurations based on installed dependencies."""

    active_log = log or logger
    registry: ModelRegistry = dict(_BASE_MODELS)

    for model_name, (module_name, builder) in _OPTIONAL_MODEL_BUILDERS.items():
        module = _import_optional(module_name, active_log)
        if module is None:
            continue
        try:
            registry[model_name] = builder(module)
        except Exception as exc:  # pragma: no cover - defensive guard
            active_log.warning("Skipping optional model '%s': %s", model_name, exc)

    return registry


__all__ = ["ModelConfig", "ModelRegistry", "get_model_registry"]

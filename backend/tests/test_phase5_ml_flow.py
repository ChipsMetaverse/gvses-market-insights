import asyncio
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:  # pragma: no cover - import guard
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pytest
from sklearn.preprocessing import StandardScaler

from backend.ml.model_registry import get_model_registry
from backend.services.pattern_confidence_service import PatternConfidenceService
from backend.services.pattern_confidence_service import ConfidencePrediction
from backend.services.pattern_lifecycle import PatternLifecycleManager


class _DummyXGBModule:
    class XGBClassifier:  # pragma: no cover - simple stub
        pass


class _DummyLGBModule:
    class LGBMClassifier:  # pragma: no cover - simple stub
        pass


@pytest.mark.parametrize(
    "available_modules,expected_optional",
    [
        ({}, set()),
        ({"xgboost": _DummyXGBModule}, {"xgboost"}),
        ({"lightgbm": _DummyLGBModule}, {"lightgbm"}),
        ({"xgboost": _DummyXGBModule, "lightgbm": _DummyLGBModule}, {"xgboost", "lightgbm"}),
    ],
)
def test_model_registry_handles_optional_dependencies(monkeypatch, available_modules, expected_optional):
    """Registry should include base models and add optional ones only when importable."""

    def _fake_import(name: str) -> Any:
        if name in available_modules:
            return available_modules[name]
        raise ImportError(f"module {name} not available")

    monkeypatch.setattr("backend.ml.model_registry.importlib.import_module", _fake_import)

    registry = get_model_registry()

    assert {"random_forest", "logistic"}.issubset(set(registry))
    optional_present = {name for name in ("xgboost", "lightgbm") if name in registry}
    assert optional_present == expected_optional


@pytest.mark.asyncio
async def test_pattern_confidence_service_loads_champion_artifacts(tmp_path: Path):
    """Service should load model metadata and feature names from champion artifacts."""

    feature_names = ["feature_a", "feature_b", "feature_c"]

    # Create minimal artifacts
    model = StandardScaler()  # simple sklearn object for serialization
    model.fit(np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]))

    joblib.dump(model, tmp_path / "model.pkl")
    joblib.dump({"logistic_scaler": model}, tmp_path / "scalers.pkl")
    joblib.dump({"label_encoder": None}, tmp_path / "encoders.pkl")

    model_card = {
        "model_version": "test_model",
        "model_type": "random_forest",
        "training_date": "2025-01-01T00:00:00Z",
        "training_data_size": 10,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "hyperparameters": {},
        "performance_metrics": {
            "accuracy": 0.9,
            "roc_auc": 0.9,
            "precision": 0.9,
            "recall": 0.9,
            "f1_score": 0.9,
            "log_loss": 0.1,
            "calibration_error": 0.05,
            "feature_importance": {},
            "cross_val_scores": [0.9, 0.88, 0.91],
        },
        "data_vintage": "2025-01-01T00:00:00Z",
        "notes": "",
    }

    with (tmp_path / "model_card.json").open("w", encoding="utf-8") as handle:
        json.dump(model_card, handle)

    service = PatternConfidenceService(model_path=str(tmp_path))
    await service._load_model()

    assert service.feature_names == feature_names
    assert service.model_metadata["model_version"] == "test_model"


def test_lifecycle_manager_emits_ml_metadata(monkeypatch):
    class _StubConfidenceService:
        async def predict_confidence(self, **_: Any) -> ConfidencePrediction:  # pragma: no cover - stub
            return ConfidencePrediction(
                ml_confidence=0.72,
                prediction_class="positive",
                class_probabilities={"positive": 0.72, "negative": 0.28},
                feature_count=50,
                model_version="champion_v1",
                inference_latency_ms=12,
                fallback_used=False,
                rule_confidence=0.65,
                blended_confidence=0.72 * 0.6 + 0.65 * 0.4,
            )

    manager = PatternLifecycleManager(
        enable_phase5_ml=True,
        confidence_service=_StubConfidenceService(),
        ml_confidence_threshold=0.5,
    )

    analysis = {
        "patterns": [
            {
                "pattern_id": "pattern-123",
                "symbol": "AAPL",
                "timeframe": "1H",
                "confidence": 65.0,
                "bias": "bullish",
                "key_levels": {"resistance": [190.0]},
                "targets": [195.0],
            }
        ]
    }

    result = manager.update(symbol="AAPL", timeframe="1H", analysis=analysis)

    assert result["states"], "Expected lifecycle states"
    state = result["states"][0]
    assert state["confidence"] == pytest.approx(69.2, rel=1e-3)
    assert "ml" in state, "Expected ML metadata in state summary"
    assert state["ml"]["ml_confidence_pct"] == pytest.approx(72.0, rel=1e-3)

    repo_updates = result.get("repository_updates")
    assert repo_updates is not None and len(repo_updates) == 1
    pattern_id, payload = repo_updates[0]
    assert pattern_id == "pattern-123"
    assert payload["ml_confidence"] == pytest.approx(72.0, rel=1e-3)
    assert payload["blended_confidence"] == pytest.approx(69.2, rel=1e-3)

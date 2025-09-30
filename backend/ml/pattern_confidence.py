#!/usr/bin/env python3
"""
Pattern Confidence ML Training Pipeline - Phase 5
===============================================
Trains and evaluates machine learning models for pattern confidence prediction
"""

import logging
import json
import os
import shutil
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, log_loss, accuracy_score
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV

# Backend imports
import sys
sys.path.append(str(Path(__file__).parent.parent))
from services.pattern_repository import PatternRepository
from .model_registry import get_model_registry, ModelRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Container for model evaluation metrics"""

    accuracy: float
    roc_auc: float
    precision: float
    recall: float
    f1_score: float
    log_loss: float
    calibration_error: float
    feature_importance: Dict[str, float]
    cross_val_scores: List[float]
    
@dataclass 
class ModelCard:
    """Model documentation and metadata"""

    model_version: str
    model_type: str
    training_date: str
    training_data_size: int
    feature_count: int
    feature_names: List[str]
    hyperparameters: Dict[str, Any]
    performance_metrics: ModelMetrics
    data_vintage: str
    notes: str

class PatternConfidenceTrainer:
    """
    Machine Learning trainer for pattern confidence prediction
    
    Features:
    - Multiple model types (XGBoost, LightGBM, Random Forest, Logistic Regression)
    - Hyperparameter tuning with cross-validation
    - Model calibration for reliable probability outputs
    - Comprehensive evaluation with multiple metrics
    - Feature importance analysis with SHAP
    - Model serialization and registry
    """
    
    def __init__(self, 
                 data_path: Optional[str] = None,
                 model_output_dir: str = "models/phase5"):
        self.data_path = data_path
        self.model_output_dir = Path(model_output_dir)
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.repository = PatternRepository()
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.training_data = None
        self.feature_names = None
        
        # Model configurations resolved via registry helper
        self.model_configs: ModelRegistry = get_model_registry(logger)

        response = (
            self.repository.client.table("pattern_events")
            .select("id,symbol,pattern_type,outcome_label,target_accuracy,realized_pnl,training_split,ml_features,last_evaluated_at")
            .eq("used_for_training", True)
            .not_.is_("outcome_label", "null")
            .not_.is_("ml_features", "null")
        ).execute()

        if not response.data:
            raise ValueError("No training data found in database")

        records: List[Dict[str, Any]] = []
        for row in response.data:
            try:
                features = row.get("ml_features")
                if isinstance(features, str):
                    features = json.loads(features)
                elif features is None:
                    features = {}

                record = {
                    "pattern_id": row.get("id"),
                    "symbol": row.get("symbol"),
                    "pattern_type": row.get("pattern_type"),
                    "outcome_label": row.get("outcome_label"),
                    "target_accuracy": row.get("target_accuracy", 0.5),
                    "realized_pnl": row.get("realized_pnl", 0.0),
                    "training_split": row.get("training_split", "train"),
                    "last_evaluated_at": row.get("last_evaluated_at"),
                    **features,
                }
                records.append(record)
            except Exception as exc:
                logger.warning(f"Skipping pattern {row.get('id')} due to malformed features: {exc}")

        if not records:
            raise ValueError("All retrieved rows were skipped due to invalid feature payloads")

        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} training samples from database")
        self.training_data = df
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and labels for training."""

        metadata_cols = [
            "pattern_id",
            "symbol",
            "pattern_type",
            "outcome_label",
            "target_accuracy",
            "realized_pnl",
            "training_split",
            "last_evaluated_at",
        ]

        feature_cols = [col for col in df.columns if col not in metadata_cols]
        if not feature_cols:
            raise ValueError("No feature columns available for training")

        features_df = df[feature_cols].astype(float)
        X = np.nan_to_num(features_df.values, nan=0.0, posinf=0.0, neginf=0.0)
        y = df["outcome_label"].values

        if "label_encoder" not in self.label_encoders:
            self.label_encoders["label_encoder"] = LabelEncoder()
            y_encoded = self.label_encoders["label_encoder"].fit_transform(y)
        else:
            y_encoded = self.label_encoders["label_encoder"].transform(y)

        self.feature_names = feature_cols
        logger.info(
            "Prepared %s samples with %s features", X.shape[0], X.shape[1]
        )
        logger.info(
            "Label distribution: %s",
            dict(zip(*np.unique(y, return_counts=True)))
        )

        return X, y_encoded, feature_cols
    
    def train_model(self, 
                   model_name: str,
                   X_train: np.ndarray,
                   y_train: np.ndarray,
                   X_val: np.ndarray,
                   y_val: np.ndarray,
                   tune_hyperparameters: bool = True) -> Tuple[Any, ModelMetrics]:
        """Train a single model with optional hyperparameter tuning"""
        
        if model_name not in self.model_configs:
            raise ValueError(f"Unknown model: {model_name}")
        
        config = self.model_configs[model_name]
        logger.info(f"Training {model_name} model...")
        
        # Scale features for logistic regression
        if model_name == 'logistic':
            scaler_key = f'{model_name}_scaler'
            if scaler_key not in self.scalers:
                self.scalers[scaler_key] = StandardScaler()
                X_train_scaled = self.scalers[scaler_key].fit_transform(X_train)
            else:
                X_train_scaled = self.scalers[scaler_key].transform(X_train)
            X_val_scaled = self.scalers[scaler_key].transform(X_val)
        else:
            X_train_scaled = X_train
            X_val_scaled = X_val
        
        # Initialize model
        model = config['class'](**config['params'])
        
        # Hyperparameter tuning
        if tune_hyperparameters and len(config.get('param_grid', {})) > 0:
            logger.info(f"Tuning hyperparameters for {model_name}...")
            grid_search = GridSearchCV(
                model, 
                config['param_grid'],
                cv=3,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train_scaled, y_train)
            model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
        else:
            model.fit(X_train_scaled, y_train)
        
        # Calibrate model for better probability estimates
        calibrated_model = CalibratedClassifierCV(model, method='isotonic', cv=3)
        calibrated_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        metrics = self._evaluate_model(calibrated_model, X_val_scaled, y_val, X_train_scaled, y_train)

        # Store model
        self.models[model_name] = calibrated_model

        return calibrated_model, metrics
    
    def _evaluate_model(self, 
                       model: Any,
                       X_val: np.ndarray,
                       y_val: np.ndarray,
                       X_train: np.ndarray,
                       y_train: np.ndarray) -> ModelMetrics:
        """Comprehensive model evaluation"""
        
        # Predictions
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)
        
        # Basic metrics
        accuracy = accuracy_score(y_val, y_pred)
        
        # Multi-class ROC AUC
        if len(np.unique(y_val)) > 2:
            roc_auc = roc_auc_score(y_val, y_pred_proba, multi_class='ovr', average='weighted')
        else:
            roc_auc = roc_auc_score(y_val, y_pred_proba[:, 1])
        
        # Classification report for precision, recall, f1
        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
        precision = report['weighted avg']['precision']
        recall = report['weighted avg']['recall']
        f1_score = report['weighted avg']['f1-score']
        
        # Log loss
        logloss = log_loss(y_val, y_pred_proba)
        
        # Calibration error
        calibration_error = self._calculate_calibration_error(y_val, y_pred_proba)
        
        # Feature importance
        feature_importance = self._get_feature_importance(model)
        
        # Cross-validation scores
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')

        return ModelMetrics(
            accuracy=accuracy,
            roc_auc=roc_auc,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            log_loss=logloss,
            calibration_error=calibration_error,
            feature_importance=feature_importance,
            cross_val_scores=cv_scores.tolist(),
        )
    
    def _calculate_calibration_error(self, y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Calculate calibration error (reliability)"""
        # For multi-class, use the predicted class probabilities
        if y_prob.shape[1] > 2:
            # Use the maximum predicted probability for each sample
            y_prob_max = np.max(y_prob, axis=1)
            y_pred_class = np.argmax(y_prob, axis=1)
            correct = (y_true == y_pred_class).astype(int)
        else:
            # Binary classification
            y_prob_max = y_prob[:, 1]
            correct = (y_true == (y_prob_max > 0.5)).astype(int)
        
        # Calculate calibration error
        try:
            fraction_of_positives, mean_predicted_value = calibration_curve(
                correct, y_prob_max, n_bins=10, strategy='quantile'
            )
            calibration_error = np.mean(np.abs(fraction_of_positives - mean_predicted_value))
        except:
            calibration_error = 0.0
        
        return calibration_error
    
    def _get_feature_importance(self, model: Any) -> Dict[str, float]:
        """Extract feature importance from model"""
        if not self.feature_names:
            return {}
        
        try:
            # Handle calibrated models
            if hasattr(model, 'base_estimator'):
                base_model = model.base_estimator
            elif hasattr(model, 'calibrated_classifiers_'):
                base_model = model.calibrated_classifiers_[0].base_estimator
            else:
                base_model = model
            
            # Get importance based on model type
            if hasattr(base_model, 'feature_importances_'):
                importance = base_model.feature_importances_
            elif hasattr(base_model, 'coef_'):
                # For linear models, use absolute coefficients
                importance = np.abs(base_model.coef_[0]) if base_model.coef_.ndim > 1 else np.abs(base_model.coef_)
            else:
                return {}
            
            # Create feature importance dictionary
            feature_importance = dict(zip(self.feature_names, importance))
            
            # Sort by importance
            sorted_importance = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            )

            return sorted_importance

        except Exception as e:
            logger.warning(f"Could not extract feature importance: {str(e)}")
            return {}

    def export_artifacts(
        self,
        model_name: str,
        model: Any,
        metrics: ModelMetrics,
        feature_cols: List[str],
        training_rows: int,
        output_subdir: Optional[str] = None,
        data_vintage: Optional[str] = None,
        notes: str = ""
    ) -> Path:
        """Persist trained model, scalers, encoders, and model card."""

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        subdir = output_subdir or f"{timestamp}_{model_name}"
        export_dir = self.model_output_dir / subdir
        export_dir.mkdir(parents=True, exist_ok=True)

        # Persist artifacts
        joblib.dump(model, export_dir / "model.pkl")
        if self.scalers:
            joblib.dump(self.scalers, export_dir / "scalers.pkl")
        if self.label_encoders:
            joblib.dump(self.label_encoders, export_dir / "encoders.pkl")

        model_card = ModelCard(
            model_version=subdir,
            model_type=model_name,
            training_date=datetime.now(timezone.utc).isoformat(),
            training_data_size=training_rows,
            feature_count=len(feature_cols),
            feature_names=feature_cols,
            hyperparameters=self.model_configs[model_name]["params"],
            performance_metrics=metrics,
            data_vintage=data_vintage or datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )

        with open(export_dir / "model_card.json", "w", encoding="utf-8") as f:
            json.dump(asdict(model_card), f, indent=2, default=lambda x: x.__dict__ if hasattr(x, "__dict__") else x)

        with open(export_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2)

        logger.info("Exported model artifacts to %s", export_dir)
        return export_dir

    def promote_champion(self, artifact_dir: Path) -> None:
        """Mark the supplied artifact directory as the active champion model."""

        champion_dir = self.model_output_dir / "champion"
        if champion_dir.exists():
            shutil.rmtree(champion_dir)
        shutil.copytree(artifact_dir, champion_dir)
        logger.info("Champion model updated: %s", champion_dir)

    def train_all_models(
        self, df: pd.DataFrame
    ) -> Dict[str, Tuple[Any, ModelMetrics, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
        """Train all configured models"""
        X, y, feature_names = self.prepare_data(df)

        train_mask = df["training_split"] == "train"
        val_mask = df["training_split"] == "val"

        if not val_mask.any():
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            X_train, y_train = X[train_mask], y[train_mask]
            X_val, y_val = X[val_mask], y[val_mask]

        logger.info("Training set: %s samples", X_train.shape[0])
        logger.info("Validation set: %s samples", X_val.shape[0])

        results: Dict[
            str,
            Tuple[Any, ModelMetrics, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
        ] = {}
        for model_name in self.model_configs.keys():
            try:
                model, metrics = self.train_model(model_name, X_train, y_train, X_val, y_val)
                results[model_name] = (model, metrics, (X_train, y_train, X_val, y_val))
                logger.info(
                    "%s - ROC AUC: %.3f, Accuracy: %.3f",
                    model_name,
                    metrics.roc_auc,
                    metrics.accuracy,
                )
            except Exception as exc:
                logger.error(f"Failed to train {model_name}: {exc}")

        return results

    def select_champion_model(
        self,
        results: Dict[str, Tuple[Any, ModelMetrics, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]],
    ) -> Tuple[str, Any, ModelMetrics]:
        """Select the best performing model as champion"""
        if not results:
            raise ValueError("No models trained successfully")

        model_scores = {name: metrics.roc_auc for name, (model, metrics, _) in results.items()}
        champion_name = max(model_scores, key=model_scores.get)
        champion_model, champion_metrics, _ = results[champion_name]

        logger.info(
            "Champion model: %s (ROC AUC: %.3f)", champion_name, champion_metrics.roc_auc
        )
        return champion_name, champion_model, champion_metrics

    def generate_evaluation_report(
        self,
        results: Dict[str, Tuple[Any, ModelMetrics, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]],
        output_dir: str = "reports/phase5",
    ) -> str:
        """Generate comprehensive evaluation report"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_dir = Path(output_dir) / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Model comparison summary
        comparison = []
        for model_name, (model, metrics, _) in results.items():
            comparison.append({
                "model": model_name,
                "roc_auc": metrics.roc_auc,
                "accuracy": metrics.accuracy,
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "log_loss": metrics.log_loss,
                "calibration_error": metrics.calibration_error,
                "cv_mean": np.mean(metrics.cross_val_scores),
                "cv_std": np.std(metrics.cross_val_scores)
            })
        
        # Save comparison table
        comparison_df = pd.DataFrame(comparison)
        comparison_path = report_dir / "model_comparison.csv"
        comparison_df.to_csv(comparison_path, index=False)
        
        # Create evaluation report
        report = {
            "evaluation_date": datetime.now(timezone.utc).isoformat(),
            "models_evaluated": len(results),
            "model_comparison": comparison,
            "champion_model": comparison_df.loc[comparison_df['roc_auc'].idxmax()]['model'],
            "feature_count": len(self.feature_names) if self.feature_names else 0,
            "training_samples": len(self.training_data) if self.training_data is not None else 0
        }
        
        # Save evaluation report
        report_path = report_dir / "evaluation.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Evaluation report saved to {report_dir}")
        return str(report_path)

async def main():
    """Main training pipeline execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pattern Confidence ML Training")
    parser.add_argument("--data", help="Training data CSV file path")
    parser.add_argument("--models", nargs='+', default=['xgboost', 'lightgbm', 'random_forest', 'logistic'],
                       help="Models to train")
    parser.add_argument("--tune", action="store_true", help="Enable hyperparameter tuning")
    parser.add_argument("--output", default="models/phase5", help="Model output directory")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = PatternConfidenceTrainer(
        data_path=args.data,
        model_output_dir=args.output
    )
    
    # Load training data
    df = trainer.training_data
    
    # Filter models to train
    trainer.model_configs = {k: v for k, v in trainer.model_configs.items() if k in args.models}
    
    # Train models
    results = trainer.train_all_models(df)
    
    if not results:
        print("❌ No models trained successfully")
        return 1
    
    # Select champion model
    champion_name, champion_model, champion_metrics = trainer.select_champion_model(results)
    
    # Export artifacts and promote champion
    artifact_dirs: Dict[str, Path] = {}
    for model_name, (model, metrics, _) in results.items():
        artifact_dirs[model_name] = trainer.export_artifacts(
            model_name=model_name,
            model=model,
            metrics=metrics,
            feature_cols=trainer.feature_names or [],
            training_rows=len(trainer.training_data) if trainer.training_data is not None else 0,
            notes="champion" if model_name == champion_name else ""
        )

    trainer.promote_champion(artifact_dirs[champion_name])
    
    # Generate evaluation report
    report_path = trainer.generate_evaluation_report(results)
    
    # Print results
    print("✅ Pattern Confidence Training Complete!")
    print(f"🏆 Champion: {champion_name} (ROC AUC: {champion_metrics.roc_auc:.3f})")
    print(f"📊 Models trained: {len(results)}")
    print(f"📁 Models saved to: {args.output}")
    print(f"📋 Report: {report_path}")
    
    return 0

if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))
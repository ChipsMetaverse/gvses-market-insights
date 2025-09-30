#!/usr/bin/env python3
"""
Train initial Phase 5 ML models for pattern confidence prediction.
Creates champion models in the models/phase5/champion directory.
"""

import sys
import os
import json
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def generate_synthetic_data(n_samples=1000):
    """Generate synthetic training data for initial model."""
    np.random.seed(42)
    
    # Generate 52 features as expected by PatternFeatureBuilder
    X = np.random.randn(n_samples, 52)
    
    # Add some patterns to make classification meaningful
    # High confidence patterns (class 1)
    high_conf_mask = np.random.choice(n_samples, size=n_samples//3, replace=False)
    X[high_conf_mask, 0] += 2  # Strong pattern geometry
    X[high_conf_mask, 10] += 1.5  # Good technical indicators
    
    # Medium confidence patterns (class 0)
    med_conf_mask = np.random.choice(
        list(set(range(n_samples)) - set(high_conf_mask)), 
        size=n_samples//3, 
        replace=False
    )
    X[med_conf_mask, 0] += 0.5
    
    # Create labels
    y = np.zeros(n_samples, dtype=int)
    y[high_conf_mask] = 1  # High confidence
    
    feature_names = [f"feature_{i}" for i in range(52)]
    
    return X, y, feature_names

def train_models(X, y, feature_names):
    """Train Random Forest and Logistic Regression models."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {}
    
    # Train Random Forest
    print("\nTraining Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_score = accuracy_score(y_test, rf.predict(X_test))
    print(f"Random Forest Accuracy: {rf_score:.3f}")
    models['random_forest'] = rf
    
    # Train Logistic Regression
    print("\nTraining Logistic Regression...")
    lr = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=42,
        solver='lbfgs'
    )
    lr.fit(X_train_scaled, y_train)
    lr_score = accuracy_score(y_test, lr.predict(X_test_scaled))
    print(f"Logistic Regression Accuracy: {lr_score:.3f}")
    models['logistic_regression'] = lr
    
    return models, scaler, rf_score

def save_champion_models(models, scaler, feature_names, accuracy):
    """Save trained models as champion artifacts."""
    champion_dir = Path(__file__).parent.parent / "models" / "phase5" / "champion"
    champion_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save Random Forest as primary model
    model_path = champion_dir / "model.pkl"
    joblib.dump(models['random_forest'], model_path)
    print(f"\n✅ Saved champion model to: {model_path}")
    
    # Save scaler
    scaler_path = champion_dir / "scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✅ Saved scaler to: {scaler_path}")
    
    # Save feature names
    features_path = champion_dir / "feature_names.json"
    with open(features_path, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"✅ Saved feature names to: {features_path}")
    
    # Save model metadata
    metadata = {
        "model_version": f"v1.0.0_{timestamp}",
        "model_type": "RandomForestClassifier",
        "training_date": datetime.now().isoformat(),
        "accuracy": float(accuracy),
        "feature_count": len(feature_names),
        "framework": "scikit-learn",
        "description": "Initial Phase 5 ML model for pattern confidence prediction",
        "training_samples": 1000,
        "status": "champion"
    }
    
    metadata_path = champion_dir / "model_card.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Saved model metadata to: {metadata_path}")
    
    # Save backup models
    backup_dir = champion_dir.parent / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    for name, model in models.items():
        backup_path = backup_dir / f"{name}_{timestamp}.pkl"
        joblib.dump(model, backup_path)
        print(f"✅ Saved backup {name} to: {backup_path}")
    
    return champion_dir

def main():
    """Main training pipeline."""
    print("=" * 60)
    print("Phase 5 ML Model Training")
    print("=" * 60)
    
    # Generate synthetic training data
    print("\n1. Generating synthetic training data...")
    X, y, feature_names = generate_synthetic_data(n_samples=1000)
    print(f"   Generated {len(X)} samples with {len(feature_names)} features")
    print(f"   Class distribution: {np.bincount(y)}")
    
    # Train models
    print("\n2. Training ML models...")
    models, scaler, accuracy = train_models(X, y, feature_names)
    
    # Save champion models
    print("\n3. Saving champion models...")
    champion_dir = save_champion_models(models, scaler, feature_names, accuracy)
    
    # Verify saved models
    print("\n4. Verifying saved models...")
    saved_files = list(champion_dir.glob("*"))
    print(f"   Champion directory contains {len(saved_files)} files:")
    for f in saved_files:
        print(f"   - {f.name}")
    
    print("\n" + "=" * 60)
    print("✅ Phase 5 ML models trained successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Apply database migration: supabase/migrations/20250928000001_phase5_ml_columns.sql")
    print("2. Enable Phase 5: Set ENABLE_PHASE5_ML=true in backend/.env")
    print("3. Monitor at: /api/ml/health and /api/ml/metrics")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
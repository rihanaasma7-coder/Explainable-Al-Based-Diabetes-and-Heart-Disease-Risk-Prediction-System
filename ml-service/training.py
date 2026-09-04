from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from preprocessing import preprocess_diabetes, preprocess_heart

MODEL_VERSION = "2026-06-22-explainability-v3"


@dataclass
class ModelBundle:
    pipeline: Pipeline
    metrics: Dict
    model_name: str
    feature_names: list[str]
    background_frame: object
    model_version: str


def candidate_models(scale_pos_weight: float = 1.0) -> Dict:
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced"),
        "XGBoost": XGBClassifier(
            n_estimators=180,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False,
        ),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=180, max_depth=4, learning_rate=0.05, random_state=42),
    }


def train_one(name: str, X, y, prep_pipeline: Pipeline, model_dir: str, feature_names: list[str]) -> Dict:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    results = {}
    best = None

    positives = int(y_train.sum())
    negatives = int(len(y_train) - positives)
    scale_pos_weight = negatives / positives if positives else 1.0

    for model_name, estimator in candidate_models(scale_pos_weight).items():
        pipeline = Pipeline([("features", prep_pipeline), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)
        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "roc_auc": round(roc_auc, 4),
        }
        results[model_name] = metrics
        selection_score = (0.35 * metrics["roc_auc"]) + (0.3 * metrics["recall"]) + (0.2 * metrics["f1"]) + (0.15 * metrics["accuracy"])
        if best is None or selection_score > best[3]:
            best = (model_name, pipeline, metrics, selection_score)

    assert best is not None
    background_frame = X_train.sample(n=min(500, len(X_train)), random_state=42).reset_index(drop=True)
    bundle = ModelBundle(
        pipeline=best[1],
        metrics=best[2],
        model_name=best[0],
        feature_names=feature_names,
        background_frame=background_frame,
        model_version=MODEL_VERSION,
    )
    joblib.dump(bundle, os.path.join(model_dir, f"{name}_model.pkl"))
    return {"selectedModel": best[0], "metrics": results, "bestMetrics": best[2]}


def train_all_models(dataset_dir: str, model_dir: str) -> Dict:
    os.makedirs(model_dir, exist_ok=True)
    processed_dir = os.path.join(os.path.dirname(model_dir), "processed")
    diabetes_X, diabetes_y, diabetes_pipeline = preprocess_diabetes(dataset_dir, processed_dir)
    heart_X, heart_y, heart_pipeline = preprocess_heart(dataset_dir, processed_dir)
    return {
        "diabetes": train_one("diabetes", diabetes_X, diabetes_y, diabetes_pipeline, model_dir, list(diabetes_X.columns)),
        "heart": train_one("heart", heart_X, heart_y, heart_pipeline, model_dir, list(heart_X.columns)),
    }

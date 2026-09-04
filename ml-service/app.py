from __future__ import annotations

import os
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import sklearn

from explainability import explain_prediction
from preprocessing import (
    DIABETES_FEATURES,
    HEART_FEATURES,
    normalize_input,
    preprocess_diabetes,
    preprocess_heart,
)
from recommendations import build_recommendations
from training import MODEL_VERSION, ModelBundle, train_all_models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(PROJECT_DIR, "models"))
DATASET_DIR = os.getenv("DATASET_DIR", os.path.join(PROJECT_DIR, "datasets"))

app = Flask(__name__)
CORS(app)


def risk_label(probability: float) -> str:
    """Map a probability percentage to the requested health risk band."""
    if probability <= 30:
        return "Low"
    if probability <= 70:
        return "Medium"
    return "High"


def sigmoid(value: float) -> float:
    return float(1 / (1 + np.exp(-value)))


def calibrate_probability(disease: str, model_probability: float, patient: Dict[str, Any]) -> float:
    """Blend model confidence with a bounded clinical prior when API inputs omit key dataset predictors."""
    if disease != "diabetes":
        return model_probability

    clinical_prior = (
        0.02
        + 0.84 * sigmoid((patient.get("glucose", 0) - 130) / 18)
        + 0.09 * sigmoid((patient.get("bmi", 0) - 30) / 4)
        + 0.06 * sigmoid((patient.get("bloodPressure", 0) - 130) / 10)
        + 0.04 * sigmoid((patient.get("age", 0) - 45) / 15)
    )
    return min(max(model_probability, clinical_prior), 0.995)


def model_path(disease: str) -> str:
    return os.path.join(MODEL_DIR, f"{disease}_model.pkl")


def load_or_train() -> Dict[str, ModelBundle]:
    os.makedirs(MODEL_DIR, exist_ok=True)
    required = {"diabetes": model_path("diabetes"), "heart": model_path("heart")}

    # If any model file is missing, mark for training
    should_train = not all(os.path.exists(path) for path in required.values())

    # Probe existing model files and validate they can be loaded with current libs
    expected_feature_sets = {
        "diabetes": DIABETES_FEATURES,
        "heart": HEART_FEATURES,
    }

    if not should_train:
        for name, path in required.items():
            try:
                bundle = joblib.load(path)
            except Exception as exc:  # catch incompatible pickle or other load error
                print(f"Failed to load model {path}: {exc!r}")
                try:
                    os.remove(path)
                    print(f"Deleted incompatible model file: {path}")
                except OSError:
                    print(f"Could not delete file: {path}")
                should_train = True
                break

            expected_features = expected_feature_sets.get(name, [])
            if (
                not hasattr(bundle, "background_frame")
                or list(getattr(bundle, "feature_names", [])) != expected_features
                or getattr(bundle, "model_version", None) != MODEL_VERSION
            ):
                print(f"Model {path} appears out-of-date or malformed; scheduling retrain.")
                should_train = True
                break

    if should_train:
        print("Retraining models due to missing or incompatible model files...")
        train_all_models(DATASET_DIR, MODEL_DIR)

    # Load models (after possible retrain) with error handling to avoid startup crashes
    models: Dict[str, ModelBundle] = {}
    for name, path in required.items():
        try:
            models[name] = joblib.load(path)
        except Exception as exc:
            print(f"Error loading model {path} after retrain: {exc!r}")
            try:
                os.remove(path)
                print(f"Deleted bad model file: {path}")
            except OSError:
                print(f"Could not delete file: {path}")
            # Attempt one more retrain to recover
            print("Attempting one more retrain to recover missing/broken model files...")
            train_all_models(DATASET_DIR, MODEL_DIR)
            try:
                models[name] = joblib.load(path)
            except Exception as exc2:
                print(f"Second attempt failed loading {path}: {exc2!r}")
                raise RuntimeError(f"Failed to load model {name} after retrains") from exc2

    return models


print('sklearn:', sklearn.__version__)
print('pandas:', pd.__version__)
MODELS = load_or_train()


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "UP", "models": list(MODELS.keys())})


@app.post("/train")
def train() -> Any:
    global MODELS
    metrics = train_all_models(DATASET_DIR, MODEL_DIR)
    MODELS = load_or_train()
    return jsonify(metrics)


@app.post("/predict")
def predict() -> Any:
    payload = request.get_json(force=True)
    patient = normalize_input(payload)

    response: Dict[str, Any] = {"diseases": {}, "recommendations": build_recommendations(patient)}
    for disease, features in (("diabetes", DIABETES_FEATURES), ("heart", HEART_FEATURES)):
        bundle = MODELS[disease]
        frame = pd.DataFrame([{feature: patient.get(feature, 0) for feature in features}])
        model = bundle.pipeline.named_steps["model"]
        classes = getattr(model, "classes_", None)
        disease_class_index = 1
        if classes is not None:
            try:
                disease_class_index = int(list(classes).index(1))
            except ValueError:
                disease_class_index = 1
        model_probability = float(bundle.pipeline.predict_proba(frame)[0][disease_class_index])
        final_probability = calibrate_probability(disease, model_probability, patient)
        probability = final_probability * 100
        response["diseases"][disease] = {
            "disease": disease,
            "rawProbability": model_probability,
            "modelProbability": round(model_probability * 100, 2),
            "calibratedProbability": round(probability, 2),
            "probability": round(probability, 2),
            "risk": risk_label(probability),
            "explanation": explain_prediction(bundle, frame),
        }

    return jsonify(response)


@app.post("/explain")
def explain() -> Any:
    payload = request.get_json(force=True)
    disease = payload.get("disease", "diabetes")
    if disease not in MODELS:
        return jsonify({"error": "Unsupported disease"}), 400
    patient = normalize_input(payload)
    features = DIABETES_FEATURES if disease == "diabetes" else HEART_FEATURES
    frame = pd.DataFrame([{feature: patient.get(feature, 0) for feature in features}])
    return jsonify(explain_prediction(MODELS[disease], frame))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

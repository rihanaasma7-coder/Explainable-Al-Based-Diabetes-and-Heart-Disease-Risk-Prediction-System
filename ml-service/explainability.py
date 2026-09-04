from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer


EXPECTED_FEATURES = ["age", "gender", "glucose", "bmi", "cholesterol", "bloodPressure"]


def _clean_feature_name(name: str) -> str:
    cleaned = name
    for prefix in ("num__", "cat__", "preprocessor__", "selector__"):
        cleaned = cleaned.replace(prefix, "")
    if cleaned.startswith("gender_"):
        return "gender"
    return cleaned


def _transformed_feature_names(bundle) -> List[str]:
    features = bundle.pipeline.named_steps["features"]
    try:
        return [_clean_feature_name(name) for name in features.get_feature_names_out()]
    except Exception:
        return list(getattr(bundle, "feature_names", EXPECTED_FEATURES))


def _rank_scores(scores: Dict[str, float], limit: int = 5) -> List[Dict]:
    ranked = sorted(scores.items(), key=lambda item: abs(item[1]), reverse=True)
    return [{"feature": name, "impact": round(float(value), 4)} for name, value in ranked[:limit]]


def _fallback_factor_scores(bundle, frame: pd.DataFrame) -> List[Dict]:
    model = bundle.pipeline.named_steps["model"]
    names = _transformed_feature_names(bundle)
    if hasattr(model, "feature_importances_"):
        raw = np.asarray(model.feature_importances_, dtype=float)
    else:
        raw = np.abs(np.asarray(getattr(model, "coef_", [[1] * len(names)]), dtype=float)[0])

    scores: Dict[str, float] = defaultdict(float)
    for name, value in zip(names, raw):
        scores[_clean_feature_name(name)] += float(abs(value))

    for feature in frame.columns:
        scores.setdefault(feature, 0.0)
    return _rank_scores(scores)


def _class_one_values(values) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim == 3:
        return arr[0, :, 1]
    if arr.ndim == 2:
        return arr[0]
    return arr.reshape(-1)


def _shap_factors(bundle, frame: pd.DataFrame) -> List[Dict]:
    features = bundle.pipeline.named_steps["features"]
    model = bundle.pipeline.named_steps["model"]
    background = getattr(bundle, "background_frame", frame)[list(frame.columns)]

    background_transformed = features.transform(background)
    frame_transformed = features.transform(frame)
    names = _transformed_feature_names(bundle)

    try:
        explainer = shap.TreeExplainer(model, data=background_transformed, feature_names=names)
        values = _class_one_values(explainer.shap_values(frame_transformed))
    except Exception:
        explainer = shap.Explainer(model.predict_proba, background_transformed, feature_names=names)
        values = _class_one_values(explainer(frame_transformed).values)

    scores: Dict[str, float] = defaultdict(float)
    for name, value in zip(names, values):
        scores[_clean_feature_name(name)] += abs(float(value))

    if not scores or all(value == 0 for value in scores.values()):
        return _fallback_factor_scores(bundle, frame)
    return _rank_scores(scores)


def _encode_lime_frame(frame: pd.DataFrame) -> pd.DataFrame:
    encoded = frame.copy()
    encoded["gender"] = encoded["gender"].map({"Female": 0, "Male": 1, "Other": 2}).fillna(2).astype(int)
    return encoded


def _decode_lime_rows(rows: np.ndarray, columns: List[str]) -> pd.DataFrame:
    decoded = pd.DataFrame(rows, columns=columns)
    gender_map = {0: "Female", 1: "Male", 2: "Other"}
    decoded["gender"] = decoded["gender"].round().clip(0, 2).astype(int).map(gender_map)
    return decoded


def _lime_factors(bundle, frame: pd.DataFrame) -> List[Dict]:
    background = getattr(bundle, "background_frame", frame)[list(frame.columns)].copy()
    columns = list(frame.columns)
    encoded_background = _encode_lime_frame(background)
    encoded_frame = _encode_lime_frame(frame)
    gender_index = columns.index("gender")

    explainer = LimeTabularExplainer(
        training_data=encoded_background.to_numpy(dtype=float),
        feature_names=columns,
        categorical_features=[gender_index],
        categorical_names={gender_index: ["Female", "Male", "Other"]},
        class_names=["Low risk", "High risk"],
        mode="classification",
        discretize_continuous=True,
        random_state=42,
    )

    explanation = explainer.explain_instance(
        encoded_frame.iloc[0].to_numpy(dtype=float),
        lambda rows: bundle.pipeline.predict_proba(_decode_lime_rows(rows, columns)),
        labels=(1,),
        num_features=5,
    )

    factors = [
        {"feature": feature, "impact": round(float(weight), 4), "weight": round(float(weight), 4)}
        for feature, weight in explanation.as_list(label=1)
    ]
    if not factors or all(item["impact"] == 0 for item in factors):
        return _fallback_factor_scores(bundle, frame)
    return factors


def explain_prediction(bundle, frame: pd.DataFrame) -> Dict:
    try:
        shap_factors = _shap_factors(bundle, frame)
    except Exception:
        shap_factors = _fallback_factor_scores(bundle, frame)

    try:
        lime_factors = _lime_factors(bundle, frame)
    except Exception:
        lime_factors = _fallback_factor_scores(bundle, frame)

    return {
        "topFactors": [item["feature"] for item in shap_factors[:3]],
        "shapFactors": shap_factors,
        "limeFactors": lime_factors,
        "plots": {
            "waterfall": "Generate from SHAP values in notebook or dashboard export.",
            "summary": "Use ml-service/processed datasets with SHAP summary_plot for report graphics.",
        },
    }

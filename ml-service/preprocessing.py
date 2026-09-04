from __future__ import annotations

import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURE_NAMES = ["age", "gender", "glucose", "bmi", "cholesterol", "bloodPressure", "heartRate"]
DIABETES_FEATURES = FEATURE_NAMES
HEART_FEATURES = ["age", "gender", "glucose", "bmi", "cholesterol", "bloodPressure"]


def normalize_input(payload: Dict) -> Dict:
    """Normalize API field names so both Kaggle schemas can share one contract."""
    gender = payload.get("gender", "Male")
    return {
        "age": float(payload.get("age", 0)),
        "gender": str(gender).title(),
        "glucose": float(payload.get("glucose", payload.get("blood_glucose_level", 0))),
        "bmi": float(payload.get("bmi", 0)),
        "bloodPressure": float(payload.get("bloodPressure", payload.get("trestbps", 0))),
        "cholesterol": float(payload.get("cholesterol", payload.get("chol", 0))),
        "heartRate": float(payload.get("heartRate", payload.get("thalach", 0))),
    }


def remove_outliers_iqr(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        q1, q3 = cleaned[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        cleaned = cleaned[(cleaned[column] >= lower) & (cleaned[column] <= upper)]
    return cleaned


def _common_pipeline(feature_names: list[str]) -> Pipeline:
    categorical = ["gender"]
    numeric = [feature for feature in feature_names if feature not in categorical]
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    return Pipeline([("preprocessor", preprocessor)])


def preprocess_diabetes(dataset_dir: str, processed_dir: str) -> Tuple[pd.DataFrame, pd.Series, Pipeline]:
    path = os.path.join(dataset_dir, "diabetes.csv")
    df = pd.read_csv(path)
    df = df.rename(columns={"blood_glucose_level": "glucose"})
    if "diabetes" not in df.columns:
        raise ValueError("diabetes.csv must contain a diabetes target column")

    if "bloodPressure" not in df.columns:
        df["bloodPressure"] = df.get("hypertension", 0).astype(float) * 30 + 120
    if "cholesterol" not in df.columns:
        df["cholesterol"] = 200
    df["heartRate"] = df.get("heartRate", 72)
    df = df[DIABETES_FEATURES + ["diabetes"]].replace([np.inf, -np.inf], np.nan)
    df = remove_outliers_iqr(df.dropna(subset=["diabetes"]), ["age", "glucose", "bmi"])

    X, y = df[DIABETES_FEATURES], df["diabetes"].astype(int)
    pipeline = _common_pipeline(DIABETES_FEATURES)
    os.makedirs(processed_dir, exist_ok=True)
    df.to_csv(os.path.join(processed_dir, "diabetes_processed.csv"), index=False)
    return X, y, pipeline


def preprocess_heart(dataset_dir: str, processed_dir: str) -> Tuple[pd.DataFrame, pd.Series, Pipeline]:
    path = os.path.join(dataset_dir, "cardio_train.csv")
    df = pd.read_csv(path, sep=";")

    # Convert raw data into model-ready features matching the UI contract.
    df = df.rename(columns={"ap_hi": "bloodPressure", "gluc": "glucose"})
    df["age"] = df["age"].astype(float) / 365.0
    df["gender"] = df["gender"].map({1: "Female", 2: "Male"})
    df["bmi"] = df["weight"].astype(float) / ((df["height"].astype(float) / 100) ** 2)
    df["bloodPressure"] = df["bloodPressure"].astype(float)

    cholesterol_map = {1: 180.0, 2: 240.0, 3: 320.0}
    glucose_map = {1: 90.0, 2: 120.0, 3: 160.0}
    df["cholesterol"] = df["cholesterol"].map(cholesterol_map)
    df["glucose"] = df["glucose"].map(glucose_map)

    # Clean invalid records from the cardiovascular dataset.
    df = df.drop_duplicates()
    df = df[df["height"] > 0]
    df = df[df["weight"] > 0]
    df = df[df["bloodPressure"] > 0]
    df = df[df["ap_lo"] > 0]
    df = df[df["bloodPressure"] >= df["ap_lo"]]
    df = df[df["age"] >= 18]
    df = df[df["bmi"] >= 10]
    df = df[df["bmi"] <= 60]
    df = df[df["cholesterol"].notna()]
    df = df[df["glucose"].notna()]
    df = df[df["gender"].isin(["Male", "Female"])]

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=HEART_FEATURES + ["cardio"])

    df = remove_outliers_iqr(df, ["age", "bmi", "bloodPressure"])

    df = df[HEART_FEATURES + ["cardio"]]
    df["cardio"] = df["cardio"].astype(int)

    X, y = df[HEART_FEATURES], df["cardio"]
    pipeline = _common_pipeline(HEART_FEATURES)
    os.makedirs(processed_dir, exist_ok=True)
    df.to_csv(os.path.join(processed_dir, "heart_processed.csv"), index=False)
    return X, y, pipeline

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "matplotlib"),
)

import shap

from .inference import prepare_model_input
from .region_service import get_region_row


def _to_float(value, name: str) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"SHAP result contains non-finite value: {name}")
    return result


def _validate_numeric_frame(frame: pd.DataFrame, context: str) -> pd.DataFrame:
    numeric = frame.copy()
    for column in numeric.columns:
        numeric[column] = pd.to_numeric(numeric[column], errors="coerce")

    if numeric.isna().any().any():
        bad = numeric.columns[numeric.isna().any()].tolist()
        raise ValueError(f"Invalid/missing {context} input columns: {bad}")

    values = numeric.to_numpy(dtype=float)
    if np.isinf(values).any():
        bad = numeric.columns[np.isinf(values).any(axis=0)].tolist()
        raise ValueError(f"Non-finite {context} input columns: {bad}")

    return numeric


def _records_from_frame(frame: pd.DataFrame) -> list[dict]:
    records = frame.to_dict("records")
    json.dumps(records, ensure_ascii=False)
    return records


def global_shap(model, X: pd.DataFrame, top_k: int = 10) -> dict:
    """Calculate JSON-friendly global SHAP feature importance."""
    X_numeric = _validate_numeric_frame(X, "global SHAP")

    explainer = shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
    )
    shap_values = explainer(X_numeric)
    values = shap_values.values

    importance = (
        pd.DataFrame(
            {
                "feature": X_numeric.columns,
                "mean_abs_shap": np.abs(values).mean(axis=0),
                "mean_shap": values.mean(axis=0),
            }
        )
        .sort_values("mean_abs_shap", ascending=False)
        .head(top_k)
        .reset_index(drop=True)
    )

    importance["mean_abs_shap"] = importance["mean_abs_shap"].map(
        lambda value: _to_float(value, "mean_abs_shap")
    )
    importance["mean_shap"] = importance["mean_shap"].map(
        lambda value: _to_float(value, "mean_shap")
    )

    result = {"top_features": _records_from_frame(importance)}
    json.dumps(result, ensure_ascii=False)
    return result


def local_shap(
    model,
    X_row: pd.DataFrame,
    top_k: int = 5,
) -> dict:
    """Calculate JSON-friendly local SHAP contributions for one model row."""
    X_numeric = _validate_numeric_frame(X_row, "local SHAP")

    if X_numeric.shape[0] != 1:
        raise ValueError(f"local_shap expects exactly one row, got {X_numeric.shape[0]}")

    explainer = shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
    )
    shap_values = explainer(X_numeric)
    values = shap_values.values[0]

    prediction = _to_float(model.predict(X_numeric)[0], "prediction")

    contribution = (
        pd.DataFrame(
            {
                "feature": X_numeric.columns,
                "feature_value": X_numeric.iloc[0].to_numpy(dtype=float),
                "shap_value": values,
                "abs_shap": np.abs(values),
            }
        )
        .sort_values("abs_shap", ascending=False)
        .head(top_k)
        .reset_index(drop=True)
    )

    for column in ["feature_value", "shap_value", "abs_shap"]:
        contribution[column] = contribution[column].map(
            lambda value, column=column: _to_float(value, column)
        )

    result = {
        "prediction": prediction,
        "top_features": _records_from_frame(contribution),
    }
    json.dumps(result, ensure_ascii=False)
    return result


def get_local_shap(
    model,
    latest_df: pd.DataFrame,
    region_code: int | str,
    features: list[str],
    top_k: int = 5,
) -> dict:
    """Find one region row and return JSON-friendly local SHAP contributions."""
    try:
        normalized_region_code = int(region_code)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"region_code must be convertible to int: {region_code}") from exc

    row = get_region_row(latest_df, normalized_region_code)
    X_row = prepare_model_input(row, features)
    shap_result = local_shap(model, X_row, top_k=top_k)

    result = {
        "region_code": normalized_region_code,
        "year": int(row["연도"]),
        "시군": str(row["시군"]),
        "읍면동": str(row["읍면동"]),
        "prediction": shap_result["prediction"],
        "top_features": shap_result["top_features"],
    }
    json.dumps(result, ensure_ascii=False)
    return result

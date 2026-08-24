import numpy as np
import pandas as pd

from src.region_service import get_region_row


def prepare_model_input(row: pd.Series, features: list[str]) -> pd.DataFrame:
    """Convert one region row into a validated one-row model input DataFrame."""
    if not isinstance(features, list) or not features:
        raise ValueError("features must be a non-empty list")

    missing_features = [feature for feature in features if feature not in row.index]
    if missing_features:
        raise ValueError(f"Row missing model features: {missing_features}")

    values = row.loc[features].copy()
    numeric_values = pd.to_numeric(values, errors="coerce")

    nan_features = numeric_values.index[numeric_values.isna()].tolist()
    if nan_features:
        raise ValueError(f"Model input contains NaN after numeric conversion: {nan_features}")

    inf_mask = np.isinf(numeric_values.to_numpy(dtype=float))
    if inf_mask.any():
        inf_features = numeric_values.index[inf_mask].tolist()
        raise ValueError(f"Model input contains inf values: {inf_features}")

    model_input = pd.DataFrame([numeric_values.to_numpy(dtype=float)], columns=features)

    if list(model_input.columns) != features:
        raise ValueError("Model input columns do not match feature order")

    expected_shape = (1, len(features))
    if model_input.shape != expected_shape:
        raise ValueError(
            f"Model input shape must be {expected_shape}, got {model_input.shape}"
        )

    return model_input


def predict_region(
    model,
    latest_df: pd.DataFrame,
    region_code: int | str,
    features: list[str],
) -> dict:
    """Predict next-year net migration rate for one region code."""
    try:
        normalized_region_code = int(region_code)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"region_code must be convertible to int: {region_code}") from exc

    row = get_region_row(latest_df, normalized_region_code)
    model_input = prepare_model_input(row, features)

    if not hasattr(model, "predict"):
        raise ValueError(f"model must provide a predict method, got {type(model).__name__}")

    try:
        prediction = model.predict(model_input)
    except Exception as exc:
        raise ValueError(f"model.predict failed for region_code={normalized_region_code}") from exc

    prediction_array = np.asarray(prediction).reshape(-1)

    if prediction_array.size != 1:
        raise ValueError(f"Expected exactly one prediction, got {prediction_array.size}")

    prediction_value = float(prediction_array[0])
    if not np.isfinite(prediction_value):
        raise ValueError(f"Prediction is not finite: {prediction_value}")

    return {
        "region_code": normalized_region_code,
        "year": int(row["연도"]),
        "시군": str(row["시군"]),
        "읍면동": str(row["읍면동"]),
        "prediction": prediction_value,
    }

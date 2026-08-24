import json

from src.inference import predict_region
from src.region_service import get_region_summary


def get_region_result(
    model,
    latest_df,
    region_code: int | str,
    features: list[str],
    target: str,
) -> dict:
    """Return frontend-ready regional status and prediction for one region code."""
    summary = get_region_summary(latest_df, region_code)
    prediction = predict_region(model, latest_df, region_code, features)

    result = {
        **summary,
        "prediction": {
            "target": str(target),
            "value": float(prediction["prediction"]),
        },
    }

    try:
        json.dumps(result, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("Region result is not JSON serializable") from exc

    return result

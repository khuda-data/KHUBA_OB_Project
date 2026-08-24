from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_FILENAME = "final_model.pkl"
REGION_DATA_FILENAME = "충북_최종학습데이터_E세트.csv"


def _resolve_project_file(preferred_path: Path, fallback_path: Path) -> Path:
    if preferred_path.exists():
        return preferred_path
    return fallback_path


MODEL_PATH = _resolve_project_file(
    PROJECT_ROOT / "models" / MODEL_FILENAME,
    PROJECT_ROOT / MODEL_FILENAME,
)
REGION_DATA_PATH = _resolve_project_file(
    PROJECT_ROOT / "data" / REGION_DATA_FILENAME,
    PROJECT_ROOT / REGION_DATA_FILENAME,
)

REQUIRED_MODEL_KEYS = {"model", "features", "target"}
EXPECTED_FEATURE_COUNT = 25
EXPECTED_TARGET = "타깃_다음해_순이동률"
REQUIRED_REGION_COLUMNS = ["지역코드", "시군", "읍면동", "연도"]


def load_model_bundle(model_path: Path = MODEL_PATH) -> dict:
    """Load and validate the final model bundle."""
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    bundle = joblib.load(model_path)
    if not isinstance(bundle, dict):
        raise ValueError(f"Model bundle must be a dict, got {type(bundle).__name__}")

    missing_keys = REQUIRED_MODEL_KEYS - set(bundle.keys())
    if missing_keys:
        raise ValueError(f"Model bundle missing required keys: {sorted(missing_keys)}")

    features = bundle["features"]
    target = bundle["target"]

    if not isinstance(features, list):
        raise ValueError(f"Model bundle 'features' must be a list, got {type(features).__name__}")
    if len(features) != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_FEATURE_COUNT} features, got {len(features)}"
        )
    if target != EXPECTED_TARGET:
        raise ValueError(f"Expected target '{EXPECTED_TARGET}', got '{target}'")

    return bundle


def load_region_data(
    data_path: Path = REGION_DATA_PATH,
    model_bundle: dict | None = None,
) -> pd.DataFrame:
    """Load and validate the region-level model input data."""
    if not data_path.exists():
        raise FileNotFoundError(f"Region data file not found: {data_path}")

    bundle = model_bundle if model_bundle is not None else load_model_bundle()
    features = bundle["features"]

    df = pd.read_csv(data_path, encoding="utf-8-sig")

    missing_required_columns = [c for c in REQUIRED_REGION_COLUMNS if c not in df.columns]
    if missing_required_columns:
        raise ValueError(
            f"Region data missing required columns: {missing_required_columns}"
        )

    missing_features = [c for c in features if c not in df.columns]
    if missing_features:
        raise ValueError(f"Region data missing model features: {missing_features}")

    feature_missing_count = int(df[features].isna().sum().sum())
    if feature_missing_count:
        missing_by_feature = {
            c: int(df[c].isna().sum()) for c in features if df[c].isna().any()
        }
        raise ValueError(
            "Region data contains NaN values in model features: "
            f"{missing_by_feature}"
        )

    return df


def build_latest_region_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return one latest-year row per region code without mutating the source frame."""
    required_columns = ["지역코드", "시군", "읍면동", "연도"]
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Region data missing required columns: {missing_columns}")

    latest_years = df.groupby("지역코드")["연도"].transform("max")
    latest_df = df.loc[df["연도"].eq(latest_years)].copy()

    duplicated_latest_codes = latest_df.loc[
        latest_df.duplicated("지역코드", keep=False), "지역코드"
    ].drop_duplicates()
    if not duplicated_latest_codes.empty:
        raise ValueError(
            "Multiple rows found for the same region code and latest year: "
            f"{duplicated_latest_codes.tolist()}"
        )

    if len(latest_df) != latest_df["지역코드"].nunique():
        raise ValueError("Latest region data must contain exactly one row per region code")

    return latest_df.sort_values(["시군", "읍면동"]).reset_index(drop=True)


def inspect_loaded_assets() -> dict:
    """Return a compact inspection summary for the configured model and data."""
    bundle = load_model_bundle()
    df = load_region_data(model_bundle=bundle)
    features = bundle["features"]
    latest_df = build_latest_region_data(df)

    return {
        "model_type": type(bundle["model"]).__name__,
        "feature_count": len(features),
        "target": bundle["target"],
        "csv_shape": tuple(df.shape),
        "region_code_unique_count": int(df["지역코드"].nunique()),
        "sigungu_unique_count": int(df["시군"].nunique()),
        "years": sorted(int(y) for y in df["연도"].dropna().unique()),
        "feature_missing_count": int(df[features].isna().sum().sum()),
        "latest_row_count": len(latest_df),
        "latest_region_code_unique_count": int(latest_df["지역코드"].nunique()),
        "latest_rows_equal_unique_region_codes": len(latest_df)
        == int(latest_df["지역코드"].nunique()),
        "latest_year_counts": {
            int(year): int(count)
            for year, count in latest_df["연도"].value_counts().sort_index().items()
        },
        "latest_non_2024_regions": latest_df.loc[
            latest_df["연도"] != 2024, ["지역코드", "시군", "읍면동", "연도"]
        ].to_dict("records"),
        "latest_duplicate_region_code_count": int(
            latest_df.duplicated("지역코드").sum()
        ),
        "latest_duplicate_sigungu_eupmyeondong_count": int(
            latest_df.duplicated(["시군", "읍면동"]).sum()
        ),
    }


if __name__ == "__main__":
    summary = inspect_loaded_assets()
    for key, value in summary.items():
        print(f"{key}: {value}")

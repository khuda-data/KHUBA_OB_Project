import math

import pandas as pd


REQUIRED_REGION_COLUMNS = ["지역코드", "시군", "읍면동"]
POPULATION_COLUMNS = [
    "총인구",
    "청년비율",
    "유소년비율",
    "고령화율",
    "가임여성비율",
    "인구증감률_전년",
]
ACCESSIBILITY_COLUMNS = [
    "의료_평균접근거리",
    "응급의료_평균접근거리",
    "산업거점_평균접근거리",
    "교통거점_평균접근거리",
    "문화시설_평균접근거리",
    "교육시설_평균접근거리",
    "상업시설_평균접근거리",
]
LIVING_AREA_COLUMNS = [
    "3분이내_의료시설수",
    "5분이내_의료시설수",
    "10분이내_의료시설수",
    "20분이내_의료시설수",
    "3분이내_문화시설수",
    "5분이내_문화시설수",
    "10분이내_문화시설수",
    "20분이내_문화시설수",
    "3분이내_교육기관수",
    "5분이내_교육기관수",
    "10분이내_교육기관수",
    "20분이내_교육기관수",
]


def _validate_region_columns(df: pd.DataFrame) -> None:
    missing_columns = [c for c in REQUIRED_REGION_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Region data missing required columns: {missing_columns}")


def get_sigungu_list(latest_df: pd.DataFrame) -> list[str]:
    """Return sorted unique sigungu names from latest region data."""
    _validate_region_columns(latest_df)
    return sorted(latest_df["시군"].dropna().astype(str).unique().tolist())


def get_eupmyeondong_list(latest_df: pd.DataFrame, sigungu: str) -> list[str]:
    """Return sorted unique eupmyeondong names for a sigungu."""
    _validate_region_columns(latest_df)

    matched = latest_df[latest_df["시군"].astype(str).eq(str(sigungu))]
    if matched.empty:
        raise ValueError(f"Unknown sigungu: {sigungu}")

    return sorted(matched["읍면동"].dropna().astype(str).unique().tolist())


def get_region_code(
    latest_df: pd.DataFrame,
    sigungu: str,
    eupmyeondong: str,
) -> int:
    """Return the region code for an exact sigungu + eupmyeondong match."""
    _validate_region_columns(latest_df)

    matched = latest_df[
        latest_df["시군"].astype(str).eq(str(sigungu))
        & latest_df["읍면동"].astype(str).eq(str(eupmyeondong))
    ]

    if matched.empty:
        raise ValueError(f"Region not found: sigungu={sigungu}, eupmyeondong={eupmyeondong}")
    if len(matched) > 1:
        raise ValueError(
            f"Multiple regions found: sigungu={sigungu}, eupmyeondong={eupmyeondong}"
        )

    return int(matched.iloc[0]["지역코드"])


def get_region_row(latest_df: pd.DataFrame, region_code: int | str) -> pd.Series:
    """Return exactly one latest region row by region code."""
    _validate_region_columns(latest_df)

    target_code = str(region_code)
    matched = latest_df[latest_df["지역코드"].astype(str).eq(target_code)]

    if matched.empty:
        raise ValueError(f"Region code not found: {region_code}")
    if len(matched) > 1:
        raise ValueError(f"Multiple rows found for region code: {region_code}")

    return matched.iloc[0].copy()


def _to_json_value(value, column: str):
    if pd.isna(value):
        raise ValueError(f"Region summary contains NaN: {column}")

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Region summary contains non-finite value: {column}")

    return value


def _extract_columns(row: pd.Series, columns: list[str], group_name: str) -> dict:
    missing_columns = [column for column in columns if column not in row.index]
    if missing_columns:
        raise ValueError(f"Region summary missing {group_name} columns: {missing_columns}")

    return {column: _to_json_value(row[column], column) for column in columns}


def get_region_summary(latest_df: pd.DataFrame, region_code: int | str) -> dict:
    """Return frontend-ready latest regional status values for one region code."""
    try:
        normalized_region_code = int(region_code)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"region_code must be convertible to int: {region_code}") from exc

    row = get_region_row(latest_df, normalized_region_code)

    return {
        "region": {
            "region_code": normalized_region_code,
            "year": int(_to_json_value(row["연도"], "연도")),
            "시군": str(_to_json_value(row["시군"], "시군")),
            "읍면동": str(_to_json_value(row["읍면동"], "읍면동")),
        },
        "population": _extract_columns(row, POPULATION_COLUMNS, "population"),
        "accessibility": _extract_columns(row, ACCESSIBILITY_COLUMNS, "accessibility"),
        "living_area": _extract_columns(row, LIVING_AREA_COLUMNS, "living_area"),
    }

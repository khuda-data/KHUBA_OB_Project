"""
충북 읍면동 GeoJSON 기반 지도 데이터
──────────────────────────────────────────
지역코드(adm_cd2)를 AI 서비스 레이어(src.region_service)가 쓰는 지역코드와
동일한 키로 사용해, 지도 폴리곤/좌표를 AI 분석 결과와 1:1로 연결합니다.
(과거 수기로 입력한 좌표/코드 테이블은 실제 학습 데이터의 읍면동 표기와
어긋나는 항목이 있어 GeoJSON 원본에서 직접 파생하는 방식으로 대체했습니다.)
"""

import json
import os

CHUNGBUK_CENTER = [36.63, 127.93]
CHUNGBUK_ZOOM = 9

GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "chungbuk_dong.geojson")

# 인구감소지역 (6개) — AI 서비스 레이어의 "시군" 표기와 동일
DEPOPULATION_AREAS = {"제천시", "보은군", "옥천군", "영동군", "괴산군", "단양군"}

# AI 서비스 레이어의 "시군" → GeoJSON sggnm 매핑
# (청주시는 AI 데이터에서 "청주시"로 통합되어 있지만, GeoJSON은 4개 구로 분리되어 있음)
SIGUNGU_TO_SGGNM = {
    "청주시": ["청주시상당구", "청주시서원구", "청주시청원구", "청주시흥덕구"],
}

_geojson_cache = None


def load_geojson() -> dict:
    """충북 읍면동 GeoJSON 로드 (캐싱)."""
    global _geojson_cache
    if _geojson_cache is None:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            _geojson_cache = json.load(f)
    return _geojson_cache


def _feature_index() -> dict:
    """지역코드(adm_cd2, str) → GeoJSON feature."""
    geo = load_geojson()
    return {f["properties"]["adm_cd2"]: f for f in geo["features"]}


def get_region_feature(region_code) -> dict:
    """지역코드로 GeoJSON feature 조회. 없으면 None."""
    return _feature_index().get(str(region_code))


def _ring_points(geometry: dict) -> list:
    """Polygon/MultiPolygon의 모든 정점을 [lon, lat] 리스트로 평탄화."""
    coords = geometry.get("coordinates", [])
    gtype = geometry.get("type")
    if gtype == "Polygon":
        rings = coords
    elif gtype == "MultiPolygon":
        rings = [ring for polygon in coords for ring in polygon]
    else:
        return []
    points = []
    for ring in rings:
        points.extend(ring)
    return points


def get_region_coords(region_code) -> list:
    """행정경계 정점 평균 기반 근사 중심좌표 [lat, lon] 반환."""
    feature = get_region_feature(region_code)
    if feature is None:
        return CHUNGBUK_CENTER

    points = _ring_points(feature["geometry"])
    if not points:
        return CHUNGBUK_CENTER

    lon_avg = sum(p[0] for p in points) / len(points)
    lat_avg = sum(p[1] for p in points) / len(points)
    return [lat_avg, lon_avg]


def get_region_bounds(region_code) -> list:
    """행정경계 bounding box [[south, west], [north, east]] 반환.

    읍면동마다 면적 편차가 커서 고정 zoom 대신 지도에서 fit_bounds로 사용합니다.
    """
    feature = get_region_feature(region_code)
    if feature is None:
        south, west = CHUNGBUK_CENTER[0] - 0.05, CHUNGBUK_CENTER[1] - 0.05
        north, east = CHUNGBUK_CENTER[0] + 0.05, CHUNGBUK_CENTER[1] + 0.05
        return [[south, west], [north, east]]

    points = _ring_points(feature["geometry"])
    if not points:
        return [[CHUNGBUK_CENTER[0] - 0.05, CHUNGBUK_CENTER[1] - 0.05],
                [CHUNGBUK_CENTER[0] + 0.05, CHUNGBUK_CENTER[1] + 0.05]]

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return [[min(lats), min(lons)], [max(lats), max(lons)]]


def get_sigu_geojson(sigungu: str) -> dict:
    """선택 시군에 해당하는 읍면동 GeoJSON만 필터링하여 반환 (청주시는 4개 구 통합)."""
    geo = load_geojson()
    target_sggnms = SIGUNGU_TO_SGGNM.get(sigungu, [sigungu])

    return {
        "type": "FeatureCollection",
        "features": [
            f for f in geo["features"]
            if f["properties"]["sggnm"] in target_sggnms
        ],
    }


def is_depopulation_area(sigungu: str) -> bool:
    """인구감소지역 여부 반환."""
    return sigungu in DEPOPULATION_AREAS

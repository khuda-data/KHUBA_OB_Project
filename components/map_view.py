"""Folium 지도 빌더 — 단일 지역 강조 지도 / 충북 전체 개요 지도."""

import folium

from data.dong_data import CHUNGBUK_CENTER, get_region_bounds, get_region_coords, get_sigu_geojson, load_geojson


def create_region_map(selected_sigu: str, selected_dong: str, region_code: int) -> folium.Map:
    """선택된 읍·면·동을 강조 표시하는 지도 (현황 분석 페이지)."""
    target_coords = get_region_coords(region_code)
    selected_code = str(region_code)

    m = folium.Map(location=target_coords, tiles="OpenStreetMap", control_scale=True)
    m.fit_bounds(get_region_bounds(region_code), padding=(40, 40))

    sigu_geo = get_sigu_geojson(selected_sigu)

    folium.GeoJson(
        sigu_geo,
        name="읍면동 경계",
        style_function=lambda feature: {
            "fillColor": "#dc2626" if feature["properties"]["adm_cd2"] == selected_code else "#0055aa",
            "color": "#1a3a5c" if feature["properties"]["adm_cd2"] == selected_code else "#64748b",
            "weight": 2.5 if feature["properties"]["adm_cd2"] == selected_code else 1,
            "fillOpacity": 0.45 if feature["properties"]["adm_cd2"] == selected_code else 0.12,
            "dashArray": "" if feature["properties"]["adm_cd2"] == selected_code else "3",
        },
        highlight_function=lambda feature: {
            "weight": 3,
            "fillOpacity": 0.5,
            "fillColor": "#ef4444" if feature["properties"]["adm_cd2"] == selected_code else "#3b82f6",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["adm_nm"],
            aliases=[""],
            style="font-family:Pretendard,sans-serif; font-size:13px; font-weight:600;",
            sticky=True,
        ),
    ).add_to(m)

    folium.Marker(
        location=target_coords,
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-family:Pretendard,sans-serif;
                font-size:11px; font-weight:700;
                color:#1a3a5c; background:white;
                border:2px solid #dc2626;
                border-radius:6px; padding:2px 6px;
                white-space:nowrap; box-shadow:0 1px 4px rgba(0,0,0,0.15);
            ">{selected_dong}</div>
            """,
            icon_size=(100, 30),
            icon_anchor=(50, 15),
        ),
    ).add_to(m)

    return m


def _prediction_color(value: float, vmin: float, vmax: float) -> str:
    """예측 순이동률 값을 빨강(유출)~파랑(유입) 색상으로 매핑."""
    if value >= 0:
        span = max(vmax, 1e-6)
        t = min(value / span, 1.0)
        # 옅은 파랑(#dbeafe) -> 진한 파랑(#0055aa)
        r = round(219 + (0 - 219) * t)
        g = round(234 + (85 - 234) * t)
        b = round(254 + (170 - 254) * t)
    else:
        span = max(abs(vmin), 1e-6)
        t = min(abs(value) / span, 1.0)
        # 옅은 빨강(#fde8e8) -> 진한 빨강(#dc2626)
        r = round(253 + (220 - 253) * t)
        g = round(232 + (38 - 232) * t)
        b = round(232 + (38 - 232) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def create_overview_map(predictions: dict) -> folium.Map:
    """충북 전체 146개 읍·면·동을 예측 순이동률 기준 색상으로 표시하는 개요 지도.

    predictions: {지역코드: 예측 순이동률(%)} — ai_module.get_all_predictions() 결과.
    """
    geo = load_geojson()
    values = list(predictions.values())
    vmin, vmax = min(values), max(values)

    m = folium.Map(location=CHUNGBUK_CENTER, zoom_start=9, tiles="OpenStreetMap", control_scale=True)

    def style_function(feature):
        code = int(feature["properties"]["adm_cd2"])
        value = predictions.get(code)
        if value is None:
            return {"fillColor": "#cbd5e1", "color": "#94a3b8", "weight": 0.5, "fillOpacity": 0.15}
        return {
            "fillColor": _prediction_color(value, vmin, vmax),
            "color": "#64748b",
            "weight": 0.7,
            "fillOpacity": 0.75,
        }

    def tooltip_text(feature):
        code = int(feature["properties"]["adm_cd2"])
        value = predictions.get(code)
        value_txt = f"{value:+.2f}%" if value is not None else "데이터 없음"
        return f"{feature['properties']['adm_nm']}: 예측 순이동률 {value_txt}"

    for feature in geo["features"]:
        folium.GeoJson(
            feature,
            style_function=style_function,
            highlight_function=lambda _f: {"weight": 2.5, "color": "#0055aa"},
            tooltip=tooltip_text(feature),
        ).add_to(m)

    legend_html = """
    <div style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
        background: white; padding: 10px 14px; border-radius: 8px;
        border: 1px solid #dee2e6; font-family: Pretendard, sans-serif; font-size: 12px;">
        <b>다음 해 예측 순이동률</b><br>
        <span style="color:#666;">전입자와 전출자의 차이를 인구 대비 비율로 나타낸 지표</span><br>
        <span style="color:#dc2626;">■</span> 순유출(감소) &nbsp;
        <span style="color:#0055aa;">■</span> 순유입(증가)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

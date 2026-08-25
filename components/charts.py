"""Plotly 차트 빌더 (SHAP / What-if 비교)."""

import plotly.graph_objects as go

PLOTLY_CONFIG = {"displayModeBar": False}


def pretty(feature: str) -> str:
    """피처명(언더스코어)을 화면 표시용 라벨로 변환."""
    return feature.replace("_", " ")


def _padded_range(values: list, pad_ratio: float = 0.35, min_pad: float = 0.3) -> list:
    """막대/텍스트 라벨이 잘리지 않도록 min/max에 여유를 준 축 범위 계산."""
    vmin, vmax = min(values), max(values)
    span = vmax - vmin
    pad = max(span * pad_ratio, min_pad)
    return [vmin - pad, vmax + pad]


def make_shap_chart(shap_data: dict, title: str = "") -> go.Figure:
    """SHAP 수평 바 차트 (Plotly)."""
    features = [pretty(f) for f in shap_data.keys()][::-1]
    values = list(shap_data.values())[::-1]
    colors = ["#dc2626" if v < 0 else "#0055aa" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker=dict(color=colors, cornerradius=6),
        text=[f"{v:+.3f}" for v in values],
        textposition="outside",
        textfont=dict(size=12, family="Pretendard"),
        hovertemplate="<b>%{y}</b><br>SHAP: %{x:+.3f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, family="Pretendard")),
        xaxis_title="모델 예측 기여도 (SHAP Value)",
        yaxis_title="",
        height=280,
        margin=dict(l=10, r=40, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard"),
        xaxis=dict(zeroline=True, zerolinecolor="#cbd5e1", showgrid=False),
        yaxis=dict(showgrid=False),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Pretendard"),
    )
    return fig


def make_whatif_comparison_chart(base: float, scenario_values: dict, feature: str) -> go.Figure:
    """What-if Before/After 비교 차트."""
    labels = ["현재 예측"] + [f"{rate}% 개선" for rate in scenario_values.keys()]
    values = [base] + list(scenario_values.values())
    colors = ["#94a3b8"] + ["#5b8fc7", "#2f6fb0", "#0055aa"][:len(scenario_values)]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors, cornerradius=6),
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
        textfont=dict(size=13, family="Pretendard", color="#1e293b"),
        hovertemplate="<b>%{x}</b><br>예측 순이동률: %{y:+.2f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(
            text=f"'{pretty(feature)}' 개선 시 모델 예측 순이동률 변화",
            font=dict(size=14, family="Pretendard"),
        ),
        yaxis_title="예측 순이동률 (%)",
        height=320,
        margin=dict(l=10, r=20, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=True, zerolinecolor="#cbd5e1",
                   range=_padded_range(values)),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Pretendard"),
    )
    return fig

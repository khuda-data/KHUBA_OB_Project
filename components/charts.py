"""Plotly 차트 빌더 (SHAP / What-if 비교)."""

import plotly.graph_objects as go


def pretty(feature: str) -> str:
    """피처명(언더스코어)을 화면 표시용 라벨로 변환."""
    return feature.replace("_", " ")


def make_shap_chart(shap_data: dict, title: str = "") -> go.Figure:
    """SHAP 수평 바 차트 (Plotly)."""
    features = [pretty(f) for f in shap_data.keys()][::-1]
    values = list(shap_data.values())[::-1]
    colors = ["#dc2626" if v < 0 else "#0055aa" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in values],
        textposition="outside",
        textfont=dict(size=12, family="Pretendard"),
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
        xaxis=dict(zeroline=True, zerolinecolor="#cbd5e1", gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
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
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
        textfont=dict(size=13, family="Pretendard", color="#1e293b"),
    ))
    fig.update_layout(
        title=dict(
            text=f"'{pretty(feature)}' 개선 시 모델 예측 순이동률 변화",
            font=dict(size=14, family="Pretendard"),
        ),
        yaxis_title="예측 순이동률 (%)",
        height=300,
        margin=dict(l=10, r=20, t=50, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard"),
        yaxis=dict(gridcolor="#f1f5f9", zeroline=True, zerolinecolor="#cbd5e1"),
    )
    return fig

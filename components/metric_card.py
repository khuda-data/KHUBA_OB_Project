"""재사용 가능한 지표 카드 컴포넌트."""

import streamlit as st


def render_metric_card(label: str, value, unit: str = "") -> None:
    """단일 지표 카드 HTML 렌더링."""
    st.markdown(f"""
    <div class="gov-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value-group">
            <span class="metric-value">{value}</span>
            <span class="metric-unit">{unit}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_row(items: list[tuple]) -> None:
    """[(label, value, unit), ...] 를 한 행의 카드로 렌더링."""
    cols = st.columns(len(items))
    for col, (label, value, unit) in zip(cols, items):
        with col:
            render_metric_card(label, value, unit)

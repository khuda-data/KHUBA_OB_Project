"""재사용 가능한 지표 카드 컴포넌트."""

from __future__ import annotations

import streamlit as st


def render_metric_card(label: str, value, unit: str = "", value_color: str | None = None) -> None:
    """단일 지표 카드 HTML 렌더링."""
    value_style = f' style="color:{value_color};"' if value_color else ""
    st.markdown(f"""
    <div class="gov-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value-group">
            <span class="metric-value"{value_style}>{value}</span>
            <span class="metric-unit">{unit}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_row(items: list[tuple]) -> None:
    """[(label, value, unit), ...] 를 한 행의 카드로 렌더링."""
    cols = st.columns(len(items))
    for col, (label, value, unit) in zip(cols, items):
        with col:
            value_color = None
            if label == "전년 대비 인구증감률":
                numeric_value = float(str(value).replace(",", "").replace("%", ""))
                value_color = (
                    POSITIVE_COLOR
                    if numeric_value > 0
                    else NEGATIVE_COLOR
                    if numeric_value < 0
                    else NEUTRAL_COLOR
                )
            render_metric_card(label, value, unit, value_color)


POSITIVE_COLOR = "#00C853"
NEGATIVE_COLOR = "#FF5252"
NEUTRAL_COLOR = "#6B7280"


def render_signed_value(
    value_text: str,
    is_positive: bool,
    badge_text: str = "",
    badge_positive: bool | None = None,
    caption: str = "",
) -> None:
    """양수/음수에 따라 초록/빨강으로 강조한 큰 숫자 표시.

    다음 해 순이동률 예측, What-if 정책 적용 후 값처럼 부호가 의미를 가지는
    핵심 수치에 사용한다. badge_text가 본문과 다른 값(예: 변화량)을 나타낼 때는
    badge_positive로 배지 색을 본문과 독립적으로 지정할 수 있다.
    """
    color = POSITIVE_COLOR if is_positive else NEGATIVE_COLOR
    badge_color = POSITIVE_COLOR if (badge_positive if badge_positive is not None else is_positive) else NEGATIVE_COLOR
    badge_html = (
        f'<span class="signed-value-badge" style="color:{badge_color}; background:{badge_color}1a;">{badge_text}</span>'
        if badge_text else ""
    )
    caption_html = f'<div class="metric-caption">{caption}</div>' if caption else ""
    st.markdown(f"""
    <div class="signed-value-block">
        <div class="signed-value" style="color:{color};">{value_text}</div>
        {badge_html}
        {caption_html}
    </div>
    """, unsafe_allow_html=True)

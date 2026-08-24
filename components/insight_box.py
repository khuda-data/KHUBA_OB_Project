"""해석/안내 박스 컴포넌트 (frontend AI 예측·시뮬레이션 목업의 해석 박스 재현)."""

import streamlit as st


def info_box(html: str) -> None:
    """단순 해석/안내 박스 (좌측 파란 보더)."""
    st.markdown(f'<div class="gov-info-box">{html}</div>', unsafe_allow_html=True)


def ai_insight_box(title: str, body_html: str, tags: list[str]) -> None:
    """'AI 분석 결과 해석' 스타일 박스 — 제목 + 본문 + 해시태그 칩.

    tags에는 반드시 실제 계산된 값(피처명 등)만 넣는다 — 임의로 지어낸 정책 태그는 넣지 않는다.
    """
    tag_html = "".join(f'<span class="ai-tag">#{tag}</span>' for tag in tags)
    st.markdown(f"""
    <div class="ai-insight-box">
        <div class="ai-insight-title">{title}</div>
        <div class="ai-insight-body">{body_html}</div>
        <div class="ai-insight-tags">{tag_html}</div>
    </div>
    """, unsafe_allow_html=True)

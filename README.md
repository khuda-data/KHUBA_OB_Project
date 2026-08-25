# 충청지역 지역소멸 대응 AI 시뮬레이터 (MVP)

충청북도 읍·면·동 단위 지역소멸 대응을 위한 AI 기반 정책 시뮬레이션 웹 애플리케이션입니다.
AI 예측 / SHAP / What-if 계산은 공동 레포 [khuda-data/KHUBA_OB_Project](https://github.com/khuda-data/KHUBA_OB_Project) `main`에
머지된 메인개발 1의 서비스 레이어(`src/`)를 그대로 연동합니다.

UI는 `UI_Ref/*/DESIGN.md` + `code.html`/`screen.png` 목업(상단 탭 네비게이션 + 좌측 "분석 필터" 사이드바)을
Streamlit 네이티브 멀티페이지(`st.navigation(position="top")`)로 재현했습니다. 목업에 있던 로그인 버튼,
가상의 "소멸위험지수", "일자리 창출 지원금" 같은 항목은 실제 AI 서비스 레이어에 없는 값이라 넣지 않았습니다 —
화면에 보이는 모든 수치는 `src/`가 계산한 실제 값입니다.

---

## 1. 화면 구성 (상단 탭 4개, 클릭 시 실제로 URL이 바뀌며 페이지 전환)

지역(시·군/읍·면·동) 선택은 모든 페이지에 공통으로 뜨는 좌측 사이드바("분석 필터")에서 하며,
선택 상태는 페이지를 이동해도 유지됩니다.

| 탭 | URL | 내용 | 구현 파일 |
|---|---|---|---|
| **지역 선택** (기본 화면) | `/region-select` | 충북 전체 146개 읍·면·동을 AI 예측 순이동률 기준 색상(choropleth)으로 표시하는 개요 지도, 현재 선택 지역 안내 + 다른 3개 탭으로 이동하는 카드형 버튼, 시·군별 예측 요약표 | [views/region_select.py](views/region_select.py) |
| **현황 분석** | `/status` | 선택한 읍·면·동을 강조 표시하는 지도, 인구구조 카드(총인구/청년비율/고령화율/인구증감률), GIS 접근성 카드(의료·응급의료·교육·교통 평균접근거리), 생활권 인프라 상세 데이터(펼치기) | [views/status_overview.py](views/status_overview.py) |
| **AI 예측** | `/ai-prediction` | 다음 해 순이동률 예측값(색상·굵은 글씨 강조), Local SHAP 상위 5개 모델 예측 기여도, "AI 분석 결과 해석" 박스, 지역별 최신 데이터 기준 Global SHAP(펼치기) | [views/ai_prediction.py](views/ai_prediction.py) |
| **시뮬레이션** | `/simulation` | What-if 정책 변수(4종) + 개선율(10/20/30%) 선택, 시나리오별 예측 변화 차트, 기존/조건 변경 후 모델 예측 카드, 시나리오 비교표, "모델 기반 시뮬레이션 분석" 해석 박스 | [views/whatif_simulation.py](views/whatif_simulation.py) |

---

## 2. 전체 파일 구조

새 화면을 추가하거나 기존 화면을 고칠 때 건드릴 파일이 명확히 나뉘어 있습니다.
**화면 하나만 고치고 싶으면 `views/` 안의 해당 파일만 보면 됩니다.**

```text
MVP/
├── app.py                     # 진입점 — 페이지 정의(st.navigation) + 공통 헤더/CSS/사이드바 호출만 담당
├── state.py                     # 세션 상태(선택된 시·군/읍·면·동) 초기화·조회 헬퍼
├── ai_module.py                   # src.* AI 서비스 레이어 어댑터 (모델/데이터 캐싱 + 함수 매핑)
├── run.sh                          # macOS libomp 폴백 실행 스크립트
├── scripts/
│   └── ai_health_check.py           # Streamlit 없이 AI 서비스 레이어 전체 검증
├── icon.jpg                         # 브라우저 탭 파비콘 (app.py의 page_icon)
├── requirements.txt                  # pip 의존성 목록
├── packages.txt                       # Streamlit Cloud(Linux)용 apt 패키지 (libgomp1 — XGBoost용 OpenMP)
├── .gitignore                          # .venv, __pycache__, .DS_Store, secrets.toml 등 제외
│
├── .streamlit/
│   └── config.toml               # 라이트 테마 고정(primaryColor #0055aa 등), 사용통계 수집 끔
│
├── views/                          # 화면(페이지)별 콘텐츠 — 탭 하나 = 파일 하나
│   ├── region_select.py              # "지역 선택" 탭
│   ├── status_overview.py             # "현황 분석" 탭
│   ├── ai_prediction.py                # "AI 예측" 탭
│   └── whatif_simulation.py             # "시뮬레이션" 탭
│
├── components/                    # 여러 화면에서 재사용하는 UI 조각 (수정 시 모든 화면에 반영됨)
│   ├── sidebar.py                    # 좌측 "분석 필터" 패널 (시·군/읍·면·동 선택 + 인구감소지역 배지)
│   ├── metric_card.py                 # 지표 카드(render_metric_card/row), 부호 강조 큰 숫자(render_signed_value)
│   ├── charts.py                       # Plotly 차트 (SHAP 바 차트, What-if 비교 차트) + PLOTLY_CONFIG
│   ├── map_view.py                     # Folium 지도 (단일 지역 강조 지도 / 전체 개요 choropleth 지도)
│   └── insight_box.py                   # "해석"/"AI 분석 결과 해석" 박스 (해시태그 칩 포함)
│
├── assets/
│   └── styles.css                # 전역 CSS 한 곳에 모음 (UI_Ref/*/DESIGN.md 색상 토큰 기반)
│
├── src/                    # 공동 레포 main에서 머지된 AI 서비스 레이어 (그대로 vendored, 직접 수정 X)
│   ├── data_loader.py       # 모델 번들 / 지역 데이터 로딩, build_latest_region_data()
│   ├── region_service.py    # 시군·읍면동 조회, 지역 현황(get_region_summary)
│   ├── inference.py         # AI 예측 (predict_region)
│   ├── service.py           # 지역 현황 + 예측 통합 (get_region_result)
│   ├── shap_service.py      # Global/Local SHAP
│   ├── whatif_service.py    # What-if 시나리오 계산
│   └── scenario_service.py  # 대표 지역 시연용 시나리오
│
├── models/
│   └── final_model.pkl     # 학습된 모델 번들 (model/features/target 딕셔너리)
│
├── data/
│   ├── chungbuk_dong.geojson   # 읍면동 행정경계 (지역코드=adm_cd2로 AI 데이터와 매칭)
│   ├── dong_data.py             # 지도용 GeoJSON 헬퍼 + 인구감소지역 목록(DEPOPULATION_AREAS)
│   └── 충북_최종학습데이터_E세트.csv  # AI 서비스 레이어 학습/조회용 실데이터
│
└── UI_Ref/                # 화면별 디자인 시스템 참고 자료 (실제 코드에는 포함되지 않음)
    ├── main/                            DESIGN.md + code.html + screen.png
    ├── ai예측 및 요인분석/                DESIGN.md + code.html + screen.png
    ├── what-if 정책 시뮬레이션/            DESIGN.md + code.html + screen.png
    └── 지역 현황 상세 분석 리포트/          DESIGN.md + code.html + screen.png
```

### 파일별 상세

**`app.py`**
- `st.Page`로 4개 페이지를 정의하고 `st.navigation(pages, position="top")`으로 상단 탭바를 만든다.
- 페이지 전환은 진짜 Streamlit 멀티페이지 라우팅이라 클릭 시 URL이 바뀌고, `st.page_link`를 쓰면 같은 탭 안에서 이동한다(raw `<a>` HTML은 Streamlit이 보안상 `target="_blank"`를 강제로 붙여 새 탭이 열리므로 쓰지 않는다).
- `page_icon`은 `icon.png`가 있으면 그것을, 없으면 `icon.jpg`를, 둘 다 없으면 Material 아이콘을 파비콘으로 쓴다.
- `assets/styles.css`를 읽어 `<style>` 태그로 주입하고, 상단 헤더 배너 → 사이드바 렌더링 → `pg.run()`(선택된 페이지 실행) → 푸터 순서로 그린다.

**`state.py`**
- `SIGU_KEY`/`DONG_KEY` 세션 상태 키를 정의한다.
- `init_region_state()`: 세션에 값이 없거나 유효하지 않으면 기본값(제천시/첫 읍면동)으로 채운다.
- `get_selected_region()`: 현재 선택된 `{sigu, dong, region_code}`를 반환한다. 모든 `views/*.py`가 이 함수 하나로 선택 상태를 읽는다.

**`ai_module.py`**
- `src/` 함수들을 그대로 호출하는 어댑터. 모델 번들 + 최신 지역 데이터는 `st.cache_resource`로 프로세스당 1회만 로드한다.
- 제공 함수: `get_sigungu_list`, `get_eupmyeondong_list`, `get_region_code`, `get_region_result`, `get_local_shap`, `get_global_shap`, `run_what_if_scenarios`, `summarize_what_if_scenarios`, `run_representative_scenarios`, `get_all_predictions`(전체 146개 지역 일괄 예측 — 지역 선택 페이지의 개요 지도용).
- `get_global_shap()`는 학습 전체 데이터가 아니라 `build_latest_region_data()`로 만든 지역별 최신 데이터 146개 행을 기준으로 Global SHAP 요약을 계산한다. 화면에는 양/음이 상쇄되지 않도록 `mean_abs_shap`을 표시한다.

**`components/sidebar.py`**
- 상단에 "충청지역 전체 보기" 페이지 이동 링크, 시·군/읍·면·동 `selectbox` 2개, 인구감소지역 여부 배지를 렌더링한다.
- 배지에는 `st.caption(..., help=...)`으로 Streamlit 네이티브 툴팁(물음표 아이콘)을 달아, 판정 기준(행정안전부 2021년 10월 지정 충북 6곳)을 hover로 볼 수 있다.

**`components/metric_card.py`**
- `render_metric_card`/`render_metric_row`: 흰 배경 카드에 라벨+값+단위를 표시하는 기본 지표 카드.
- `render_signed_value`: 순이동률처럼 부호가 의미를 갖는 값을 초록(#00C853, 양수)/빨강(#FF5252, 음수)으로 크고 굵게 표시하고, 별도 부호를 갖는 델타 배지(예: 변화량)를 독립적으로 색칠할 수 있다.

**`components/charts.py`**
- `make_shap_chart`: SHAP 값을 수평 막대 차트로 표시(양수=파랑, 음수=빨강, 모서리 둥글게, 격자선 최소화).
- `make_whatif_comparison_chart`: What-if 시나리오 Before/After 막대 차트. `_padded_range()`로 Y축 범위를 데이터 min/max 기준으로 여유 있게 잡아 변화량이 잘려 보이지 않게 한다.
- `PLOTLY_CONFIG = {"displayModeBar": False}`: 모든 `st.plotly_chart` 호출에 공통으로 넘겨서 툴바를 숨긴다. (`st.plotly_chart(..., width="stretch")`처럼 존재하지 않는 키워드를 넘기면 "keyword arguments deprecated" 경고가 뜨므로, 반드시 `use_container_width=True, config=PLOTLY_CONFIG` 형태로 호출한다.)

**`components/map_view.py`**
- `create_region_map`: 선택된 읍·면·동 폴리곤을 빨간색으로 강조하고 마커를 찍는 지도. `fit_bounds`로 읍면동 크기에 맞춰 자동 줌.
- `create_overview_map`: 충북 전체 GeoJSON을 순회하며 `get_all_predictions()` 값 기준으로 파랑(순유입)~빨강(순유출) 그라데이션을 칠하는 choropleth 지도 + 범례.

**`components/insight_box.py`**
- `info_box`: 좌측 파란 보더의 단순 해석 박스.
- `ai_insight_box`: 제목 + 본문 + 해시태그 칩으로 구성된 강조 박스. 태그는 실제 SHAP 피처명/개선율처럼 계산된 값만 넣는다(임의로 지어낸 정책 태그 금지).

**`data/dong_data.py`**
- GeoJSON을 읽어 지역코드(`adm_cd2`) 기준으로 지도 좌표/경계/색상을 계산한다. 예전에는 153개 읍면동 좌표를 손으로 입력한 테이블을 썼는데, 실제 AI 학습데이터의 읍면동 표기와 어긋나는 항목이 있어 GeoJSON에서 직접 파생하는 방식으로 바꿨다.
- `DEPOPULATION_AREAS`: 인구감소지역 6곳(제천시·보은군·옥천군·영동군·괴산군·단양군) 하드코딩 목록 — 행정안전부가 2021년 10월 전국 최초로 지정한 89개 인구감소지역 중 충청북도 해당 지역과 일치한다. AI 예측값과는 무관한 고정 값이라, 이후 행정안전부가 지정 목록을 갱신했다면 반영되어 있지 않을 수 있다.
- `SIGUNGU_TO_SGGNM`: AI 데이터의 "청주시"(통합 표기)를 GeoJSON의 4개 구(상당·서원·흥덕·청원)로 매핑.

**`src/` (vendored AI 서비스 레이어)**
- 공동 레포 `khuda-data/KHUBA_OB_Project`의 `main`에서 머지된 코드를 그대로 가져왔다. 로컬 Python 3.9 호환을 위해 각 파일 맨 위에 `from __future__ import annotations` 한 줄만 추가했고(동작 변경 없음), 그 외 로직은 원본 그대로다.

---

## 3. 데이터 흐름 (요청 1건 기준)

```text
사용자가 사이드바에서 시·군/읍·면·동 선택
        │  (components/sidebar.py → st.session_state)
        ▼
state.get_selected_region()  ──── region_code 확정 (src.region_service.get_region_code)
        │
        ▼
ai_module.py  (캐시된 모델 번들 + 최신 지역 데이터)
        │
        ├─ get_region_result()   → src.service        → 인구/GIS/예측값 + 기준/예측연도
        ├─ get_local_shap()      → src.shap_service    → SHAP 상위 5개 모델 예측 기여도
        ├─ run_what_if_scenarios() → src.whatif_service → 10/20/30% 시나리오
        ├─ summarize_what_if_scenarios() → src.whatif_service → 방향성/단조성 요약
        └─ get_all_predictions() → 146개 지역 일괄 예측 (지역 선택 개요 지도용)
        │
        ▼
views/*.py 가 components/*.py(카드·차트·지도·해석박스)로 화면에 렌더링
```

---

## 4. 실행 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 앱 실행
streamlit run app.py
```

### AI 서비스 health-check

Streamlit 없이 모델/데이터 로딩, 146개 지역 예측, Local SHAP, What-if, 대표 시나리오, 주요 regression 값을 한 번에 검증할 수 있습니다.

```bash
python scripts/ai_health_check.py
```

정상 종료 시 마지막에 `FINAL: PASS`가 출력됩니다.

### 주요 AI 반환 구조

`get_region_result()`의 `prediction`은 다음 정보를 포함합니다.

```python
{
    "target": "타깃_다음해_순이동률",
    "value": -2.1026148796081543,
    "base_year": 2024,
    "prediction_year": 2025,
}
```

- `base_year`: 해당 지역의 최신 데이터 기준연도
- `prediction_year`: `base_year + 1`

`summarize_what_if_scenarios()`는 이미 계산된 10/20/30% What-if 결과를 받아 모델 반응 패턴을 요약합니다.

```python
{
    "direction_consistent": True,
    "monotonic": True,
    "all_positive": True,
    "all_negative": False,
    "best_rate": 0.3,
    "best_change": 0.32829549908638,
    "interpretation": "개선율 증가에 따라 모델 예측값이 일관되게 증가하는 패턴입니다.",
}
```

이 summary는 정책 효과 검증이 아니라 모델 기반 What-if 결과의 방향성과 단조성을 해석하기 위한 보조 정보입니다.

### macOS(Apple Silicon)에서 XGBoost 오류가 날 경우

XGBoost는 실행에 `libomp.dylib`(OpenMP)이 필요합니다. Homebrew가 있다면:

```bash
brew install libomp
```

Homebrew가 없다면, `scikit-learn`을 추가 설치한 뒤 동봉된 `run.sh`로 실행하세요
(scikit-learn 휠에 번들된 libomp 사본 경로를 자동으로 찾아 폴백으로 지정합니다).

```bash
pip install scikit-learn
./run.sh
```

---

## 5. 배포 (Streamlit Community Cloud)

1. https://share.streamlit.io → **New app**
2. Repository: `khuda-data/KHUBA_OB_Project`, Branch: `main`, Main file path: `app.py`
3. **Deploy** 클릭 → `https://xxxx.streamlit.app` 링크 생성

`packages.txt`(`libgomp1`)가 Linux 배포 환경에서 XGBoost가 필요로 하는 OpenMP 라이브러리를 자동으로 설치해 준다.
배포 직후 첫 로딩(모델 로딩 + SHAP 계산 준비)은 로컬보다 조금 걸릴 수 있다.

---

## 6. 자주 하는 수정 작업별 안내

| 하고 싶은 일 | 고칠 파일 |
|---|---|
| 카드에 새 지표 추가 | 해당 `views/*.py`에서 `render_metric_row([...])` 항목 추가 |
| 새 탭(페이지) 추가 | `views/`에 파일 추가 → `app.py`의 `pages` 리스트에 `st.Page(...)` 한 줄 추가 |
| 사이드바 필터 항목 추가 | `components/sidebar.py` |
| 색상/폰트/여백 등 디자인 변경 | `assets/styles.css` |
| AI 서비스 레이어 함수 새로 연동 | `ai_module.py`에 어댑터 함수 추가 (`src/` 원본은 건드리지 않음) |
| 배지/버튼에 hover 설명 추가 | 위젯의 `help=` 파라미터 사용 (`st.caption`, `st.button` 등이 지원 — native title 속성보다 안정적으로 표시됨) |

---

## 7. 용어 설명

- **순이동률**: 특정 지역에서 전입자 수와 전출자 수의 차이를 인구 대비 비율로 나타낸 지표. 양수(+)면 순유입(인구 증가 방향), 음수(-)면 순유출(인구 감소 방향)을 의미한다. 앱 안에서는 "AI 예측", "시뮬레이션", "지역 선택" 탭의 설명 문구 옆 물음표 아이콘에 이 설명이 달려 있다.
- **SHAP**: 모델 예측에 대한 변수별 기여도를 나타내는 지표. **원인이 아니다** — "모델 예측 기여도"로만 해석한다.
- **What-if**: 특정 입력 변수를 바꿨을 때 같은 학습 모델의 예측값이 어떻게 달라지는지 확인하는 **모델 기반 민감도 분석**. 실제 정책 시행의 인과효과를 보장하지 않는다.
- **인구감소지역**: 행정안전부가 지정한 목록 기준(코드 상 고정값). 자세한 기준은 위 "전체 파일 구조" 섹션의 `data/dong_data.py` 설명 참고.

## 8. 기술 스택

- Python, Streamlit, Folium, Plotly, Pandas, NumPy
- XGBoost, SHAP, joblib (AI 서비스 레이어)

## 9. 팀

KHUDA OB 심화 프로젝트

## 10. 주의사항

- `ai_module.py`는 AI 서비스 레이어(`src/`)를 그대로 호출하는 얇은 어댑터이며, Stub이 아니다.
- `src/`는 공동 레포에서 머지된 코드를 그대로 vendoring한 것이며, 로컬 Python 3.9 호환을 위해
  각 파일 맨 위에 `from __future__ import annotations` 한 줄만 추가했다(동작 변경 없음).
- 지도 표시 지역코드(GeoJSON `adm_cd2`)와 AI 데이터의 `지역코드`는 1:1로 매칭된다(146/153개 읍면동에 AI 데이터 존재).
- 모든 What-if 해석 문구는 **인과관계를 직접 단정하지 않는다** ("모델 기반 민감도 분석"으로 표현).
- SHAP은 **"모델 예측 기여도"**로 표현하며, 원인으로 해석하지 않는다.
- `UI_Ref/`는 디자인 참고용 목업 자료일 뿐, 앱 실행에는 필요하지 않다.

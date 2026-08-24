
```markdown
# 충북 지역소멸 대응 AI 시뮬레이터 (MVP)

> ** 충청북도 읍·면·동 단위 지역소멸 대응을 위한 AI 기반 정책 시뮬레이션 웹 애플리케이션**  
> 본 프로젝트는 공동 레포지토리 [KHUBA_OB_Project](https://github.com/khuda-data/KHUBA_OB_Project) `main` 브랜치의 AI 서비스 레이어(`src/`)를 연동하여 동작합니다.

---

## 주요 기능 (Key Features)

1. ** 지능형 지역 선택 (Interactive Map) **
   - 충북 시·군 및 읍·면·동 단위 선택 (Folium 기반 지도 시각화)
   - 지도 행정경계(`adm_cd2`)와 AI 최신 데이터의 1:1 매칭 (146/153개 읍면동 커버)
2. ** 지역 현황 대시보드 (Overview) **
   - 인구구조, GIS 접근성, 생활권 인프라 실데이터 통합 조회
3. ** AI 순이동률 예측 (AI Prediction) **
   - XGBoost 모델(`final_model.pkl`) 기반 다음 해 순이동률 AI 예측
4. ** SHAP 요인 분석 (Explainable AI) **
   - Global / Local SHAP 기반 모델 예측 기여도(Feature Importance) 제공
5. ** What-if 정책 시뮬레이션 (Simulation) **
   - 주요 정책 변수(10/20/30% 개선) 변동에 따른 모델 기반 민감도 분석

---

## 기술 스택 (Tech Stack)

| 구분 | 기술 / 라이브러리 |
| :--- | :--- |
| **Frontend / Dashboard** | Streamlit, Folium, Plotly |
| **Data & Analytics** | Pandas, NumPy |
| **AI / Machine Learning** | XGBoost, SHAP, Scikit-learn, Joblib |

---

## 실행 방법 (Getting Started)

### 1. 기본 실행

```bash
# 1) 필요한 패키지 설치
pip install -r requirements.txt

# 2) Streamlit 앱 실행
streamlit run app.py

```

### 2. macOS (Apple Silicon) 문제 해결

XGBoost 실행 시 `libomp.dylib` 오류가 발생할 경우 아래 안내를 참고하세요.

* **Homebrew가 있는 경우:**
```bash
brew install libomp

```


* **Homebrew가 없는 경우:**
```bash
pip install scikit-learn
./run.sh

```


*(동봉된 `run.sh`가 scikit-learn 휠 내부의 OpenMP 경로를 자동으로 잡아 폴백 실행합니다.)*

---

## 📂 프로젝트 구조 (Directory Structure)

```text
KHUBA_OB_Project/
├── app.py                # Streamlit 메인 실행 파일 (상태 관리, 레이아웃 메인 UI)
├── ai_module.py           # src.* AI 서비스 레이어 캐싱 및 매핑 어댑터
├── run.sh                  # macOS libomp 이슈 대응 실행 스크립트
├── requirements.txt
│
├── components/            # UI 공통 컴포넌트 (지도, 차트, 지표 카드, 사이드바 등)
├── views/                 # 화면 탭별 View 모듈 (지역 선택, 예측, SHAP, What-if 등)
│
├── src/                   # AI 서비스 레이어 (Vendored Core Logic)
│   ├── data_loader.py    # 모델 번들 및 지역 데이터 로더
│   ├── region_service.py # 시군·읍면동 조회 및 지역 현황 요약
│   ├── inference.py      # AI 예측 추론 Engine
│   ├── service.py        # 지역 현황 + 예측 결과 통합 레이어
│   ├── shap_service.py   # Global / Local SHAP 분석 서비스
│   ├── whatif_service.py # What-if 정책 시뮬레이션 계산
│   └── scenario_service.py # 시연용 대표 시나리오
│
├── models/
│   └── final_model.pkl   # 학습된 AI 모델 번들 (Model/Features/Target)
│
└── data/
    ├── chungbuk_dong.geojson  # 읍면동 행정경계 GIS 데이터
    ├── dong_data.py            # GeoJSON 좌표/경계 헬퍼
    └── 충북_최종학습데이터_E세트.csv # AI 학습 및 조회용 실데이터

```

---

## 안내 및 주의사항 (Notice)

* **AI 서비스 연동:** `ai_module.py`는 `src/` 레이어를 원본 그대로 호출하는 어댑터 역할을 수행합니다.
* **Python 버전 호환:** `src/` 내부 코드는 Python 3.9 호환성을 위해 `from __future__ import annotations`가 포함되어 있습니다.
* **결과 해석 유의사항:**
* **What-if 시뮬레이션:** 인과관계를 단정하지 않으며, **"모델 기반 민감도 분석"** 수치로 제공됩니다.
* **SHAP 분석:** 원인 분석이 아닌 "모델 예측에 대한 변수별 기여도"로 해석합니다.




```

```

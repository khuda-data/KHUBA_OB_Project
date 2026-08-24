#!/usr/bin/env bash
# macOS(Apple Silicon)에서 XGBoost가 필요로 하는 libomp.dylib을
# Homebrew(`brew install libomp`) 없이도 찾을 수 있도록,
# scikit-learn 패키지에 번들된 libomp 사본의 경로를 폴백으로 지정한 뒤 앱을 실행합니다.
# Homebrew로 libomp를 설치했다면 이 스크립트 없이 `streamlit run app.py`만으로도 동작합니다.
set -e
cd "$(dirname "$0")"

SKLEARN_DYLIBS="$(./.venv/bin/python -c 'import sklearn, pathlib; print(pathlib.Path(sklearn.__file__).parent / ".dylibs")' 2>/dev/null || true)"
# DYLD_FALLBACK_LIBRARY_PATH를 지정하면 macOS 기본 폴백 경로($HOME/lib:/usr/local/lib:/lib:/usr/lib)가
# 사라지므로, numba/llvmlite 등이 찾는 시스템 라이브러리(libz 등)를 위해 기본 경로를 함께 붙여줍니다.
DEFAULT_FALLBACK="$HOME/lib:/usr/local/lib:/lib:/usr/lib"
if [ -n "$SKLEARN_DYLIBS" ] && [ -d "$SKLEARN_DYLIBS" ]; then
    export DYLD_FALLBACK_LIBRARY_PATH="$SKLEARN_DYLIBS:$DEFAULT_FALLBACK"
else
    export DYLD_FALLBACK_LIBRARY_PATH="$DEFAULT_FALLBACK"
fi

exec ./.venv/bin/streamlit run app.py

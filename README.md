# DebugMate RAG

DebugMate RAG는 AI 학습자가 실제로 겪은 오류 기록을 기반으로, RAG 검색과 source citation을 통해 개인화된 오류 해결 답변을 제공하는 DLthon용 MVP입니다.

일반 GPT에게 오류를 질문하는 방식이 아니라, 사용자가 직접 겪은 Python, RunPod, Jupyter, Git, LangChain, RAGAS 관련 오류 기록을 검색 기반으로 참고하여 답변합니다.

---

## 1. 프로젝트 개요

AI 학습 과정에서는 설치 오류, 환경 충돌, API 설정 문제, 라이브러리 import 오류, 실행 명령어 혼동 등이 반복적으로 발생합니다.

DebugMate RAG는 이러한 오류 기록을 데이터셋으로 저장하고, 사용자의 질문이 들어오면 관련 오류 기록을 검색한 뒤, 해당 source를 기반으로 해결 방향을 제시합니다.

이 프로젝트의 핵심 목표는 다음과 같습니다.

* 실제 학습자가 겪은 오류 기록 기반 답변
* RAG 검색을 통한 개인화된 디버깅 지원
* source citation을 통한 근거 있는 답변 제공
* Streamlit 기반 간단한 데모 UI 제공
* RAGAS를 활용한 RAG 품질 평가

---

## 2. 핵심 차별점

기존 GPT 사용 방식은 일반적인 지식 기반 답변에 가깝습니다.

DebugMate RAG는 다음과 같은 점에서 차별화됩니다.

1. 사용자가 실제로 겪은 오류 기록을 데이터로 사용합니다.
2. 프로젝트 환경, 실행 명령어, 과거 오류 맥락을 반영합니다.
3. 답변과 함께 참고한 source 문서를 출력합니다.
4. RAGAS 평가를 통해 검색 및 답변 품질을 정량적으로 확인합니다.

즉, DebugMate RAG는 범용 챗봇이 아니라 AI 학습자를 위한 개인화된 오류 해결 보조 도구입니다.

---

## 3. 주요 기능

* 오류 기록 데이터셋 로드
* 질문 유형 자동 분류
* metadata filter 적용
* Chroma vector search
* OpenAIEmbeddings 기반 임베딩 생성
* ChatOpenAI 기반 답변 생성
* 검색된 source 문서 출력
* Streamlit UI 제공
* RAGAS 기반 평가 결과 생성

---

## 4. 프로젝트 구조

```text
debugmate-rag/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .vscode/
│   └── settings.json
├── data/
│   ├── .gitkeep
│   ├── error_logs.txt
│   ├── runpod_notes.txt
│   ├── git_errors.txt
│   ├── jupyter_env_errors.txt
│   └── ragas_langchain_errors.txt
├── src/
│   ├── loader.py
│   ├── router.py
│   ├── retriever.py
│   ├── answer.py
│   └── evaluation.py
├── results/
│   ├── .gitkeep
│   └── debugmate_ragas_results.csv
├── notebooks/
│   └── .gitkeep
├── tests/
│   └── .gitkeep
├── vectorstore/
│   └── .gitkeep
└── assets/
    ├── streamlit_full_page.png
    └── ragas_results.png
```

---

## 5. 기술 스택

* Python 3.11.9
* Streamlit
* LangChain
* Chroma
* OpenAIEmbeddings
* ChatOpenAI
* RAGAS
* pandas
* python-dotenv

---

## 6. 실행 방법

### 6.1 프로젝트 폴더 이동

```powershell
cd C:\AI_study\debugmate-rag
```

### 6.2 가상환경 활성화

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& C:\AI_study\debugmate-rag\.venv\Scripts\Activate.ps1)
```

### 6.3 패키지 설치

```powershell
pip install -r requirements.txt
```

### 6.4 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API Key를 입력합니다.

```env
OPENAI_API_KEY=your_openai_api_key
```

`.env` 파일은 `.gitignore`에 의해 GitHub에 업로드되지 않습니다.

---

## 7. Streamlit 앱 실행

반드시 아래 명령어로 실행합니다.

```powershell
python -m streamlit run app.py
```

주의할 점:

```powershell
streamlit run app.py
```

위 명령어를 사용하면 전역 Python 3.12 환경의 Streamlit이 실행될 수 있습니다.
이 프로젝트는 Python 3.11.9 가상환경 기준으로 구성되어 있으므로 반드시 `python -m streamlit run app.py` 명령어를 사용해야 합니다.

---

## 8. 데모 화면

### Streamlit Demo

![Streamlit Demo](assets/streamlit_full_page.png)

---

## 9. RAGAS 평가 결과

RAGAS를 사용하여 DebugMate RAG의 검색 및 답변 품질을 평가했습니다.

![RAGAS Results](assets/ragas_results.png)

평가 결과, 검색 관련 지표인 context_precision과 context_recall은 높게 측정되었습니다.
이는 질문에 대해 관련 source 문서를 비교적 잘 검색하고 있음을 의미합니다.

다만 일부 질문에서는 answer_relevancy와 faithfulness가 낮게 측정되었습니다.
이는 현재 구조가 rule-based router와 기본 프롬프트에 의존하고 있기 때문입니다.

향후에는 LLM Router, Hybrid Search, Reranker, 프롬프트 개선 등을 통해 답변 품질과 근거 충실도를 보완할 수 있습니다.

---

## 10. 현재 한계

현재 MVP에는 다음과 같은 한계가 있습니다.

1. 질문 유형 분류가 rule-based router에 의존합니다.
2. 검색 방식이 기본 vector search 중심입니다.
3. 답변 품질이 프롬프트 구성에 영향을 크게 받습니다.
4. 데이터셋 규모가 아직 작습니다.
5. 일부 질문에서는 검색 문서와 답변 간의 faithfulness가 낮게 나올 수 있습니다.

---

## 11. 개선 방향

향후 개선 방향은 다음과 같습니다.

* LLM Router 적용
* Hybrid Search 적용
* Reranker 적용
* 오류 유형별 프롬프트 분리
* 더 많은 실제 오류 로그 추가
* Streamlit UI 개선
* RAGAS 평가셋 확장
* 사용자별 오류 히스토리 관리 기능 추가

---

## 12. 기대 효과

DebugMate RAG는 AI 학습자가 반복적으로 겪는 오류를 개인화된 방식으로 해결할 수 있도록 돕습니다.

특히 초보 학습자는 같은 오류를 반복해서 검색하거나, 과거 해결 방법을 잊어버리는 경우가 많습니다.
DebugMate RAG는 이러한 오류 경험을 데이터로 축적하고, 이후 비슷한 문제가 발생했을 때 빠르게 검색하여 해결 방향을 제공합니다.

이를 통해 단순한 오류 해결을 넘어, 개인 학습 기록을 활용한 AI 학습 보조 시스템으로 확장할 수 있습니다.

---

## 13. GitHub 제출 전 확인 사항

제출 전 아래 항목을 확인합니다.

```powershell
git status
```

확인할 항목:

* `.env` 파일이 Git에 포함되지 않았는지 확인
* `README.md`가 최신 내용인지 확인
* `assets/streamlit_full_page.png` 파일이 존재하는지 확인
* `assets/ragas_results.png` 파일이 존재하는지 확인
* `results/debugmate_ragas_results.csv` 파일이 존재하는지 확인
* 불필요한 캐시 파일이 포함되지 않았는지 확인

커밋 및 푸시 예시:

```powershell
git add .
git commit -m "Finalize DebugMate RAG README and demo assets"
git push origin main
```

---

## 14. 프로젝트 요약

DebugMate RAG는 AI 학습자가 실제로 겪은 오류 기록을 기반으로, RAG 검색과 source citation을 통해 개인화된 오류 해결 답변을 제공하는 DLthon용 MVP입니다.

이 프로젝트는 단순한 챗봇이 아니라, 학습자의 오류 경험을 데이터화하고 다시 활용하는 개인화된 디버깅 보조 시스템을 목표로 합니다.

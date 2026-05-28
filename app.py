import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

load_dotenv(PROJECT_ROOT / ".env")

from loader import load_debugmate_documents
from retriever import build_vectorstore, search_documents
from answer import generate_answer


st.set_page_config(
    page_title="DebugMate RAG",
    page_icon="🛠️",
    layout="wide",
)


def get_vectorstore():
    docs = load_debugmate_documents(data_dir=str(PROJECT_ROOT / "data"))

    vectorstore = build_vectorstore(
        docs=docs,
        chunk_size=1000,
        chunk_overlap=100,
        persist_directory=None,
    )

    return vectorstore


def main():
    st.title("DebugMate RAG")
    st.caption("AI 학습자를 위한 오류 해결 RAG Assistant")

    api_key_exists = os.environ.get("OPENAI_API_KEY") is not None

    if not api_key_exists:
        st.error(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. "
            "프로젝트 루트의 .env 파일을 확인하세요."
        )
        st.stop()

    with st.sidebar:
        st.header("설정")

        k = st.slider(
            "검색할 문서 chunk 개수",
            min_value=1,
            max_value=8,
            value=3,
            step=1,
        )

        use_router = st.checkbox(
            "질문 유형 자동 분류 사용",
            value=True,
        )

        st.markdown("---")
        st.markdown("### 예시 질문")

        examples = [
            "ModuleNotFoundError: No module named 'datasets' 오류는 어떻게 해결하나요?",
            "OpenAI API 키 오류가 났을 때 어떻게 해야 하나요?",
            "git push rejected 오류는 어떻게 해결하나요?",
            "RunPod에서 Network Volume은 언제 써야 하나요?",
            "Chroma 설치할 때 chroma-hnswlib 빌드 실패가 납니다.",
            "Jupyter 커널이 패키지를 못 찾습니다.",
        ]

        selected_example = st.selectbox(
            "예시 선택",
            ["직접 입력"] + examples,
        )

    if selected_example == "직접 입력":
        default_query = ""
    else:
        default_query = selected_example

    query = st.text_area(
        "오류 메시지 또는 질문을 입력하세요",
        value=default_query,
        height=140,
        placeholder="예: ModuleNotFoundError: No module named 'datasets'",
    )

    run_button = st.button("해결 방법 찾기", type="primary")

    if run_button:
        if not query.strip():
            st.warning("질문 또는 오류 메시지를 입력하세요.")
            st.stop()

        with st.spinner("문서를 로드하고 Chroma 검색기를 준비하는 중입니다..."):
            vectorstore = get_vectorstore()

        with st.spinner("관련 오류 문서를 검색하는 중입니다..."):
            search_result = search_documents(
                query=query,
                vectorstore=vectorstore,
                k=k,
                use_router=use_router,
            )

        with st.spinner("답변을 생성하는 중입니다..."):
            answer_result = generate_answer(
                query=query,
                search_result=search_result,
            )

        st.markdown("## 답변")
        st.write(answer_result["answer"])

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("선택 route", answer_result["route"])

        with col2:
            st.metric("검색 문서 수", len(answer_result["retrieved_documents"]))

        with col3:
            if answer_result["metadata_filter"]:
                st.metric("metadata filter", str(answer_result["metadata_filter"]))
            else:
                st.metric("metadata filter", "전체 검색")

        st.markdown("### 참고 source")

        for source in answer_result["sources"]:
            st.write(f"- {source}")

        with st.expander("검색된 문서 context 보기"):
            for i, doc in enumerate(answer_result["retrieved_documents"], 1):
                st.markdown(f"#### 검색 결과 {i}")
                st.json(doc.metadata)
                st.write(doc.page_content[:1500])


if __name__ == "__main__":
    main()
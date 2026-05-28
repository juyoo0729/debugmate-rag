from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from loader import load_debugmate_documents
from retriever import build_vectorstore, search_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def format_context(documents: List[Document]) -> str:
    """
    검색된 문서를 LLM에게 넘길 context 문자열로 변환한다.
    """

    context_blocks = []

    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "unknown")
        doc_type = doc.metadata.get("doc_type", "unknown")
        topic = doc.metadata.get("topic", "unknown")

        block = f"""
[문서 {i}]
source: {source}
doc_type: {doc_type}
topic: {topic}

{doc.page_content}
"""
        context_blocks.append(block.strip())

    return "\n\n---\n\n".join(context_blocks)


def generate_answer(
    query: str,
    search_result: Dict[str, Any],
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    검색 결과를 바탕으로 오류 해결 답변을 생성한다.
    """

    retrieved_docs = search_result["documents"]

    if not retrieved_docs:
        return {
            "query": query,
            "route": search_result["route"],
            "route_description": search_result["route_description"],
            "metadata_filter": search_result["metadata_filter"],
            "answer": (
                "관련 문서를 찾지 못했습니다. 질문을 조금 더 구체적으로 입력하거나 "
                "질문 유형 자동 분류를 끄고 다시 검색해 보세요."
            ),
            "sources": [],
            "retrieved_documents": [],
        }

    context = format_context(retrieved_docs)

    llm = ChatOpenAI(
        model=model,
        temperature=0,
    )

    prompt = f"""
너는 AI 학습자를 돕는 오류 해결 RAG assistant다.

반드시 아래 [검색된 문서]를 근거로 답변해라.
문서에 없는 내용은 추측하지 말고, "문서에서 확인되지 않습니다."라고 말해라.

답변 형식은 반드시 다음 구조를 따른다.

원인:
- 오류가 발생한 핵심 원인을 설명한다.

해결 방법:
1. 사용자가 바로 따라 할 수 있는 순서로 설명한다.
2. 필요한 명령어가 있으면 포함한다.

주의사항:
- 실수하기 쉬운 점을 설명한다.

참고 문서:
- 사용한 source 파일명을 적는다.

[질문]
{query}

[선택된 route]
{search_result["route"]}

[route 설명]
{search_result["route_description"]}

[검색된 문서]
{context}

[답변]
"""

    response = llm.invoke(prompt)

    sources = []
    for doc in retrieved_docs:
        source = doc.metadata.get("source", "unknown")
        if source not in sources:
            sources.append(source)

    return {
        "query": query,
        "route": search_result["route"],
        "route_description": search_result["route_description"],
        "metadata_filter": search_result["metadata_filter"],
        "answer": response.content,
        "sources": sources,
        "retrieved_documents": retrieved_docs,
    }


def print_answer(result: Dict[str, Any]) -> None:
    """
    답변 결과를 보기 좋게 출력한다.
    """

    print("=" * 80)
    print("질문:", result["query"])
    print("route:", result["route"])
    print("route 설명:", result["route_description"])
    print("metadata filter:", result["metadata_filter"])

    print("\n답변:")
    print(result["answer"])

    print("\n참고 source:")
    for source in result["sources"]:
        print("-", source)


if __name__ == "__main__":
    docs = load_debugmate_documents(data_dir="data")

    vectorstore = build_vectorstore(
        docs=docs,
        chunk_size=1000,
        chunk_overlap=100,
        persist_directory=None,
    )

    test_queries = [
        "ModuleNotFoundError: No module named 'datasets' 오류는 어떻게 해결하나요?",
        "OpenAI API 키 오류가 났을 때 어떻게 해야 하나요?",
        "git push rejected 오류는 어떻게 해결하나요?",
        "RunPod에서 Network Volume은 언제 써야 하나요?",
        "Chroma 설치할 때 chroma-hnswlib 빌드 실패가 납니다.",
    ]

    for query in test_queries:
        search_result = search_documents(
            query=query,
            vectorstore=vectorstore,
            k=3,
            use_router=True,
        )

        answer_result = generate_answer(
            query=query,
            search_result=search_result,
        )

        print_answer(answer_result)

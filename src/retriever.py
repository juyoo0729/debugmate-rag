import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from loader import load_debugmate_documents
from router import route_query, get_route_filter, describe_route


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def split_documents(
    docs: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> List[Document]:
    """
    문서를 chunk 단위로 분할한다.
    metadata는 chunk에도 유지된다.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    splits = splitter.split_documents(docs)
    return splits


def build_vectorstore(
    docs: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    persist_directory: Optional[str] = None,
) -> Chroma:
    """
    Chroma vectorstore를 생성한다.

    persist_directory가 None이면 메모리 Chroma로 동작한다.
    persist_directory를 지정하면 디스크 저장형 Chroma로 동작한다.
    """

    splits = split_documents(
        docs=docs,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    embeddings = OpenAIEmbeddings()

    if persist_directory:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
    else:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
        )

    return vectorstore


def search_documents(
    query: str,
    vectorstore: Chroma,
    k: int = 4,
    use_router: bool = True,
) -> Dict[str, Any]:
    """
    사용자 질문을 검색한다.

    use_router=True이면 질문 유형을 분류하고,
    route에 맞는 metadata filter를 적용한다.
    """

    route = route_query(query) if use_router else "general"
    metadata_filter = get_route_filter(route) if use_router else None

    search_kwargs: Dict[str, Any] = {"k": k}

    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    retriever = vectorstore.as_retriever(
        search_kwargs=search_kwargs
    )

    retrieved_docs = retriever.invoke(query)

    return {
        "query": query,
        "route": route,
        "route_description": describe_route(route),
        "metadata_filter": metadata_filter,
        "documents": retrieved_docs,
    }


def print_search_results(search_result: Dict[str, Any]) -> None:
    """
    검색 결과를 보기 좋게 출력한다.
    """

    print("=" * 80)
    print("질문:", search_result["query"])
    print("선택 route:", search_result["route"])
    print("route 설명:", search_result["route_description"])
    print("metadata filter:", search_result["metadata_filter"])
    print("검색 결과 수:", len(search_result["documents"]))

    for i, doc in enumerate(search_result["documents"], 1):
        print("-" * 80)
        print(f"[검색 결과 {i}]")
        print("metadata:", doc.metadata)
        print(doc.page_content[:800])


if __name__ == "__main__":
    docs = load_debugmate_documents(data_dir="data")

    print(f"로드된 원본 문서 수: {len(docs)}")

    vectorstore = build_vectorstore(
        docs=docs,
        chunk_size=1000,
        chunk_overlap=100,
        persist_directory=None,
    )

    test_queries = [
        "datasets 모듈이 없다고 나와요",
        "RunPod에서 Network Volume은 언제 써야 하나요?",
        "git push rejected 오류는 어떻게 해결하나요?",
        "Jupyter 커널이 패키지를 못 찾습니다",
        "RAGAS 평가에서 answer_relevancy가 이상하게 나옵니다",
        "Chroma 설치가 안 됩니다",
    ]

    for query in test_queries:
        result = search_documents(
            query=query,
            vectorstore=vectorstore,
            k=3,
            use_router=True,
        )
        print_search_results(result)
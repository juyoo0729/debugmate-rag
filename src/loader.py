from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


DATA_CONFIGS: List[Dict[str, str]] = [
    {
        "filename": "error_logs.txt",
        "doc_type": "error_log",
        "topic": "general_error",
        "description": "일반 Python, 패키지, API 키, 가상환경 오류 기록",
    },
    {
        "filename": "runpod_notes.txt",
        "doc_type": "infra_note",
        "topic": "runpod",
        "description": "RunPod, GPU, 저장공간, Network Volume 관련 노트",
    },
    {
        "filename": "git_errors.txt",
        "doc_type": "git_note",
        "topic": "git",
        "description": "Git, GitHub, commit, push, branch 관련 오류 기록",
    },
    {
        "filename": "jupyter_env_errors.txt",
        "doc_type": "env_note",
        "topic": "jupyter_env",
        "description": "Jupyter, VS Code, Python interpreter, 가상환경 오류 기록",
    },
    {
        "filename": "ragas_langchain_errors.txt",
        "doc_type": "rag_note",
        "topic": "ragas_langchain",
        "description": "RAGAS, LangChain, Chroma, OpenAIEmbeddings 관련 오류 기록",
    },
]


def load_debugmate_documents(data_dir: str = "data") -> List[Document]:
    """
    data 폴더의 txt 문서를 LangChain Document로 로드하고 metadata를 부여한다.
    """

    base_dir = Path(data_dir)
    docs: List[Document] = []

    if not base_dir.exists():
        raise FileNotFoundError(f"data 폴더를 찾을 수 없습니다: {base_dir.resolve()}")

    for config in DATA_CONFIGS:
        file_path = base_dir / config["filename"]

        if not file_path.exists():
            print(f"[경고] 파일 없음: {file_path}")
            continue

        loader = TextLoader(str(file_path), encoding="utf-8")
        loaded_docs = loader.load()

        for doc in loaded_docs:
            doc.metadata.update(
                {
                    "source": config["filename"],
                    "doc_type": config["doc_type"],
                    "topic": config["topic"],
                    "description": config["description"],
                }
            )
            docs.append(doc)

    if not docs:
        raise ValueError("로드된 문서가 없습니다. data 폴더의 txt 파일을 확인하세요.")

    return docs


if __name__ == "__main__":
    documents = load_debugmate_documents()
    print(f"로드된 문서 수: {len(documents)}")

    for doc in documents:
        print("-" * 80)
        print(doc.metadata)
        print("문자 수:", len(doc.page_content))
        print("앞부분:", doc.page_content[:200])
        print("끝부분:", doc.page_content[-200:])
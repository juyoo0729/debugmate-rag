from typing import Dict


ROUTE_CONFIGS: Dict[str, Dict[str, str]] = {
    "general_error": {
        "filter_key": "topic",
        "filter_value": "general_error",
        "description": "일반 Python, 패키지, API 키, 가상환경 오류",
    },
    "runpod": {
        "filter_key": "topic",
        "filter_value": "runpod",
        "description": "RunPod, GPU, 저장공간, Network Volume 관련 질문",
    },
    "git": {
        "filter_key": "topic",
        "filter_value": "git",
        "description": "Git, GitHub, commit, push, branch 관련 질문",
    },
    "jupyter_env": {
        "filter_key": "topic",
        "filter_value": "jupyter_env",
        "description": "Jupyter, VS Code, Python interpreter, 가상환경 관련 질문",
    },
    "ragas_langchain": {
        "filter_key": "topic",
        "filter_value": "ragas_langchain",
        "description": "RAGAS, LangChain, Chroma, OpenAIEmbeddings 관련 질문",
    },
    "general": {
        "filter_key": "",
        "filter_value": "",
        "description": "전체 문서 검색",
    },
}


def route_query(query: str) -> str:
    """
    사용자 질문을 보고 검색할 문서군 route를 결정한다.
    초기 MVP에서는 rule-based keyword router를 사용한다.
    """

    q = query.lower()

    git_keywords = [
        "git",
        "github",
        "push",
        "pull",
        "commit",
        "branch",
        "main",
        "master",
        "origin",
        "remote",
        "rejected",
        "fetch first",
        "gitignore",
        "깃",
        "깃허브",
        "커밋",
        "푸시",
        "브랜치",
    ]

    runpod_keywords = [
        "runpod",
        "런포드",
        "pod",
        "gpu",
        "network volume",
        "네트워크 볼륨",
        "volume",
        "workspace",
        "저장공간",
        "서버",
        "vram",
    ]

    jupyter_keywords = [
        "jupyter",
        "notebook",
        "kernel",
        "ipykernel",
        "vscode",
        "interpreter",
        "activate",
        "venv",
        ".venv",
        "python --version",
        "sys.executable",
        "주피터",
        "노트북",
        "커널",
        "가상환경",
        "인터프리터",
        "파워셀",
        "powershell",
    ]

    ragas_langchain_keywords = [
        "ragas",
        "langchain",
        "chroma",
        "chromadb",
        "chroma-hnswlib",
        "openaiembeddings",
        "chatopenai",
        "textloader",
        "splitter",
        "retriever",
        "chunk",
        "chunk_size",
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
        "래그",
        "청크",
        "임베딩",
        "벡터",
    ]

    general_error_keywords = [
        "modulenotfounderror",
        "no module named",
        "openaierror",
        "api_key",
        "openai_api_key",
        "permissionerror",
        "syntaxerror",
        "importerror",
        "nameerror",
        "오류",
        "에러",
        "설치",
        "안됨",
        "안 돼",
        "실패",
        "모듈",
        "패키지",
        "api 키",
    ]

    if any(keyword in q for keyword in git_keywords):
        return "git"

    if any(keyword in q for keyword in runpod_keywords):
        return "runpod"

    if any(keyword in q for keyword in jupyter_keywords):
        return "jupyter_env"

    if any(keyword in q for keyword in ragas_langchain_keywords):
        return "ragas_langchain"

    if any(keyword in q for keyword in general_error_keywords):
        return "general_error"

    return "general"


def get_route_filter(route: str) -> Dict[str, str] | None:
    """
    route에 맞는 Chroma metadata filter를 반환한다.
    general route는 전체 검색이므로 None을 반환한다.
    """

    config = ROUTE_CONFIGS.get(route, ROUTE_CONFIGS["general"])

    if config == ROUTE_CONFIGS["general"]:
        return None

    return {
        config["filter_key"]: config["filter_value"]
    }


def describe_route(route: str) -> str:
    """
    route 설명을 반환한다.
    """

    return ROUTE_CONFIGS.get(route, ROUTE_CONFIGS["general"])["description"]


if __name__ == "__main__":
    test_queries = [
        "datasets 모듈이 없다고 나와요",
        "RunPod에서 Network Volume은 언제 써야 하나요?",
        "git push rejected 오류가 나요",
        "Jupyter 커널이 패키지를 못 찾습니다",
        "RAGAS 평가에서 answer_relevancy가 이상해요",
        "이 오류는 왜 나는 건가요?",
    ]

    for query in test_queries:
        route = route_query(query)
        print("=" * 80)
        print("질문:", query)
        print("route:", route)
        print("filter:", get_route_filter(route))
        print("설명:", describe_route(route))

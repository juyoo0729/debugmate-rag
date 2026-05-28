from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from loader import load_debugmate_documents
from retriever import build_vectorstore, search_documents
from answer import generate_answer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


EVAL_QUESTIONS = [
    {
        "question": "ModuleNotFoundError: No module named 'datasets' 오류는 어떻게 해결하나요?",
        "ground_truth": "현재 Python 또는 Jupyter 커널 환경에 datasets 패키지가 설치되어 있지 않기 때문에 발생하며, 현재 커널의 Python 경로를 확인한 뒤 python -m pip install datasets 또는 requirements.txt 설치를 실행해야 한다.",
    },
    {
        "question": "OpenAI API 키 오류가 났을 때 어떻게 해야 하나요?",
        "ground_truth": "프로젝트 루트에 .env 파일을 만들고 OPENAI_API_KEY를 설정한 뒤, python-dotenv의 load_dotenv로 해당 파일을 로드해야 한다. API 키는 GitHub에 올리면 안 된다.",
    },
    {
        "question": "git push rejected 오류는 왜 발생하나요?",
        "ground_truth": "원격 저장소에 로컬에는 없는 commit이 있어서 발생한다. git pull origin main --allow-unrelated-histories로 원격 변경사항을 가져온 뒤 충돌을 해결하고 다시 push해야 한다.",
    },
    {
        "question": "RunPod에서 Network Volume은 언제 필요한가요?",
        "ground_truth": "대용량 모델, 데이터셋, 학습 체크포인트를 Pod와 독립적으로 장기간 보관해야 할 때 필요하다. 초기 RAG 실습에서는 GitHub와 로컬 백업으로 충분할 수 있다.",
    },
    {
        "question": "Chroma 설치 중 chroma-hnswlib 빌드 실패가 발생하면 어떻게 하나요?",
        "ground_truth": "Windows와 Python 3.12 조합에서 chroma-hnswlib 빌드가 실패할 수 있다. Python 3.11 가상환경을 사용하거나 Microsoft C++ Build Tools를 설치하는 방식으로 해결할 수 있다.",
    },
]


def run_debugmate_evaluation() -> pd.DataFrame:
    docs = load_debugmate_documents(data_dir=str(PROJECT_ROOT / "data"))

    vectorstore = build_vectorstore(
        docs=docs,
        chunk_size=1000,
        chunk_overlap=100,
        persist_directory=None,
    )

    questions: List[str] = []
    answers: List[str] = []
    contexts: List[List[str]] = []
    ground_truths: List[str] = []

    for item in EVAL_QUESTIONS:
        question = item["question"]
        ground_truth = item["ground_truth"]

        search_result = search_documents(
            query=question,
            vectorstore=vectorstore,
            k=3,
            use_router=True,
        )

        answer_result = generate_answer(
            query=question,
            search_result=search_result,
        )

        retrieved_contexts = [
            doc.page_content for doc in answer_result["retrieved_documents"]
        ]

        questions.append(question)
        answers.append(answer_result["answer"])
        contexts.append(retrieved_contexts)
        ground_truths.append(ground_truth)

    dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    result_df = result.to_pandas()

    result_df["project"] = "DebugMate RAG"
    result_df["chunk_size"] = 1000
    result_df["chunk_overlap"] = 100
    result_df["k"] = 3

    return result_df


if __name__ == "__main__":
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    df = run_debugmate_evaluation()

    output_path = results_dir / "debugmate_ragas_results.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("RAGAS 평가 완료")
    print(df)
    print(f"저장 위치: {output_path}")
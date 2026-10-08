import json
import os
from uuid import uuid4

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)

PENDING_DIR = os.path.join(
    BACKEND_API_DIR,
    "data",
    "pending_csv",
)


def _ensure_pending_dir():
    os.makedirs(
        PENDING_DIR,
        exist_ok=True,
    )


def create_csv_analysis():
    _ensure_pending_dir()

    analysis_id = f"CSV-{uuid4().hex}"

    file_path = os.path.join(
        PENDING_DIR,
        f"{analysis_id}.jsonl",
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ):
        pass

    return analysis_id


def append_csv_analysis_records(
    analysis_id: str,
    records: list[dict],
):
    _ensure_pending_dir()

    file_path = os.path.join(
        PENDING_DIR,
        f"{analysis_id}.jsonl",
    )

    if not os.path.exists(file_path):
        raise ValueError("Hasil analisis CSV tidak ditemukan.")

    with open(
        file_path,
        "a",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def load_csv_analysis(
    analysis_id: str,
):
    _ensure_pending_dir()

    file_path = os.path.join(
        PENDING_DIR,
        f"{analysis_id}.jsonl",
    )

    if not os.path.exists(file_path):
        raise ValueError("Hasil analisis CSV sudah tidak tersedia.")

    records = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            records.append(json.loads(line))

    return records


def delete_csv_analysis(
    analysis_id: str,
):
    file_path = os.path.join(
        PENDING_DIR,
        f"{analysis_id}.jsonl",
    )

    if os.path.exists(file_path):
        os.remove(file_path)

import json
import os
from datetime import datetime
from typing import Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)

HISTORY_DIR = os.path.join(
    BACKEND_API_DIR,
    "data",
)

HISTORY_FILE = os.path.join(
    HISTORY_DIR,
    "history.json",
)


def _ensure_history_file():
    os.makedirs(
        HISTORY_DIR,
        exist_ok=True,
    )

    if not os.path.exists(HISTORY_FILE):
        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=2,
            )


def _load_history():
    _ensure_history_file()

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []


def _save_history(history):
    _ensure_history_file()

    temp_file = HISTORY_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_file,
        HISTORY_FILE,
    )


def save_transaction_history(
    amount: float,
    fraud_score: float,
    status: str,
    transaction_time: str,
):
    history = _load_history()

    transaction_id = (
        f"TRX-{datetime.now().strftime('%Y%m%d%H%M%S')}" f"-{len(history) + 1:04d}"
    )

    record = {
        "id": transaction_id,
        "amount": float(amount),
        "fraud_score": float(fraud_score),
        "status": status,
        "transaction_time": transaction_time,
        "created_at": datetime.now().isoformat(),
    }

    history.insert(
        0,
        record,
    )

    _save_history(history)

    return record


def get_transaction_history(
    search: Optional[str] = None,
    status: Optional[str] = None,
):
    history = _load_history()

    if search:
        search_value = search.strip().lower()

        history = [
            item
            for item in history
            if (
                search_value in str(item.get("id", "")).lower()
                or search_value in str(item.get("amount", "")).lower()
                or search_value
                in str(
                    item.get(
                        "transaction_time",
                        "",
                    )
                ).lower()
            )
        ]

    if status:
        normalized_status = status.strip().upper()

        if normalized_status in {
            "SAFE",
            "FRAUD",
        }:
            history = [
                item for item in history if item.get("status") == normalized_status
            ]

    return history

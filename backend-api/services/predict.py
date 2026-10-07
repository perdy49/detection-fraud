import os
from collections import deque

import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

from services.preprocess import preprocess_for_prediction
from services.preprocess_single import (
    preprocess_single_transaction,
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(
    BACKEND_API_DIR,
    "model",
)

XGB_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgb_model.pkl",
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl",
)

FEATURE_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.pkl",
)

LSTM_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "lstm_model.keras",
)


# =========================================================
# LOAD MODELS
# =========================================================

xgb_model = joblib.load(
    XGB_MODEL_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

lstm_model = load_model(
    LSTM_MODEL_PATH
)

feature_names = joblib.load(
    FEATURE_NAMES_PATH
)

FRAUD_THRESHOLD = 0.35


# =========================================================
# VALIDATE MODEL CONTRACT
# =========================================================

EXPECTED_FEATURES = scaler.n_features_in_

if len(feature_names) != EXPECTED_FEATURES:
    raise RuntimeError(
        "Model schema rusak: feature_names dan scaler berbeda."
    )

lstm_input_shape = lstm_model.input_shape

if len(lstm_input_shape) != 3:
    raise RuntimeError(
        "LSTM model harus menerima input 3 dimensi "
        "(batch, sequence, features)."
    )

SEQUENCE_LENGTH = lstm_input_shape[1]

if SEQUENCE_LENGTH is None:
    raise RuntimeError(
        "Sequence length LSTM tidak boleh None."
    )

LSTM_FEATURE_COUNT = lstm_input_shape[2]

if LSTM_FEATURE_COUNT != EXPECTED_FEATURES:
    raise RuntimeError(
        "Jumlah feature LSTM tidak cocok dengan scaler: "
        f"LSTM={LSTM_FEATURE_COUNT}, "
        f"scaler={EXPECTED_FEATURES}."
    )


# =========================================================
# CSV SEQUENCE BUFFER
# =========================================================

csv_sequence_buffer = deque(
    maxlen=SEQUENCE_LENGTH
)


def _predict_hybrid_batch(
    sequences,
    batch_size=512,
):
    """
    Run the existing LSTM -> XGBoost hybrid pipeline.

    No model is retrained or refit here.
    """
    sequences = np.asarray(
        sequences,
        dtype=np.float32,
    )

    lstm_features = lstm_model.predict(
        sequences,
        verbose=0,
        batch_size=batch_size,
    )

    xgb_input = sequences[:, -1, :]

    hybrid_input = np.hstack(
        (
            xgb_input,
            lstm_features,
        )
    )

    probabilities = xgb_model.predict_proba(
        hybrid_input
    )[:, 1]

    return probabilities


# =========================================================
# FULL FEATURE VECTOR
# =========================================================

def predict_transaction(data: list):
    if len(data) != EXPECTED_FEATURES:
        raise ValueError(
            f"Jumlah fitur harus {EXPECTED_FEATURES}, "
            f"tetapi dapat {len(data)}."
        )

    data = np.asarray(
        data,
        dtype=np.float32,
    ).reshape(
        1,
        -1,
    )

    data_scaled = scaler.transform(
        data
    )[0]

    csv_sequence_buffer.append(
        data_scaled
    )

    sequence = list(
        csv_sequence_buffer
    )

    while len(sequence) < SEQUENCE_LENGTH:
        sequence.insert(
            0,
            np.zeros_like(data_scaled),
        )

    sequence = np.asarray(
        sequence,
        dtype=np.float32,
    ).reshape(
        1,
        SEQUENCE_LENGTH,
        EXPECTED_FEATURES,
    )

    fraud_score = float(
        _predict_hybrid_batch(
            sequence,
            batch_size=1,
        )[0]
    )

    return fraud_score


# =========================================================
# SINGLE TRANSACTION
# =========================================================

def predict_single_transaction(
    amount: float,
    product_code: str,
    card_type: str,
    email: str,
    transaction_time: str,
):
    if not email or "@" not in email:
        raise ValueError(
            "Email tidak valid."
        )

    parsed_time = pd.Timestamp(
        transaction_time
    )

    email_domain = (
        email.split("@")[-1]
        .strip()
        .lower()
    )

    data_scaled = preprocess_single_transaction(
        amount=amount,
        product_code=product_code,
        card_type=card_type,
        email_domain=email_domain,
        transaction_hour=parsed_time.hour,
    )

    if data_scaled.shape != (
        1,
        EXPECTED_FEATURES,
    ):
        raise ValueError(
            "Single transaction preprocessing menghasilkan "
            f"shape {data_scaled.shape}, expected "
            f"(1, {EXPECTED_FEATURES})."
        )

    current_transaction = data_scaled[0]

    sequence = np.zeros(
        (
            SEQUENCE_LENGTH,
            EXPECTED_FEATURES,
        ),
        dtype=np.float32,
    )

    sequence[-1] = current_transaction

    sequence = sequence.reshape(
        1,
        SEQUENCE_LENGTH,
        EXPECTED_FEATURES,
    )

    probabilities = _predict_hybrid_batch(
        sequence,
        batch_size=1,
    )

    fraud_score = float(
        probabilities[0]
    )

    print(
        "\n========== SINGLE PREDICTION =========="
    )
    print(f"Amount       : {amount}")
    print(f"Product Code : {product_code}")
    print(f"Card Type    : {card_type}")
    print(f"Email        : {email}")
    print(f"Time         : {transaction_time}")
    print(f"Feature count: {data_scaled.shape[1]}")
    print(
        f"SAFE         : {1.0 - fraud_score:.6f}"
    )
    print(
        f"FRAUD        : {fraud_score:.6f}"
    )
    print("========================================\n")

    return fraud_score


# =========================================================
# BATCH CSV
# =========================================================

def predict_transactions_batch(
    df,
    batch_size=512,
):
    if df is None or df.empty:
        raise ValueError(
            "Data transaksi kosong."
        )

    if batch_size <= 0:
        raise ValueError(
            "batch_size harus lebih besar dari 0."
        )

    print(
        "[CSV] Batch prediction dimulai. "
        f"Jumlah transaksi: {len(df):,}",
        flush=True,
    )

    if "TransactionDT" in df.columns:
        df = df.sort_values(
            "TransactionDT"
        ).reset_index(drop=True)

    print(
        "[CSV] Mulai preprocessing...",
        flush=True,
    )

    X_scaled = preprocess_for_prediction(
        df.copy()
    )

    print(
        "[CSV] Preprocessing selesai. "
        f"Shape: {X_scaled.shape}",
        flush=True,
    )

    if X_scaled.shape[1] != EXPECTED_FEATURES:
        raise ValueError(
            "Jumlah fitur hasil preprocessing harus "
            f"{EXPECTED_FEATURES}, tetapi mendapat "
            f"{X_scaled.shape[1]}."
        )

    fraud_count = 0
    safe_count = 0
    preview_results = []

    total_rows = len(X_scaled)

    print(
        f"[CSV] Sequence length: {SEQUENCE_LENGTH}",
        flush=True,
    )

    for batch_start in range(
        0,
        total_rows,
        batch_size,
    ):
        batch_end = min(
            batch_start + batch_size,
            total_rows,
        )

        print(
            "[CSV] Memproses row "
            f"{batch_start + 1:,} - {batch_end:,} "
            f"dari {total_rows:,}",
            flush=True,
        )

        sequences = []

        for index in range(
            batch_start,
            batch_end,
        ):
            start_index = max(
                0,
                index - SEQUENCE_LENGTH + 1,
            )

            sequence = X_scaled[
                start_index : index + 1
            ]

            if len(sequence) < SEQUENCE_LENGTH:
                padding = np.zeros(
                    (
                        SEQUENCE_LENGTH - len(sequence),
                        EXPECTED_FEATURES,
                    ),
                    dtype=np.float32,
                )

                sequence = np.vstack(
                    (
                        padding,
                        sequence,
                    )
                )

            sequences.append(
                sequence
            )

        sequences = np.asarray(
            sequences,
            dtype=np.float32,
        )

        probabilities = _predict_hybrid_batch(
            sequences,
            batch_size=batch_size,
        )

        for local_index, score in enumerate(
            probabilities
        ):
            score = float(score)

            row_number = (
                batch_start
                + local_index
                + 1
            )

            status = (
                "FRAUD"
                if score >= FRAUD_THRESHOLD
                else "SAFE"
            )

            if status == "FRAUD":
                fraud_count += 1
            else:
                safe_count += 1

            if len(preview_results) < 100:
                preview_results.append(
                    {
                        "row": row_number,
                        "fraud_score": score,
                        "status": status,
                    }
                )

        del sequences
        del probabilities

        print(
            "[CSV] Batch selesai: "
            f"{batch_end:,}/{total_rows:,}",
            flush=True,
        )

    print(
        "[CSV] Semua batch selesai.",
        flush=True,
    )

    return {
        "total_transactions": total_rows,
        "fraud_count": fraud_count,
        "safe_count": safe_count,
        "preview": preview_results,
    }

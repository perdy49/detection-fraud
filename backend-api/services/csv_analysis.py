import csv
import json
import os
import shutil
import tempfile
import threading
import uuid
from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd

from services.feature_engineering import create_features


# =========================================================
# MODEL
# =========================================================

xgb_model = joblib.load("model/xgb_model.pkl")
scaler = joblib.load("model/scaler.pkl")
lstm_model = __import__("tensorflow").keras.models.load_model(
    "model/lstm_model.keras"
)
feature_names = joblib.load("model/feature_names.pkl")

SEQ_LEN = int(lstm_model.input_shape[1])
BATCH_ROWS = 2048

JOBS = {}
JOBS_LOCK = threading.Lock()


# =========================================================
# JOB STATE
# =========================================================

def set_job(job_id, **values):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(values)


def get_job(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        return dict(job) if job else None


# =========================================================
# UPLOAD STORAGE
# =========================================================

def save_upload(upload_file, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as output:
        shutil.copyfileobj(upload_file.file, output, length=1024 * 1024)


# =========================================================
# CSV HELPERS
# =========================================================

def _quote_path(path: str) -> str:
    return "'" + path.replace("'", "''") + "'"


def _looks_like_preprocessed(df: pd.DataFrame) -> bool:
    if len(df.columns) != scaler.n_features_in_:
        return False

    numeric = df.apply(pd.to_numeric, errors="coerce")
    return numeric.notna().all().all()


def _stable_encode(df: pd.DataFrame, maps: dict):
    """
    Fallback encoder used when the training encoder artifact is not
    available yet. The mapping is stable for the whole uploaded dataset,
    so different chunks cannot receive different category numbers.
    """

    for col in df.select_dtypes(include=["object"]).columns:
        values = df[col].fillna("missing").astype(str)

        if col not in maps:
            categories = sorted(values.unique().tolist())
            maps[col] = {value: index for index, value in enumerate(categories)}

        mapping = maps[col]
        df[col] = values.map(mapping).fillna(-1).astype(np.float32)

    return df


def _prepare_batch(
    raw: pd.DataFrame,
    encoder_maps: dict,
):
    if _looks_like_preprocessed(raw):
        return raw.to_numpy(dtype=np.float32), raw

    df = create_features(raw)

    if "isFraud" in df.columns:
        df = df.drop(columns=["isFraud"])

    if "TransactionID" in df.columns:
        ids = df["TransactionID"].copy()
        df = df.drop(columns=["TransactionID"])
    else:
        ids = pd.Series(
            np.arange(len(df)),
            index=df.index,
            name="TransactionID",
        )

    df = _stable_encode(df, encoder_maps)

    # Align exactly to the 444 model features.
    aligned = pd.DataFrame(
        index=df.index,
        columns=feature_names,
        dtype=np.float32,
    )

    for column in feature_names:
        if column in df.columns:
            aligned[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # A missing model input becomes the scaler mean, which becomes
    # approximately zero after StandardScaler.
    for index, column in enumerate(feature_names):
        aligned[column] = aligned[column].fillna(
            float(scaler.mean_[index])
        )

    aligned = aligned.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    for index, column in enumerate(feature_names):
        aligned[column] = aligned[column].fillna(
            float(scaler.mean_[index])
        )

    scaled = scaler.transform(aligned).astype(np.float32)

    meta = pd.DataFrame({
        "TransactionID": ids.to_numpy(),
    })

    return scaled, meta


def _predict_batch(
    scaled: np.ndarray,
    sequence_tail: np.ndarray,
):
    """
    Predict many transactions at once.

    This replaces one-LSTM-call-per-row with batched inference.
    """

    combined = np.concatenate(
        [sequence_tail, scaled],
        axis=0,
    )

    windows = np.lib.stride_tricks.sliding_window_view(
        combined,
        window_shape=SEQ_LEN,
        axis=0,
    )

    # sliding_window_view gives (rows, features, seq_len)
    windows = np.transpose(
        windows,
        (0, 2, 1),
    ).astype(np.float32, copy=False)

    lstm_feature = lstm_model.predict(
        windows,
        batch_size=256,
        verbose=0,
    )

    xgb_input = windows[:, -1, :]

    hybrid_input = np.hstack((
        xgb_input,
        lstm_feature,
    ))

    probabilities = xgb_model.predict_proba(
        hybrid_input,
    )[:, 1]

    new_tail = combined[-(SEQ_LEN - 1):].copy()

    return probabilities.astype(float), new_tail


# =========================================================
# RAW CSV QUERY
# =========================================================

def _build_relation(connection, transaction_path, identity_path):
    transaction = _quote_path(transaction_path)

    if identity_path:
        identity = _quote_path(identity_path)

        return connection.sql(
            f"""
            SELECT
                t.*,
                i.* EXCLUDE (TransactionID)
            FROM read_csv_auto({transaction}) AS t
            LEFT JOIN read_csv_auto({identity}) AS i
            USING (TransactionID)
            ORDER BY t.TransactionDT
            """
        )

    return connection.sql(
        f"""
        SELECT *
        FROM read_csv_auto({transaction})
        ORDER BY TransactionDT
        """
    )


# =========================================================
# ANALYSIS
# =========================================================

def analyze_csv(
    job_id: str,
    transaction_path: str,
    identity_path: str | None,
    result_path: str,
):
    temp_dir = Path(result_path).parent / "duckdb_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect()
    connection.execute(
        f"SET temp_directory = {_quote_path(str(temp_dir))}"
    )
    connection.execute("SET preserve_insertion_order = false")
    connection.execute("SET threads = 4")
    connection.execute("SET memory_limit = '60%'")


    try:
        set_job(
            job_id,
            status="processing",
            progress=1,
            message="Reading CSV...",
        )

        relation = _build_relation(
            connection,
            transaction_path,
            identity_path,
        )

        # Count without materializing the complete CSV in Python.
        total_rows = connection.sql(
            f"""
            SELECT COUNT(*)
            FROM ({relation.query}) AS source
            """
        ).fetchone()[0]

        total_rows = int(total_rows)

        set_job(
            job_id,
            total_rows=total_rows,
            progress=2,
            message="Preprocessing transactions...",
        )

        encoder_maps = {}
        sequence_tail = np.zeros(
            (SEQ_LEN - 1, scaler.n_features_in_),
            dtype=np.float32,
        )

        safe_count = 0
        fraud_count = 0
        score_sum = 0.0
        processed = 0
        highest = []

        result_file = Path(result_path)
        result_file.parent.mkdir(parents=True, exist_ok=True)

        with result_file.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as output:

            writer = csv.writer(output)
            writer.writerow([
                "TransactionID",
                "fraud_score",
                "status",
            ])

            while True:
                raw = relation.fetch_df_chunk(
                    max(1, BATCH_ROWS // 2048)
                )

                if raw.empty:
                    break

                scaled, meta = _prepare_batch(
                    raw,
                    encoder_maps,
                )

                # Split model input into moderate batches so a 444-feature
                # sequence never creates a giant RAM spike.
                for start in range(0, len(scaled), BATCH_ROWS):
                    end = min(
                        start + BATCH_ROWS,
                        len(scaled),
                    )

                    scores, sequence_tail = _predict_batch(
                        scaled[start:end],
                        sequence_tail,
                    )

                    ids = meta["TransactionID"].iloc[
                        start:end
                    ].tolist()

                    for transaction_id, score in zip(
                        ids,
                        scores,
                    ):
                        score = float(score)
                        status = (
                            "FRAUD"
                            if score > 0.5
                            else "SAFE"
                        )

                        writer.writerow([
                            transaction_id,
                            round(score, 6),
                            status,
                        ])

                        score_sum += score

                        if status == "FRAUD":
                            fraud_count += 1
                        else:
                            safe_count += 1

                        highest.append(
                            (score, transaction_id, status)
                        )

                processed += len(raw)

                # Keep only the most relevant few rows.
                highest = sorted(
                    highest,
                    key=lambda item: item[0],
                    reverse=True,
                )[:10]

                progress = 2 + int(
                    (processed / max(total_rows, 1)) * 96
                )

                set_job(
                    job_id,
                    progress=min(progress, 98),
                    processed_rows=processed,
                    message=(
                        f"Analyzing {processed:,} / "
                        f"{total_rows:,} transactions..."
                    ),
                )

        average_score = (
            score_sum / total_rows
            if total_rows
            else 0.0
        )

        summary = {
            "total_transactions": total_rows,
            "safe_transactions": safe_count,
            "fraud_transactions": fraud_count,
            "fraud_percentage": (
                fraud_count / total_rows * 100
                if total_rows
                else 0.0
            ),
            "average_fraud_score": average_score,
            "highest_risk": [
                {
                    "transaction_id": item[1],
                    "fraud_score": item[0],
                    "status": item[2],
                }
                for item in highest
            ],
        }

        set_job(
            job_id,
            status="completed",
            progress=100,
            processed_rows=total_rows,
            message="Analysis completed.",
            result=summary,
            result_path=str(result_file),
        )

    except Exception as exc:
        set_job(
            job_id,
            status="failed",
            progress=0,
            message=str(exc),
        )

    finally:
        connection.close()

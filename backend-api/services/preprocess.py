import os

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from services.feature_engineering import create_features


def preprocess_data(
    transaction_path,
    identity_path=None,
    is_training=True,
):
    # =========================
    # LOAD TRANSACTION DATA
    # =========================
    df_transaction = pd.read_csv(transaction_path)

    # =========================
    # LOAD IDENTITY DATA
    # =========================
    if identity_path:
        df_identity = pd.read_csv(identity_path)

        df = pd.merge(
            df_transaction,
            df_identity,
            on="TransactionID",
            how="left",
        )
    else:
        df = df_transaction.copy()

    # =========================
    # SORT TEMPORAL
    # =========================
    if "TransactionDT" in df.columns:
        df = df.sort_values("TransactionDT").reset_index(drop=True)

    # =========================
    # FEATURE ENGINEERING
    # =========================
    df = create_features(df)

    # =========================
    # TARGET
    # =========================
    y = None

    if "isFraud" in df.columns:
        y = df["isFraud"]

        df = df.drop(columns=["isFraud"])

    # =========================
    # DROP TRANSACTION ID
    # =========================
    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================
    # CATEGORICAL
    # =========================
    categorical_cols = df.select_dtypes(include=["object"]).columns

    label_encoders = {}

    for col in categorical_cols:
        df[col] = df[col].fillna("missing").astype(str)

        encoder = LabelEncoder()

        df[col] = encoder.fit_transform(df[col])

        label_encoders[col] = encoder

    # =========================
    # NUMERICAL MISSING
    # =========================
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # =========================
    # INF
    # =========================
    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    # =========================
    # FINAL FEATURES
    # =========================
    X = df.copy()

    feature_names = X.columns.tolist()

    # =========================
    # SCALER
    # =========================
    scaler = StandardScaler()

    if is_training:
        X_scaled = scaler.fit_transform(X)

        joblib.dump(
            scaler,
            "model/scaler.pkl",
        )

        joblib.dump(
            feature_names,
            "model/feature_names.pkl",
        )
    else:
        scaler = joblib.load("model/scaler.pkl")

        X_scaled = scaler.transform(X)

    return (
        X_scaled,
        y,
        scaler,
        feature_names,
    )


def preprocess_for_prediction(df):
    """
    Preprocessing inference.

    TIDAK melakukan:
    - fit scaler
    - fit encoder
    - retraining
    - perubahan model

    Hanya menggunakan artefak training
    yang sudah tersedia.
    """

    # =========================
    # FEATURE ENGINEERING
    # =========================
    df = create_features(df)

    # =========================
    # DROP TRANSACTION ID
    # =========================
    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================
    # LOAD FEATURE NAMES
    # =========================
    feature_names = joblib.load("model/feature_names.pkl")

    # =========================
    # ADD MISSING FEATURES
    # =========================
    missing_features = [
        feature for feature in feature_names if feature not in df.columns
    ]

    if missing_features:
        for feature in missing_features:
            df[feature] = 0

    # =========================
    # ALIGN FEATURES
    # =========================
    df = df[feature_names]

    # =========================
    # LOAD ENCODERS
    # =========================
    encoder_path = "model/label_encoders.pkl"

    if not os.path.exists(encoder_path):
        raise FileNotFoundError("label_encoders.pkl tidak ditemukan.")

    label_encoders = joblib.load(encoder_path)

    # =========================
    # ENCODE CATEGORICAL
    # =========================
    for col, encoder in label_encoders.items():
        if col not in df.columns:
            continue

        series = df[col].fillna("0").astype(str)

        known_categories = set(encoder.classes_.astype(str))

        # ---------------------------------
        # DETEKSI UNKNOWN
        # ---------------------------------
        unknown_categories = sorted(set(series.unique()) - known_categories)

        if unknown_categories:
            examples = unknown_categories[:10]

            raise ValueError(
                f"Kolom '{col}' memiliki "
                f"kategori yang tidak ada "
                f"saat training: "
                f"{examples}. "
                f"File harus menggunakan "
                f"kategori yang kompatibel "
                f"dengan dataset training."
            )

        # ---------------------------------
        # ENCODE
        # ---------------------------------
        df[col] = encoder.transform(series)

    # =========================
    # CHECK OBJECT / STRING
    # =========================
    remaining_object_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(remaining_object_cols) > 0:
        raise ValueError(
            "Masih terdapat kolom "
            "categorical yang belum "
            "menjadi numerik: "
            f"{list(remaining_object_cols)}"
        )

    # =========================
    # NUMERIC CLEANUP
    # =========================
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(0)

    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    # =========================
    # LOAD TRAINED SCALER
    # =========================
    scaler = joblib.load("model/scaler.pkl")

    # =========================
    # VALIDATE FEATURE COUNT
    # =========================
    expected_features = scaler.n_features_in_

    if df.shape[1] != expected_features:
        raise ValueError(
            "Jumlah fitur setelah "
            "preprocessing harus "
            f"{expected_features}, "
            f"tetapi mendapat "
            f"{df.shape[1]}"
        )

    # =========================
    # SCALE
    # =========================
    X_scaled = scaler.transform(df)

    return X_scaled

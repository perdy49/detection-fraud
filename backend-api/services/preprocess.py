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
    # =========================================================
    # LOAD TRANSACTION
    # =========================================================

    df_transaction = pd.read_csv(transaction_path)

    # =========================================================
    # LOAD IDENTITY
    # =========================================================

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

    # =========================================================
    # SORT TEMPORAL
    # =========================================================

    if "TransactionDT" in df.columns:
        df = df.sort_values("TransactionDT").reset_index(drop=True)

    # =========================================================
    # FEATURE ENGINEERING
    # =========================================================

    df = create_features(df)

    # =========================================================
    # TARGET
    # =========================================================

    y = None

    if "isFraud" in df.columns:
        y = df["isFraud"]

        df = df.drop(columns=["isFraud"])

    # =========================================================
    # TRANSACTION ID
    # =========================================================

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================================================
    # CATEGORICAL
    # =========================================================

    categorical_cols = df.select_dtypes(include=["object", "string"]).columns

    label_encoders = {}

    for col in categorical_cols:
        df[col] = df[col].fillna("0").astype(str)

        encoder = LabelEncoder()

        df[col] = encoder.fit_transform(df[col])

        label_encoders[col] = encoder

    # =========================================================
    # NUMERICAL MISSING
    # =========================================================

    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # =========================================================
    # INFINITY
    # =========================================================

    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    # =========================================================
    # FINAL FEATURES
    # =========================================================

    X = df.copy()

    feature_names = X.columns.tolist()

    # =========================================================
    # SCALER
    # =========================================================

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
    Preprocessing CSV inference.

    Tidak:
    - fit scaler baru
    - fit encoder baru
    - retrain model
    - mengubah model

    Hanya menggunakan artefak training.
    """

    # =========================================================
    # FEATURE ENGINEERING
    # =========================================================

    df = create_features(df)

    # =========================================================
    # DROP TRANSACTION ID
    # =========================================================

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================================================
    # LOAD FEATURE NAMES
    # =========================================================

    feature_names = joblib.load("model/feature_names.pkl")

    # =========================================================
    # ADD MISSING FEATURES
    # =========================================================
    #
    # Hanya feature yang memang diperlukan model.
    # Tidak menambahkan feature sembarangan.
    # =========================================================

    missing_features = [
        feature for feature in feature_names if feature not in df.columns
    ]

    for feature in missing_features:
        df[feature] = 0

    # =========================================================
    # ALIGN FEATURE ORDER
    # =========================================================

    df = df[feature_names]

    # =========================================================
    # LOAD TRAINING ENCODERS
    # =========================================================

    encoder_path = "model/label_encoders.pkl"

    if not os.path.exists(encoder_path):
        raise FileNotFoundError(
            "model/label_encoders.pkl "
            "tidak ditemukan. "
            "Jalankan create_label_encoders.py "
            "terlebih dahulu."
        )

    label_encoders = joblib.load(encoder_path)

    # =========================================================
    # ENCODE CATEGORICAL
    # =========================================================

    unknown_categories = {}

    for col, encoder in label_encoders.items():
        if col not in df.columns:
            continue

        # Semua nilai dibuat string agar
        # identik dengan encoder training.
        series = df[col].fillna("0").astype(str)

        known_categories = set(encoder.classes_.astype(str))

        # -----------------------------------------------------
        # NILAI "0" = MISSING
        # -----------------------------------------------------
        #
        # Jika "0" memang tidak ada pada training encoder,
        # jangan langsung dianggap kategori valid.
        #
        # Cari representasi missing yang memang dipelajari
        # encoder.
        # -----------------------------------------------------

        if "0" not in known_categories and "missing" in known_categories:
            series = series.replace(
                "0",
                "missing",
            )

            known_categories = set(encoder.classes_.astype(str))

        # -----------------------------------------------------
        # DETECT UNKNOWN
        # -----------------------------------------------------

        current_categories = set(series.unique())

        unknown = sorted(current_categories - known_categories)

        if unknown:
            unknown_categories[col] = unknown[:10]

            continue

        # -----------------------------------------------------
        # ENCODE
        # -----------------------------------------------------

        df[col] = encoder.transform(series)

    # =========================================================
    # REAL UNKNOWN CATEGORY
    # =========================================================

    if unknown_categories:
        messages = []

        for col, categories in unknown_categories.items():
            messages.append(f"{col}: {categories}")

        raise ValueError(
            "Ditemukan kategori yang "
            "benar-benar tidak pernah ada "
            "saat training:\n" + "\n".join(messages) + "\n\n"
            "Nilai ini tidak dipaksa menjadi "
            "kategori lain karena dapat "
            "mengubah arti fitur model."
        )

    # =========================================================
    # CHECK REMAINING STRING
    # =========================================================

    remaining_object_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(remaining_object_cols) > 0:
        raise ValueError(
            "Masih terdapat kolom "
            "categorical yang belum "
            "menjadi numerik: "
            f"{list(remaining_object_cols)}"
        )

    # =========================================================
    # NUMERIC CLEANUP
    # =========================================================

    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(0)

    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    # =========================================================
    # LOAD SCALER
    # =========================================================

    scaler = joblib.load("model/scaler.pkl")

    # =========================================================
    # VALIDATE FEATURE COUNT
    # =========================================================

    expected_features = scaler.n_features_in_

    if df.shape[1] != expected_features:
        raise ValueError(
            "Jumlah fitur setelah "
            "preprocessing harus "
            f"{expected_features}, "
            f"tetapi mendapat "
            f"{df.shape[1]}"
        )

    # =========================================================
    # SCALE
    # =========================================================

    X_scaled = scaler.transform(df)

    return X_scaled

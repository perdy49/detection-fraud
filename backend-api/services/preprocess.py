import os
import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import StandardScaler, LabelEncoder

from services.feature_engineering import create_features


def preprocess_data(transaction_path, identity_path=None, is_training=True):
    # =========================
    # LOAD TRANSACTION DATA
    # =========================
    df_transaction = pd.read_csv(transaction_path)

    # =========================
    # LOAD IDENTITY DATA
    # =========================
    if identity_path:
        df_identity = pd.read_csv(identity_path)

        df = pd.merge(df_transaction, df_identity, on="TransactionID", how="left")
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
    # DROP NON-PREDICTIVE ID
    # =========================
    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================
    # HANDLE CATEGORICAL
    # =========================
    categorical_cols = df.select_dtypes(include=["object"]).columns

    label_encoders = {}

    for col in categorical_cols:
        df[col] = df[col].fillna("missing")

        le = LabelEncoder()

        df[col] = le.fit_transform(df[col].astype(str))

        label_encoders[col] = le

    # =========================
    # HANDLE NUMERICAL MISSING
    # =========================
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # =========================
    # HANDLE INF
    # =========================
    df.replace([np.inf, -np.inf], 0, inplace=True)

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

        joblib.dump(scaler, "model/scaler.pkl")

        joblib.dump(feature_names, "model/feature_names.pkl")

    else:
        scaler = joblib.load("model/scaler.pkl")

        X_scaled = scaler.transform(X)

    return X_scaled, y, scaler, feature_names


def preprocess_for_prediction(df):
    """
    Preprocess transaction data for inference.

    Encoding categorical menggunakan LabelEncoder
    yang dibuat dari dataset training asli.

    Tidak melakukan:
    - training model
    - fit scaler
    - fit encoder baru
    """

    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================

    df = create_features(df)

    # =====================================================
    # DROP ID
    # =====================================================

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =====================================================
    # LOAD FEATURE NAMES
    # =====================================================

    feature_names = joblib.load("model/feature_names.pkl")

    # =====================================================
    # TAMBAHKAN FEATURE YANG TIDAK ADA
    # =====================================================

    missing_features = [
        feature for feature in feature_names if feature not in df.columns
    ]

    if missing_features:
        df = pd.concat(
            [df, pd.DataFrame(0, index=df.index, columns=missing_features)], axis=1
        )

    # =====================================================
    # BUANG FEATURE YANG TIDAK DIPAKAI
    # =====================================================

    df = df[feature_names]

    # =====================================================
    # LOAD TRAINING ENCODERS
    # =====================================================

    encoder_path = "model/label_encoders.pkl"

    if not os.path.exists(encoder_path):
        raise FileNotFoundError(
            "label_encoders.pkl tidak ditemukan. "
            "Jalankan create_label_encoders.py terlebih dahulu."
        )

    label_encoders = joblib.load(encoder_path)

    # =====================================================
    # CATEGORICAL ENCODING
    # =====================================================

    for col, encoder in label_encoders.items():

        if col not in df.columns:
            continue

        df[col] = df[col].fillna("missing").astype(str)

        # -------------------------------------------------
        # CEK CATEGORY UNKNOWN
        # -------------------------------------------------

        known_categories = set(encoder.classes_)

        current_categories = set(df[col].unique())

        unknown_categories = current_categories - known_categories

        if unknown_categories:

            examples = sorted(list(unknown_categories))[:10]

            raise ValueError(
                f"Kolom '{col}' memiliki kategori "
                f"yang tidak pernah ada saat training: "
                f"{examples}"
            )

        # -------------------------------------------------
        # GUNAKAN MAPPING TRAINING
        # -------------------------------------------------

        df[col] = encoder.transform(df[col])

    # =====================================================
    # HANDLE CATEGORICAL YANG TIDAK ADA DI ENCODER
    # =====================================================

    remaining_object_cols = df.select_dtypes(include=["object"]).columns

    if len(remaining_object_cols) > 0:

        raise ValueError(
            "Ditemukan kolom categorical yang "
            "tidak memiliki encoder training: "
            f"{list(remaining_object_cols)}"
        )

    # =====================================================
    # NUMERICAL MISSING
    # =====================================================

    numerical_cols = df.select_dtypes(include=[np.number]).columns

    for col in numerical_cols:

        df[col] = df[col].fillna(0)

    # =====================================================
    # HANDLE INF
    # =====================================================

    df.replace([np.inf, -np.inf], 0, inplace=True)

    # =====================================================
    # LOAD TRAINED SCALER
    # =====================================================

    scaler = joblib.load("model/scaler.pkl")

    # =====================================================
    # SCALE
    # =====================================================

    X_scaled = scaler.transform(df)

    return X_scaled

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

    Encoding categorical menggunakan encoder
    yang dibuat dari dataset training.

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
    # DROP TRANSACTION ID
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
    # GUNAKAN HANYA FEATURE MODEL
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

        # Ambil nilai asli
        series = df[col].copy()

        # -----------------------------------------------
        # NILAI MISSING
        # -----------------------------------------------
        #
        # create_features() mengubah missing string
        # menjadi "0".
        #
        # "0" DI SINI BUKAN kategori baru.
        # Ini adalah representasi missing.
        #

        missing_mask = series.isna() | series.astype(str).eq("0")

        # -----------------------------------------------
        # SIAPKAN HASIL NUMERIK
        # -----------------------------------------------

        encoded = pd.Series(0.0, index=df.index)

        # -----------------------------------------------
        # NILAI YANG BENAR-BENAR ADA
        # -----------------------------------------------

        valid_mask = ~missing_mask

        if valid_mask.any():

            valid_values = series.loc[valid_mask].astype(str)

            known_categories = set(encoder.classes_.astype(str))

            unknown_categories = set(valid_values.unique()) - known_categories

            # -------------------------------------------
            # UNKNOWN CATEGORY
            # -------------------------------------------

            if unknown_categories:

                examples = sorted(list(unknown_categories))[:10]

                print(
                    f"[WARNING] Kolom '{col}' "
                    f"memiliki {len(unknown_categories)} "
                    f"kategori yang tidak dikenal. "
                    f"Contoh: {examples}. "
                    f"Nilai tersebut diperlakukan "
                    f"sebagai missing."
                )

                unknown_mask = valid_values.isin(unknown_categories)

                known_mask = ~unknown_mask

                known_values = valid_values.loc[known_mask]

                if len(known_values) > 0:
                    encoded.loc[known_values.index] = encoder.transform(known_values)

            else:

                # Semua kategori dikenal
                encoded.loc[valid_values.index] = encoder.transform(valid_values)

        # -----------------------------------------------
        # SIMPAN HASIL ENCODING
        # -----------------------------------------------

        df[col] = encoded

    # =====================================================
    # CEK OBJECT / STRING YANG TERSISA
    # =====================================================

    remaining_object_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(remaining_object_cols) > 0:

        raise ValueError(
            "Masih terdapat kolom categorical "
            "yang belum berhasil diubah menjadi numerik: "
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
    # FINAL VALIDATION
    # =====================================================

    expected_features = scaler.n_features_in_

    if df.shape[1] != expected_features:

        raise ValueError(
            "Jumlah fitur setelah preprocessing "
            f"harus {expected_features}, "
            f"tetapi mendapat {df.shape[1]}"
        )

    # =====================================================
    # SCALE
    # =====================================================

    X_scaled = scaler.transform(df)

    return X_scaled

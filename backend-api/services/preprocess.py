import os

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from services.feature_engineering import (
    build_reference_stats,
    create_features,
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(BACKEND_API_DIR, "model")

SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "feature_names.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoders.pkl")


def _load_feature_names():
    if not os.path.exists(FEATURE_NAMES_PATH):
        raise FileNotFoundError(
            f"Feature schema tidak ditemukan: {FEATURE_NAMES_PATH}"
        )

    return joblib.load(FEATURE_NAMES_PATH)


def _load_preprocessing_metadata():
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(
            "model/label_encoders.pkl tidak ditemukan. "
            "Jalankan backend-api/services/create_label_encoders.py "
            "terlebih dahulu."
        )

    metadata = joblib.load(ENCODER_PATH)

    # Backward compatibility dengan artifact lama yang hanya berisi
    # {column: LabelEncoder}.
    if isinstance(metadata, dict) and "encoders" in metadata:
        return metadata

    if isinstance(metadata, dict):
        return {
            "version": 1,
            "encoders": metadata,
            "categorical_defaults": {
                col: (
                    str(encoder.classes_[0])
                    if len(encoder.classes_) > 0
                    else "0"
                )
                for col, encoder in metadata.items()
            },
            "feature_engineering_stats": {},
        }

    raise ValueError(
        "Format model/label_encoders.pkl tidak valid."
    )


def _validate_model_schema(feature_names, scaler):
    if len(feature_names) != scaler.n_features_in_:
        raise ValueError(
            "Feature schema dan scaler tidak cocok: "
            f"feature_names={len(feature_names)}, "
            f"scaler={scaler.n_features_in_}."
        )


def preprocess_data(
    transaction_path,
    identity_path=None,
    is_training=True,
):
    """
    Training-compatible preprocessing.

    IMPORTANT:
    Existing Hybrid XGBoost + LSTM artifacts were trained with:
        categorical missing -> "0"
        numeric missing      -> 0

    This function keeps that contract.
    """

    df_transaction = pd.read_csv(transaction_path)

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

    if "TransactionDT" in df.columns:
        df = df.sort_values(
            "TransactionDT"
        ).reset_index(drop=True)

    df = create_features(df)

    y = None

    if "isFraud" in df.columns:
        y = df["isFraud"].astype(int)
        df = df.drop(columns=["isFraud"])

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    categorical_cols = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    label_encoders = {}

    for col in categorical_cols:
        series = (
            df[col]
            .fillna("0")
            .astype(str)
            .str.strip()
        )

        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(series)
        label_encoders[col] = encoder

    numerical_cols = df.select_dtypes(
        include=[np.number]
    ).columns

    for col in numerical_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        ).fillna(0)

    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    feature_names = df.columns.tolist()
    X = df[feature_names].copy()

    scaler = StandardScaler()

    if is_training:
        X_scaled = scaler.fit_transform(X)

        os.makedirs(MODEL_DIR, exist_ok=True)

        joblib.dump(
            scaler,
            SCALER_PATH,
        )

        joblib.dump(
            feature_names,
            FEATURE_NAMES_PATH,
        )

        # Save the exact encoder artifact used by this preprocessing.
        joblib.dump(
            {
                "version": 2,
                "encoders": label_encoders,
                "categorical_defaults": {
                    col: str(series.mode().iloc[0])
                    if not series.mode().empty
                    else "0"
                    for col, series in (
                        (
                            col,
                            df[col].astype(str),
                        )
                        for col in categorical_cols
                    )
                },
            },
            ENCODER_PATH,
        )
    else:
        scaler = joblib.load(SCALER_PATH)
        X_scaled = scaler.transform(X)

    return (
        X_scaled,
        y,
        scaler,
        feature_names,
    )


def preprocess_for_prediction(df):
    """
    Prepare an uploaded CSV for the EXISTING trained model.

    Rules:
    1. Never fit an encoder.
    2. Never fit a scaler.
    3. Never create a new feature schema.
    4. Missing columns are completed using training-compatible defaults.
    5. Empty categorical cells use a training category, never an invented
       category such as "0" when that category did not exist in training.
    6. Truly unknown non-empty categories still raise an error.
    """

    if df is None or df.empty:
        raise ValueError("Data transaksi kosong.")

    scaler = joblib.load(SCALER_PATH)
    feature_names = _load_feature_names()
    metadata = _load_preprocessing_metadata()

    _validate_model_schema(
        feature_names,
        scaler,
    )

    encoders = metadata["encoders"]
    categorical_defaults = metadata.get(
        "categorical_defaults",
        {},
    )

    reference_stats = metadata.get(
        "feature_engineering_stats",
        {},
    )

    # Feature engineering must use training-derived aggregate statistics,
    # not statistics calculated from the uploaded file.
    df = create_features(
        df.copy(),
        reference_stats=reference_stats,
    )

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # ---------------------------------------------------------
    # COMPLETE MISSING MODEL FEATURES
    # ---------------------------------------------------------

    for feature in feature_names:
        if feature in df.columns:
            continue

        if feature in encoders:
            default_value = categorical_defaults.get(
                feature,
                str(encoders[feature].classes_[0]),
            )

            df[feature] = default_value
        else:
            # Existing model was trained with zero-imputation.
            df[feature] = 0

    # Ignore columns not used by the model and align exact order.
    df = df.reindex(columns=feature_names)

    # ---------------------------------------------------------
    # CATEGORICAL TRANSFORMATION
    # ---------------------------------------------------------

    unknown_categories = {}

    for col, encoder in encoders.items():
        if col not in df.columns:
            continue

        default_value = categorical_defaults.get(
            col,
            str(encoder.classes_[0]),
        )

        series = (
            df[col]
            .replace(
                {
                    "": np.nan,
                    "nan": np.nan,
                    "NaN": np.nan,
                    "None": np.nan,
                    "null": np.nan,
                    "NULL": np.nan,
                }
            )
            .fillna(default_value)
            .astype(str)
            .str.strip()
        )

        known_categories = set(
            encoder.classes_.astype(str)
        )

        unknown_mask = ~series.isin(
            known_categories
        )

        if unknown_mask.any():
            unknown_categories[col] = sorted(
                series.loc[unknown_mask]
                .dropna()
                .unique()
                .tolist()
            )[:10]

            continue

        df[col] = encoder.transform(series)

    if unknown_categories:
        messages = [
            f"{col}: {categories}"
            for col, categories in unknown_categories.items()
        ]

        raise ValueError(
            "Ditemukan kategori baru yang benar-benar tidak ada "
            "saat training:\n"
            + "\n".join(messages)
            + "\n\n"
            "Kosong/NaN sudah ditangani sebagai missing value. "
            "Kategori baru yang berisi nilai nyata tidak boleh "
            "dipaksa menjadi kategori lain karena akan mengubah "
            "arti fitur model."
        )

    # ---------------------------------------------------------
    # NUMERIC CLEANUP
    # ---------------------------------------------------------

    for col in feature_names:
        if col in encoders:
            continue

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        ).fillna(0)

    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True,
    )

    # ---------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------

    if df.shape[1] != scaler.n_features_in_:
        raise ValueError(
            "Jumlah fitur setelah preprocessing harus "
            f"{scaler.n_features_in_}, tetapi mendapat "
            f"{df.shape[1]}."
        )

    if df.isna().any().any():
        raise ValueError(
            "Masih terdapat NaN setelah preprocessing."
        )

    if not np.isfinite(
        df.to_numpy(dtype=np.float64)
    ).all():
        raise ValueError(
            "Masih terdapat nilai infinity setelah preprocessing."
        )

    return scaler.transform(df)

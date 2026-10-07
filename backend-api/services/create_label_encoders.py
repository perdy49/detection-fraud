import os
import sys

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_API_DIR)

TRAINING_DIR = os.path.join(
    PROJECT_DIR,
    "sistem backend-ai",
)

DATA_DIR = os.path.join(
    TRAINING_DIR,
    "data",
)

TRANSACTION_PATH = os.path.join(
    DATA_DIR,
    "train_transaction.csv",
)

IDENTITY_PATH = os.path.join(
    DATA_DIR,
    "train_identity.csv",
)

OUTPUT_PATH = os.path.join(
    BACKEND_API_DIR,
    "model",
    "label_encoders.pkl",
)

FEATURE_NAMES_PATH = os.path.join(
    BACKEND_API_DIR,
    "model",
    "feature_names.pkl",
)

sys.path.insert(
    0,
    BACKEND_API_DIR,
)

from services.feature_engineering import (
    build_reference_stats,
    create_features,
)


def _normalise_key(value):
    if pd.isna(value):
        return None

    try:
        numeric = float(value)

        if numeric.is_integer():
            return str(int(numeric))
    except (TypeError, ValueError):
        pass

    return str(value).strip().lower()


def create_label_encoders():
    print("=" * 70)
    print("MEMBUAT ARTIFACT PREPROCESSING DARI DATASET TRAINING")
    print("=" * 70)

    if not os.path.exists(TRANSACTION_PATH):
        raise FileNotFoundError(
            f"Training transaction tidak ditemukan: {TRANSACTION_PATH}"
        )

    if not os.path.exists(IDENTITY_PATH):
        raise FileNotFoundError(
            f"Training identity tidak ditemukan: {IDENTITY_PATH}"
        )

    print("\n[1/7] Membaca train_transaction.csv...")
    df_transaction = pd.read_csv(
        TRANSACTION_PATH
    )
    print(f"Rows: {len(df_transaction):,}")

    print("\n[2/7] Membaca train_identity.csv...")
    df_identity = pd.read_csv(
        IDENTITY_PATH
    )
    print(f"Rows: {len(df_identity):,}")

    print("\n[3/7] Merge training...")
    df = pd.merge(
        df_transaction,
        df_identity,
        on="TransactionID",
        how="left",
    )

    if "TransactionDT" in df.columns:
        df = df.sort_values(
            "TransactionDT"
        ).reset_index(drop=True)

    # Save aggregate statistics BEFORE feature engineering.
    # Inference will reuse these statistics instead of calculating
    # them from the uploaded CSV.
    print("\n[4/7] Menyimpan statistik feature engineering...")
    reference_stats = build_reference_stats(df)

    print("\n[5/7] Feature engineering training...")
    processed = create_features(
        df.copy()
    )

    if "isFraud" in processed.columns:
        processed = processed.drop(
            columns=["isFraud"]
        )

    if "TransactionID" in processed.columns:
        processed = processed.drop(
            columns=["TransactionID"]
        )

    categorical_cols = processed.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    print(
        f"Categorical columns: {len(categorical_cols)}"
    )

    encoders = {}
    categorical_defaults = {}

    for col in categorical_cols:
        series = (
            processed[col]
            .fillna("0")
            .astype(str)
            .str.strip()
        )

        encoder = LabelEncoder()
        encoder.fit(series)

        encoders[col] = encoder

        mode = series.mode()
        categorical_defaults[col] = (
            str(mode.iloc[0])
            if not mode.empty
            else str(encoder.classes_[0])
        )

        print(
            f"  {col}: "
            f"{len(encoder.classes_)} kategori | "
            f"default={categorical_defaults[col]}"
        )

    # Save a schema-safe artifact.
    feature_names = processed.columns.tolist()

    if os.path.exists(FEATURE_NAMES_PATH):
        existing_feature_names = joblib.load(
            FEATURE_NAMES_PATH
        )

        if feature_names != existing_feature_names:
            raise ValueError(
                "Feature schema hasil training preprocessing berbeda "
                "dengan model/feature_names.pkl.\n"
                f"Generated: {len(feature_names)} features\n"
                f"Model:    {len(existing_feature_names)} features"
            )

    # Numeric defaults are kept at zero because the existing trained
    # model was trained after numeric NaN values were replaced by 0.
    numeric_columns = [
        col
        for col in feature_names
        if col not in encoders
    ]

    print("\n[6/7] Menyimpan artifact...")
    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True,
    )

    metadata = {
        "version": 2,
        "encoding_strategy": "LabelEncoder",
        "missing_categorical_strategy": "training_default_category",
        "missing_numeric_strategy": "zero",
        "encoders": encoders,
        "categorical_defaults": categorical_defaults,
        "numeric_columns": numeric_columns,
        "feature_names": feature_names,
        "feature_engineering_stats": reference_stats,
    }

    joblib.dump(
        metadata,
        OUTPUT_PATH,
    )

    print(f"Artifact tersimpan: {OUTPUT_PATH}")
    print(
        f"Total encoder: {len(encoders)}"
    )
    print(
        f"Total features: {len(feature_names)}"
    )

    print("\n[7/7] VALIDASI...")
    for col, encoder in encoders.items():
        default = categorical_defaults[col]

        if default not in set(
            encoder.classes_.astype(str)
        ):
            raise ValueError(
                f"Default kategori {col}={default!r} "
                "tidak ada di encoder."
            )

    print("Artifact preprocessing VALID.")
    print("\nSELESAI.")


if __name__ == "__main__":
    create_label_encoders()

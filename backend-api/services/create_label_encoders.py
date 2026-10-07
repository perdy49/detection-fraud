import os
import sys

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# =========================================================
# PATH
# =========================================================

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


# =========================================================
# IMPORT FEATURE ENGINEERING
# =========================================================

sys.path.insert(
    0,
    BACKEND_API_DIR,
)

from services.feature_engineering import (
    create_features,
)

# =========================================================
# MAIN
# =========================================================


def create_label_encoders():

    print("=" * 60)
    print("MEMBUAT LABEL ENCODERS " "DARI DATASET TRAINING")
    print("=" * 60)

    # =========================
    # VALIDATE FILE
    # =========================

    if not os.path.exists(TRANSACTION_PATH):
        raise FileNotFoundError(TRANSACTION_PATH)

    if not os.path.exists(IDENTITY_PATH):
        raise FileNotFoundError(IDENTITY_PATH)

    # =========================
    # LOAD TRANSACTION
    # =========================

    print("\n[1/6] Membaca " "train_transaction.csv...")

    df_transaction = pd.read_csv(TRANSACTION_PATH)

    print(f"Rows: {len(df_transaction):,}")

    # =========================
    # LOAD IDENTITY
    # =========================

    print("\n[2/6] Membaca " "train_identity.csv...")

    df_identity = pd.read_csv(IDENTITY_PATH)

    print(f"Rows: {len(df_identity):,}")

    # =========================
    # MERGE
    # =========================

    print("\n[3/6] Merge...")

    df = pd.merge(
        df_transaction,
        df_identity,
        on="TransactionID",
        how="left",
    )

    # =========================
    # SORT
    # =========================

    if "TransactionDT" in df.columns:
        df = df.sort_values("TransactionDT").reset_index(drop=True)

    # =========================
    # FEATURE ENGINEERING
    # =========================

    print("\n[4/6] Feature engineering...")

    df = create_features(df)

    # =========================
    # TARGET
    # =========================

    if "isFraud" in df.columns:
        df = df.drop(columns=["isFraud"])

    # =========================
    # TRANSACTION ID
    # =========================

    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================
    # CATEGORICAL
    # =========================

    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    print("\n[5/6] Categorical:")

    print(f"Total: {len(categorical_cols)}")

    label_encoders = {}

    for col in categorical_cols:

        df[col] = df[col].fillna("missing").astype(str)

        encoder = LabelEncoder()

        encoder.fit(df[col])

        label_encoders[col] = encoder

        print(f"{col}: " f"{len(encoder.classes_)} kategori")

    # =========================
    # SAVE
    # =========================

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True,
    )

    joblib.dump(
        label_encoders,
        OUTPUT_PATH,
    )

    print("\n[6/6] Encoder tersimpan:")

    print(OUTPUT_PATH)

    print(f"\nTotal encoder: " f"{len(label_encoders)}")

    print("\nSELESAI")


if __name__ == "__main__":
    create_label_encoders()

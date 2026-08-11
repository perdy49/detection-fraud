import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import StandardScaler, LabelEncoder

from services.feature_engineering import create_features


def preprocess_data(
    transaction_path,
    identity_path=None,
    is_training=True
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
            how="left"
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
    # DROP NON-PREDICTIVE ID
    # =========================
    if "TransactionID" in df.columns:
        df = df.drop(columns=["TransactionID"])

    # =========================
    # HANDLE CATEGORICAL
    # =========================
    categorical_cols = df.select_dtypes(
        include=["object"]
    ).columns

    label_encoders = {}

    for col in categorical_cols:
        df[col] = df[col].fillna("missing")

        le = LabelEncoder()

        df[col] = le.fit_transform(
            df[col].astype(str)
        )

        label_encoders[col] = le

    # =========================
    # HANDLE NUMERICAL MISSING
    # =========================
    numerical_cols = df.select_dtypes(
        include=[np.number]
    ).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(
            df[col].median()
        )

    # =========================
    # HANDLE INF
    # =========================
    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True
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
            "model/scaler.pkl"
        )

        joblib.dump(
            feature_names,
            "model/feature_names.pkl"
        )

    else:
        scaler = joblib.load(
            "model/scaler.pkl"
        )

        X_scaled = scaler.transform(X)

    return X_scaled, y, scaler, feature_names
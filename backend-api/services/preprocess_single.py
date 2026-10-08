import os

import joblib
import numpy as np
import pandas as pd

from services.feature_engineering import create_features


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_API_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(
    BACKEND_API_DIR,
    "model",
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl",
)

FEATURE_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.pkl",
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "label_encoders.pkl",
)


def _load_preprocessing():
    scaler = joblib.load(
        SCALER_PATH
    )

    feature_names = joblib.load(
        FEATURE_NAMES_PATH
    )

    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(
            "model/label_encoders.pkl tidak ditemukan. "
            "Jalankan create_label_encoders.py terlebih dahulu."
        )

    metadata = joblib.load(
        ENCODER_PATH
    )

    if isinstance(metadata, dict) and "encoders" in metadata:
        encoders = metadata["encoders"]
        defaults = metadata.get(
            "categorical_defaults",
            {},
        )
    else:
        # Compatibility with old artifact.
        encoders = metadata
        defaults = {
            col: str(encoder.classes_[0])
            for col, encoder in encoders.items()
        }

    return (
        scaler,
        feature_names,
        encoders,
        defaults,
    )


def _encode_category(
    value,
    encoder,
    default_value,
):
    """
    Encode categorical value for SINGLE TRANSACTION only.

    Empty values and numeric placeholders produced by the small
    single-transaction form are treated as missing values.

    Real unknown categories are still rejected.
    """

    if value is None:
        value = default_value

    value = str(value).strip()

    # ---------------------------------------------------------
    # MISSING VALUE
    # ---------------------------------------------------------

    if value == "":
        value = default_value

    if value.lower() in {
        "nan",
        "none",
        "null",
        "na",
        "<na>",
    }:
        value = default_value

    # ---------------------------------------------------------
    # PLACEHOLDER DARI SINGLE TRANSACTION
    # ---------------------------------------------------------
    #
    # Karena single transaction hanya menyediakan sebagian kecil
    # fitur, beberapa nilai kosong dapat direpresentasikan sebagai
    # "0" atau "0.0".
    #
    # Ini bukan kategori baru. Ini adalah missing value.
    #

    if value in {
        "0",
        "0.0",
    }:
        known = set(encoder.classes_.astype(str))

        # Jika "0"/"0.0" memang merupakan kategori training,
        # pertahankan nilai tersebut.
        if value in known:
            return float(encoder.transform([value])[0])

        # Jika tidak pernah ada saat training, gunakan default
        # kategori training.
        value = default_value

    # ---------------------------------------------------------
    # VALIDATE AGAINST TRAINING CATEGORIES
    # ---------------------------------------------------------

    known = set(encoder.classes_.astype(str))

    if value not in known:
        raise ValueError(f"Kategori {value!r} tidak ada pada data training.")

    return float(encoder.transform([value])[0])


def preprocess_single_transaction(
    amount: float,
    product_code: str,
    card_type: str,
    email_domain: str,
    transaction_hour: int,
):
    """
    Convert the small web-form input into the same 444-feature
    numeric representation expected by the existing model.

    Features not supplied by the form use the training scaler mean.
    This keeps their scaled value near zero instead of injecting
    arbitrary values into the model.
    """

    (
        scaler,
        feature_names,
        encoders,
        categorical_defaults,
    ) = _load_preprocessing()

    if amount is None or not np.isfinite(
        float(amount)
    ):
        raise ValueError(
            "Transaction amount tidak valid."
        )

    transaction_hour = int(transaction_hour)

    if not 0 <= transaction_hour <= 23:
        raise ValueError(
            "Transaction hour harus berada pada 0-23."
        )

    transaction = pd.DataFrame(
        [
            {
                "TransactionDT": np.nan,
                "TransactionAmt": float(amount),
                "ProductCD": (
                    str(product_code).strip().upper()
                    if product_code is not None
                    else np.nan
                ),
                "card4": (
                    str(card_type).strip().lower()
                    if card_type is not None
                    else np.nan
                ),
                "P_emaildomain": (
                    str(email_domain).strip().lower()
                    if email_domain is not None
                    else np.nan
                ),
                "R_emaildomain": np.nan,
            }
        ]
    )

    transaction = create_features(
        transaction
    )

    if "transaction_hour" in transaction.columns:
        transaction["transaction_hour"] = (
            transaction_hour
        )

    if "is_night_transaction" in transaction.columns:
        transaction["is_night_transaction"] = int(
            transaction_hour <= 5
            or transaction_hour >= 23
        )

    if "TransactionID" in transaction.columns:
        transaction = transaction.drop(
            columns=["TransactionID"]
        )

    # Do not use hand-written category lists. Use the exact encoders
    # produced from the training dataset.
    for col in encoders:
        if col not in transaction.columns:
            continue

        default = categorical_defaults.get(
            col,
            str(encoders[col].classes_[0]),
        )

        transaction[col] = transaction[col].map(
            lambda value: _encode_category(
                value,
                encoders[col],
                default,
            )
        )

    # Exact model schema.
    aligned = pd.DataFrame(
        index=transaction.index,
        columns=feature_names,
        dtype=float,
    )

    for feature in feature_names:
        if feature not in transaction.columns:
            continue

        value = transaction.iloc[
            0
        ][feature]

        numeric_value = pd.to_numeric(
            pd.Series([value]),
            errors="coerce",
        ).iloc[0]

        if pd.notna(numeric_value):
            aligned.loc[
                aligned.index[0],
                feature,
            ] = float(numeric_value)

    # Features not available in the form are deliberately neutralized
    # using the exact scaler training mean. After StandardScaler this
    # becomes approximately zero.
    for index, feature in enumerate(
        feature_names
    ):
        if pd.isna(
            aligned.iloc[0, index]
        ):
            aligned.iloc[
                0,
                index,
            ] = scaler.mean_[index]

    aligned = aligned.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    for index in range(
        len(feature_names)
    ):
        if pd.isna(
            aligned.iloc[0, index]
        ):
            aligned.iloc[
                0,
                index,
            ] = scaler.mean_[index]

    data_scaled = scaler.transform(
        aligned
    )

    if data_scaled.shape[1] != scaler.n_features_in_:
        raise ValueError(
            "Jumlah fitur single transaction harus "
            f"{scaler.n_features_in__}, tetapi mendapat "
            f"{data_scaled.shape[1]}."
        )

    if not np.isfinite(data_scaled).all():
        raise ValueError(
            "Single transaction menghasilkan nilai non-finite."
        )

    return data_scaled

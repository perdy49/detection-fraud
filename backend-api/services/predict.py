import pandas as pd
import joblib
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model

from services.feature_engineering import create_features


# =========================================================
# LOAD MODELS
# =========================================================

xgb_model = joblib.load(
    "model/xgb_model.pkl"
)

scaler = joblib.load(
    "model/scaler.pkl"
)

lstm_model = load_model(
    "model/lstm_model.keras"
)

feature_names = joblib.load(
    "model/feature_names.pkl"
)


# =========================================================
# SEQUENCE BUFFER
# =========================================================

# KHUSUS CSV / FULL TRANSACTION
# JANGAN DIGUNAKAN OLEH SINGLE TRANSACTION

csv_sequence_buffer = deque(maxlen=20)


# =========================================================
# CSV / FULL TRANSACTION PREDICTION
# =========================================================

def predict_transaction(data: list):

    expected_features = scaler.n_features_in_

    if len(data) != expected_features:
        raise ValueError(
            f"Jumlah fitur harus {expected_features}, "
            f"tetapi dapat {len(data)}"
        )

    data = np.array(
        data,
        dtype=np.float32
    ).reshape(1, -1)

    # Scaling CSV tetap sama
    data_scaled = scaler.transform(data)[0]

    csv_sequence_buffer.append(
        data_scaled
    )

    sequence = list(csv_sequence_buffer)

    while len(sequence) < 20:
        sequence.insert(
            0,
            np.zeros_like(data_scaled)
        )

    sequence = np.array(
        sequence,
        dtype=np.float32
    ).reshape(1, 20, -1)

    lstm_feature = lstm_model.predict(
        sequence,
        verbose=0
    )

    xgb_input = sequence[:, -1, :]

    hybrid_input = np.hstack((
        xgb_input,
        lstm_feature
    ))

    fraud_score = xgb_model.predict_proba(
        hybrid_input
    )[0][1]

    return float(fraud_score)


# =========================================================
# SINGLE TRANSACTION
# =========================================================

def predict_single_transaction(
    amount: float,
    product_code: str,
    card_type: str,
    email: str,
    transaction_time: str
):

    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    if not email or "@" not in email:
        raise ValueError(
            "Email tidak valid."
        )

    # -----------------------------------------------------
    # EMAIL DOMAIN
    # -----------------------------------------------------

    email_domain = (
        email
        .split("@")[-1]
        .strip()
        .lower()
    )

    # -----------------------------------------------------
    # TRANSACTION TIME
    # -----------------------------------------------------

    parsed_time = pd.Timestamp(
        transaction_time
    )

    # -----------------------------------------------------
    # BUILD BASIC TRANSACTION
    # -----------------------------------------------------

    transaction = pd.DataFrame([
        {
            "TransactionDT": np.nan,
            "TransactionAmt": amount,
            "ProductCD": product_code,
            "card4": card_type,
            "P_emaildomain": email_domain,

            # JANGAN membuat P dan R sama.
            # Kita tidak mengetahui R_emaildomain
            # dari form single.
            "R_emaildomain": np.nan,
        }
    ])

    # -----------------------------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------------------------

    transaction = create_features(
        transaction
    )

    # -----------------------------------------------------
    # SINGLE-SPECIFIC FEATURE OVERRIDE
    # -----------------------------------------------------
    #
    # Single transaction tidak mempunyai informasi
    # lengkap seperti dataset training.
    #
    # Karena itu jangan biarkan feature yang tidak diketahui
    # menghasilkan nilai ekstrem.
    # -----------------------------------------------------

    if "missing_count" in transaction.columns:

        missing_idx = feature_names.index(
            "missing_count"
        )

        transaction["missing_count"] = (
            scaler.mean_[missing_idx]
        )

    if "email_match" in transaction.columns:

        email_match_idx = feature_names.index(
            "email_match"
        )

        transaction["email_match"] = (
            scaler.mean_[email_match_idx]
        )

    # -----------------------------------------------------
    # ADD HOUR MANUALLY
    # -----------------------------------------------------

    transaction["transaction_hour"] = (
        parsed_time.hour
    )

    transaction["is_night_transaction"] = int(
        parsed_time.hour <= 5
        or parsed_time.hour >= 23
    )

    # -----------------------------------------------------
    # REMOVE ID
    # -----------------------------------------------------

    if "TransactionID" in transaction.columns:

        transaction = transaction.drop(
            columns=["TransactionID"]
        )

    # -----------------------------------------------------
    # ALIGN TO 444 FEATURES
    # -----------------------------------------------------

    aligned = pd.DataFrame(
        index=transaction.index,
        columns=feature_names,
        dtype=float
    )

    # -----------------------------------------------------
    # COPY AVAILABLE FEATURES
    # -----------------------------------------------------

    for feature in feature_names:

        if feature in transaction.columns:

            value = transaction.iloc[0][feature]

            numeric_value = pd.to_numeric(
                pd.Series([value]),
                errors="coerce"
            ).iloc[0]

            if pd.notna(numeric_value):

                aligned.loc[
                    aligned.index[0],
                    feature
                ] = float(numeric_value)

    # -----------------------------------------------------
    # HANDLE UNKNOWN FEATURES
    # -----------------------------------------------------
    #
    # Feature yang memang tidak tersedia pada single
    # menggunakan mean training sebagai nilai netral.
    # -----------------------------------------------------

    for i, feature in enumerate(feature_names):

        value = aligned.iloc[0, i]

        if pd.isna(value):

            aligned.iloc[0, i] = (
                scaler.mean_[i]
            )

    # -----------------------------------------------------
    # TRANSACTIONDT
    # -----------------------------------------------------

    if "TransactionDT" in feature_names:

        idx = feature_names.index(
            "TransactionDT"
        )

        aligned.iloc[0, idx] = (
            scaler.mean_[idx]
        )

    # -----------------------------------------------------
    # CLEAN NUMERIC VALUES
    # -----------------------------------------------------

    aligned = aligned.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # -----------------------------------------------------
    # FINAL FALLBACK
    # -----------------------------------------------------

    for i in range(len(feature_names)):

        if pd.isna(aligned.iloc[0, i]):

            aligned.iloc[0, i] = (
                scaler.mean_[i]
            )

    # -----------------------------------------------------
    # SCALE
    # -----------------------------------------------------

    data_scaled = scaler.transform(
        aligned
    )

    # -----------------------------------------------------
    # DEBUG EXTREME FEATURES
    # -----------------------------------------------------

    scaled_row = data_scaled[0]

    print(
        "\n========== SINGLE FEATURES =========="
    )

    print(
        f"Feature count : {data_scaled.shape[1]}"
    )

    print(
        "\nExtreme features:"
    )

    for i in np.argsort(
        np.abs(scaled_row)
    )[-15:][::-1]:

        print(
            f"{feature_names[i]:30s} "
            f"scaled={scaled_row[i]:12.4f}"
        )

    print(
        "======================================\n"
    )

    # -----------------------------------------------------
    # VALIDATE 444 FEATURES
    # -----------------------------------------------------

    expected_features = (
        scaler.n_features_in_
    )

    if data_scaled.shape[1] != expected_features:

        raise ValueError(
            f"Jumlah fitur hasil preprocessing harus "
            f"{expected_features}, tetapi mendapat "
            f"{data_scaled.shape[1]}"
        )

    # -----------------------------------------------------
    # SINGLE TRANSACTION SEQUENCE
    # -----------------------------------------------------
    #
    # TIDAK menggunakan csv_sequence_buffer.
    #
    # Single transaction tetap berdiri sendiri.
    # -----------------------------------------------------

    current_transaction = (
        data_scaled[0]
    )

    sequence = [
        np.zeros_like(
            current_transaction
        )
        for _ in range(19)
    ]

    sequence.append(
        current_transaction
    )

    sequence = np.array(
        sequence,
        dtype=np.float32
    ).reshape(
        1,
        20,
        -1
    )

    # -----------------------------------------------------
    # LSTM
    # -----------------------------------------------------

    lstm_feature = lstm_model.predict(
        sequence,
        verbose=0
    )

    # -----------------------------------------------------
    # XGBOOST
    # -----------------------------------------------------

    xgb_input = (
        sequence[:, -1, :]
    )

    hybrid_input = np.hstack((
        xgb_input,
        lstm_feature
    ))

    fraud_probability = (
        xgb_model.predict_proba(
            hybrid_input
        )[0]
    )

    fraud_score = float(
        fraud_probability[1]
    )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    print(
        "\n========== SINGLE PREDICTION =========="
    )

    print("Input:")
    print(f"  Amount       : {amount}")
    print(f"  Product Code : {product_code}")
    print(f"  Card Type    : {card_type}")
    print(f"  Email        : {email}")
    print(f"  Time         : {transaction_time}")

    print("\nPreprocessed:")
    print(
        f"  Shape : {data_scaled.shape}"
    )

    print("\nScaled statistics:")
    print(
        f"  Min  : {data_scaled.min():.6f}"
    )

    print(
        f"  Max  : {data_scaled.max():.6f}"
    )

    print(
        f"  Mean : {data_scaled.mean():.6f}"
    )

    print("\nSequence:")
    print(
        f"  Shape : {sequence.shape}"
    )

    print("\nXGBoost probability:")
    print(
        f"  SAFE  : {fraud_probability[0]:.6f}"
    )

    print(
        f"  FRAUD : {fraud_probability[1]:.6f}"
    )

    print(
        f"\nFinal fraud score: {fraud_score:.6f}"
    )

    print(
        "========================================\n"
    )

    return fraud_score
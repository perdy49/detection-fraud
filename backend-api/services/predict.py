import pandas as pd
import joblib
import numpy as np

from collections import deque

from tensorflow.keras.models import load_model

from services.preprocess_single import (
    preprocess_single_transaction
)


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
# CSV SEQUENCE BUFFER
# =========================================================
#
# KHUSUS CSV / FULL TRANSACTION
#
# SINGLE TRANSACTION TIDAK MENGGUNAKAN BUFFER INI.
# =========================================================

csv_sequence_buffer = deque(
    maxlen=20
)


# =========================================================
# CSV / FULL TRANSACTION
# =========================================================

def predict_transaction(
    data: list
):

    expected_features = (
        scaler.n_features_in_
    )

    if len(data) != expected_features:

        raise ValueError(
            f"Jumlah fitur harus "
            f"{expected_features}, "
            f"tetapi dapat {len(data)}"
        )

    data = np.array(
        data,
        dtype=np.float32
    ).reshape(
        1,
        -1
    )

    # -----------------------------------------------------
    # SCALING
    # -----------------------------------------------------

    data_scaled = scaler.transform(
        data
    )[0]

    # -----------------------------------------------------
    # BUFFER
    # -----------------------------------------------------

    csv_sequence_buffer.append(
        data_scaled
    )

    sequence = list(
        csv_sequence_buffer
    )

    while len(sequence) < 20:

        sequence.insert(
            0,
            np.zeros_like(
                data_scaled
            )
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

    lstm_feature = (
        lstm_model.predict(
            sequence,
            verbose=0
        )
    )

    # -----------------------------------------------------
    # XGBOOST
    # -----------------------------------------------------

    xgb_input = (
        sequence[:, -1, :]
    )

    hybrid_input = np.hstack(
        (
            xgb_input,
            lstm_feature
        )
    )

    fraud_score = (
        xgb_model.predict_proba(
            hybrid_input
        )[0][1]
    )

    return float(
        fraud_score
    )


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
    # VALIDATE EMAIL
    # -----------------------------------------------------

    if (
        not email
        or "@"
        not in email
    ):

        raise ValueError(
            "Email tidak valid."
        )

    # -----------------------------------------------------
    # PARSE TIME
    # -----------------------------------------------------

    parsed_time = pd.Timestamp(
        transaction_time
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
    # SINGLE PREPROCESSING
    # -----------------------------------------------------

    data_scaled = (
        preprocess_single_transaction(
            amount=amount,
            product_code=product_code,
            card_type=card_type,
            email_domain=email_domain,
            transaction_hour=parsed_time.hour
        )
    )

    # -----------------------------------------------------
    # DEBUG FEATURES
    # -----------------------------------------------------

    scaled_row = (
        data_scaled[0]
    )

    print(
        "\n========== SINGLE FEATURES =========="
    )

    print(
        f"Feature count : "
        f"{data_scaled.shape[1]}"
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
    # VALIDATE 444
    # -----------------------------------------------------

    expected_features = (
        scaler.n_features_in_
    )

    if (
        data_scaled.shape[1]
        != expected_features
    ):

        raise ValueError(
            "Jumlah fitur hasil "
            "preprocessing harus "
            f"{expected_features}, "
            f"tetapi mendapat "
            f"{data_scaled.shape[1]}"
        )

    # -----------------------------------------------------
    # DETERMINE LSTM SEQUENCE LENGTH
    # -----------------------------------------------------
    #
    # Jangan hardcode sequence length berdasarkan
    # asumsi dokumentasi.
    #
    # Ambil langsung dari model LSTM.
    # -----------------------------------------------------

    lstm_input_shape = (
        lstm_model.input_shape
    )

    sequence_length = (
        lstm_input_shape[1]
    )

    if sequence_length is None:

        sequence_length = 20

    # -----------------------------------------------------
    # SINGLE SEQUENCE
    # -----------------------------------------------------

    current_transaction = (
        data_scaled[0]
    )

    sequence = [
        np.zeros_like(
            current_transaction
        )
        for _ in range(
            sequence_length - 1
        )
    ]

    sequence.append(
        current_transaction
    )

    sequence = np.array(
        sequence,
        dtype=np.float32
    ).reshape(
        1,
        sequence_length,
        -1
    )

    # -----------------------------------------------------
    # LSTM
    # -----------------------------------------------------

    lstm_feature = (
        lstm_model.predict(
            sequence,
            verbose=0
        )
    )

    # -----------------------------------------------------
    # XGBOOST
    # -----------------------------------------------------

    xgb_input = (
        sequence[:, -1, :]
    )

    hybrid_input = np.hstack(
        (
            xgb_input,
            lstm_feature
        )
    )

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

    print(
        f"  Amount       : {amount}"
    )

    print(
        f"  Product Code : {product_code}"
    )

    print(
        f"  Card Type    : {card_type}"
    )

    print(
        f"  Email        : {email}"
    )

    print(
        f"  Time         : {transaction_time}"
    )

    print(
        "\nPreprocessed:"
    )

    print(
        f"  Shape : {data_scaled.shape}"
    )

    print(
        "\nScaled statistics:"
    )

    print(
        f"  Min  : "
        f"{data_scaled.min():.6f}"
    )

    print(
        f"  Max  : "
        f"{data_scaled.max():.6f}"
    )

    print(
        f"  Mean : "
        f"{data_scaled.mean():.6f}"
    )

    print(
        "\nSequence:"
    )

    print(
        f"  Shape : {sequence.shape}"
    )

    print(
        "\nXGBoost probability:"
    )

    print(
        f"  SAFE  : "
        f"{fraud_probability[0]:.6f}"
    )

    print(
        f"  FRAUD : "
        f"{fraud_probability[1]:.6f}"
    )

    print(
        f"\nFinal fraud score: "
        f"{fraud_score:.6f}"
    )

    print(
        "========================================\n"
    )

    return fraud_score
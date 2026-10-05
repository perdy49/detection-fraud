import joblib
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model


# =========================
# LOAD MODELS
# =========================
xgb_model = joblib.load(
    "model/xgb_model.pkl"
)

scaler = joblib.load(
    "model/scaler.pkl"
)

lstm_model = load_model(
    "model/lstm_model.h5"
)


# =========================
# SEQUENCE BUFFER
# =========================
sequence_buffer = deque(maxlen=10)


def predict_transaction(data: list):

    # =========================
    # VALIDATE INPUT
    # =========================
    expected_features = scaler.n_features_in_

    if len(data) != expected_features:
        raise ValueError(
            f"Jumlah fitur harus {expected_features}, "
            f"tetapi dapat {len(data)}"
        )

    # =========================
    # CONVERT TO NUMPY
    # =========================
    data = np.array(
        data,
        dtype=np.float32
    ).reshape(1, -1)

    # =========================
    # SCALING
    # =========================
    data_scaled = scaler.transform(data)[0]

    # =========================
    # ADD TO BUFFER
    # =========================
    sequence_buffer.append(data_scaled)

    # =========================
    # BUILD SEQUENCE
    # =========================
    sequence = list(sequence_buffer)

    while len(sequence) < 10:
        sequence.insert(
            0,
            np.zeros_like(data_scaled)
        )

    sequence = np.array(
        sequence,
        dtype=np.float32
    ).reshape(1, 10, -1)

    # =========================
    # LSTM FEATURE
    # =========================
    lstm_feature = lstm_model.predict(
        sequence,
        verbose=0
    )

    # =========================
    # LAST STEP FEATURES
    # =========================
    xgb_input = sequence[:, -1, :]

    # =========================
    # HYBRID FEATURES
    # =========================
    hybrid_input = np.hstack((
        xgb_input,
        lstm_feature
    ))

    # =========================
    # XGBOOST PREDICTION
    # =========================
    fraud_score = xgb_model.predict_proba(
        hybrid_input
    )[0][1]

    return float(fraud_score)
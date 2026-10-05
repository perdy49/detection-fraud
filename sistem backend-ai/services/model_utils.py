import joblib
from tensorflow.keras.models import load_model


def load_hybrid_models():

    xgb_model = joblib.load(
        "model/xgb_model.pkl"
    )

    scaler = joblib.load(
        "model/scaler.pkl"
    )

    feature_names = joblib.load(
        "model/feature_names.pkl"
    )

    lstm_model = load_model(
        "model/lstm_model.keras"
    )

    return {
        "xgb_model": xgb_model,
        "scaler": scaler,
        "feature_names": feature_names,
        "lstm_model": lstm_model
    }
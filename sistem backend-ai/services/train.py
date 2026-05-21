import os
import sys
import time
import joblib
import numpy as np

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from xgboost import XGBClassifier

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE

from services.preprocess import preprocess_data
from services.sequence import create_sequences
from services.evaluate import evaluate_model


def train_model():

    # =========================
    # DATASET PATH
    # =========================
    transaction_path = "data/train_transaction.csv"
    identity_path = "data/train_identity.csv"

    # =========================
    # PREPROCESS
    # =========================
    X, y, scaler, feature_names = preprocess_data(
        transaction_path=transaction_path,
        identity_path=identity_path,
        is_training=True
    )

    print("Shape X:", X.shape)
    print("Shape y:", y.shape)

    # =========================
    # CREATE SEQUENCE
    # =========================
    X_seq, y_seq = create_sequences(
        X,
        y.values,
        sequence_length=10
    )

    print("Shape X_seq:", X_seq.shape)
    print("Shape y_seq:", y_seq.shape)

    # =========================
    # TRAIN TEST SPLIT
    # =========================
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq,
        y_seq,
        test_size=0.2,
        random_state=42,
        stratify=y_seq
    )

    # =========================
    # LSTM MODEL
    # =========================
    lstm_model = Sequential()

    lstm_model.add(
        Input(
            shape=(
                X_train.shape[1],
                X_train.shape[2]
            )
        )
    )

    lstm_model.add(
        LSTM(32)
    )

    lstm_model.add(
        Dropout(0.2)
    )

    lstm_model.add(
        Dense(16, activation="relu")
    )

    lstm_model.add(
        Dense(1, activation="sigmoid")
    )

    # =========================
    # COMPILE
    # =========================
    lstm_model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    # =========================
    # EARLY STOPPING
    # =========================
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=2,
        restore_best_weights=True
    )

    # =========================
    # TRAIN LSTM
    # =========================
    lstm_model.fit(
        X_train,
        y_train,
        validation_split=0.1,
        epochs=10,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )

    # =========================
    # LSTM FEATURE EXTRACTION
    # =========================
    lstm_train_features = lstm_model.predict(
        X_train,
        verbose=0
    )

    lstm_test_features = lstm_model.predict(
        X_test,
        verbose=0
    )

    # =========================
    # LAST STEP FEATURES
    # =========================
    X_train_flat = X_train[:, -1, :]
    X_test_flat = X_test[:, -1, :]

    # =========================
    # HYBRID FEATURES
    # =========================
    X_train_hybrid = np.hstack((
        X_train_flat,
        lstm_train_features
    ))

    X_test_hybrid = np.hstack((
        X_test_flat,
        lstm_test_features
    ))

    # =========================
    # SMOTE (ONLY TRAIN)
    # =========================
    smote = SMOTE(random_state=42)

    X_train_hybrid, y_train = smote.fit_resample(
        X_train_hybrid,
        y_train
    )

    # =========================
    # XGBOOST MODEL
    # =========================
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42
    )

    # =========================
    # TRAIN XGBOOST
    # =========================
    xgb_model.fit(
        X_train_hybrid,
        y_train
    )

    # =========================
    # LATENCY TEST
    # =========================
    start_time = time.time()

    predictions = xgb_model.predict(
        X_test_hybrid
    )

    prediction_probs = xgb_model.predict_proba(
        X_test_hybrid
    )[:, 1]

    end_time = time.time()

    latency = (
        (end_time - start_time) /
        len(X_test_hybrid)
    )

    print(f"Latency per transaction: {latency:.6f} sec")

    # =========================
    # EVALUATE
    # =========================
    evaluate_model(
        y_test,
        predictions,
        prediction_probs
    )

    # =========================
    # ACCURACY
    # =========================
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(f"Akurasi Hybrid Model: {accuracy:.4f}")

    # =========================
    # SAVE MODELS
    # =========================
    os.makedirs("model", exist_ok=True)

    joblib.dump(
        xgb_model,
        "model/xgb_model.pkl"
    )

    joblib.dump(
        scaler,
        "model/scaler.pkl"
    )

    lstm_model.save(
        "model/lstm_model.keras"
    )

    print("Training Hybrid XGBoost + LSTM selesai!")


if __name__ == "__main__":
    train_model()
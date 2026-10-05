import os


# =========================
# DATA PATH
# =========================
TRAIN_TRANSACTION_PATH = "data/train_transaction.csv"
TRAIN_IDENTITY_PATH = "data/train_identity.csv"

TEST_TRANSACTION_PATH = "data/test_transaction.csv"
TEST_IDENTITY_PATH = "data/test_identity.csv"

# =========================
# MODEL PATH
# =========================
MODEL_DIR = "model"

XGB_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgb_model.pkl"
)

LSTM_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "lstm_model.keras"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl"
)

FEATURE_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.pkl"
)

# =========================
# RESULTS
# =========================
RESULTS_DIR = "results"

# =========================
# MODEL SETTINGS
# =========================
SEQUENCE_LENGTH = 10

LSTM_UNITS = 32

BATCH_SIZE = 32

EPOCHS = 10

RANDOM_STATE = 42
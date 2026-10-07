from services.predict import (
    predict_transaction,
    predict_single_transaction,
    predict_transactions_batch,
)

FRAUD_THRESHOLD = 0.35


def predict_transaction_controller(
    features: list[float],
):
    score = predict_transaction(features)

    return {
        "fraud_score": score,
        "status": ("FRAUD" if score >= FRAUD_THRESHOLD else "SAFE"),
    }


def predict_file_controller(df):
    return predict_transactions_batch(df)


def predict_single_transaction_controller(
    amount: float,
    product_code: str,
    card_type: str,
    email: str,
    transaction_time: str,
):
    score = predict_single_transaction(
        amount=amount,
        product_code=product_code,
        card_type=card_type,
        email=email,
        transaction_time=transaction_time,
    )

    return {
        "fraud_score": score,
        "status": ("FRAUD" if score >= FRAUD_THRESHOLD else "SAFE"),
    }

from services.predict import predict_transaction


def predict_transaction_controller(features: list[float]):
    score = predict_transaction(features)

    return {
        "fraud_score": score,
        "status": "FRAUD" if score > 0.5 else "SAFE"
    }
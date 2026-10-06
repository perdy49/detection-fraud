from services.predict import (
    predict_transaction,
    predict_single_transaction,
    predict_transactions_batch
)


def predict_transaction_controller(features: list[float]):
    score = predict_transaction(features)

    return {
        "fraud_score": score,
        "status": "FRAUD" if score > 0.5 else "SAFE"
    }
    
def predict_file_controller(df):
    results = predict_transactions_batch(df)

    # return {
    #     "total_transactions": len(results),
    #     "fraud_count": sum(
    #         1 for result in results
    #         if result["status"] == "FRAUD"
    #     ),
    #     "safe_count": sum(
    #         1 for result in results
    #         if result["status"] == "SAFE"
    #     ),
    #     "results": results
    # }


def predict_single_transaction_controller(
    amount: float,
    product_code: str,
    card_type: str,
    email: str,
    transaction_time: str
):
    score = predict_single_transaction(
        amount=amount,
        product_code=product_code,
        card_type=card_type,
        email=email,
        transaction_time=transaction_time
    )

    return {
        "fraud_score": score,
        "status": "FRAUD" if score > 0.5 else "SAFE"
    }
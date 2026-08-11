from fastapi import FastAPI, HTTPException

from schemas.transaction_schema import TransactionSchema
from services.predict import predict_transaction


app = FastAPI(
    title="Hybrid Fraud Detection API",
    description="XGBoost + LSTM Hybrid Fraud Detection",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API Running"
    }


@app.post("/predict")
def predict(data: TransactionSchema):

    try:
        score = predict_transaction(
            data.features
        )

        return {
            "fraud_score": score,
            "status": "FRAUD" if score > 0.5 else "SAFE"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
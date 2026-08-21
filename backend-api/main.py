from fastapi import FastAPI

from routers.transaction_router import router as transaction_router


app = FastAPI(
    title="Hybrid Fraud Detection API",
    description="XGBoost + LSTM Hybrid Fraud Detection",
    version="1.0.0"
)


app.include_router(transaction_router)


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API Running"
    }
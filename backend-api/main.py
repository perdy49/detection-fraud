from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.transaction_router import router as transaction_router
from routers.csv_router import router as csv_router


app = FastAPI(
    title="Hybrid Fraud Detection API",
    description="XGBoost + LSTM Hybrid Fraud Detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction_router)
app.include_router(csv_router)


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API Running"
    }
from fastapi import APIRouter, HTTPException

from schemas.transaction_schema import TransactionSchema
from controllers.transaction_controller import (
    predict_transaction_controller
)


router = APIRouter(
    prefix="/api/transaction",
    tags=["Transaction Detection"]
)


@router.post("/predict")
def predict(data: TransactionSchema):

    try:
        return predict_transaction_controller(
            data.features
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
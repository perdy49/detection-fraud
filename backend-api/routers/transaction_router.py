from fastapi import APIRouter, HTTPException

from schemas.transaction_schema import (
    TransactionSchema,
    SingleTransactionSchema
)

from controllers.transaction_controller import (
    predict_transaction_controller,
    predict_single_transaction_controller
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


@router.post("/predict-single")
def predict_single(data: SingleTransactionSchema):

    try:
        return predict_single_transaction_controller(
            amount=data.amount,
            product_code=data.product_code,
            card_type=data.card_type,
            email=data.email,
            transaction_time=data.transaction_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
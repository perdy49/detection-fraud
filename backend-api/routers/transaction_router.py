from fastapi import APIRouter, HTTPException, UploadFile, File
import io
import pandas as pd

from schemas.transaction_schema import (
    TransactionSchema,
    SingleTransactionSchema
)

from controllers.transaction_controller import (
    predict_transaction_controller,
    predict_single_transaction_controller,
    predict_file_controller
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
        
@router.post("/predict-file")
async def predict_file(
    file: UploadFile = File(...)
):

    try:
        # -------------------------------------------------
        # VALIDATE FILE
        # -------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File tidak memiliki nama."
            )

        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="File harus berformat CSV."
            )

        # -------------------------------------------------
        # READ CSV
        # -------------------------------------------------

        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="File CSV kosong."
            )

        df = pd.read_csv(
            io.BytesIO(file_content)
        )

        # -------------------------------------------------
        # VALIDATE DATA
        # -------------------------------------------------

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="CSV tidak memiliki transaksi."
            )

        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        return predict_file_controller(
            df
        )

    except HTTPException:
        raise

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
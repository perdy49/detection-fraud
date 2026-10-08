from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Query,
)
import io
import pandas as pd

from services.history_service import (
    get_transaction_history,
    delete_transaction_history,
    save_transaction_history,
)

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


@router.post("/history")
def save_history(
    amount: float,
    fraud_score: float,
    status: str,
    transaction_time: str,
):
    try:
        history_record = save_transaction_history(
            amount=amount,
            fraud_score=fraud_score,
            status=status,
            transaction_time=transaction_time,
        )

        return {
            "message": "Transaction history saved successfully.",
            "data": history_record,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/history")
def get_history(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    try:
        history = get_transaction_history(
            search=search,
            status=status,
        )

        return {
            "total": len(history),
            "data": history,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/history/{transaction_id}")
def delete_history(transaction_id: str):
    try:
        deleted = delete_transaction_history(transaction_id)

        if not deleted:
            raise HTTPException(
                status_code=404, detail="Transaction history not found."
            )

        return {
            "message": "Transaction history deleted.",
            "id": transaction_id,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

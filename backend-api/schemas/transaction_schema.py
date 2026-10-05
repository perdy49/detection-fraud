from pydantic import BaseModel, Field
from typing import List


class TransactionSchema(BaseModel):
    features: List[float] = Field(
        ...,
        description="Daftar fitur transaksi hasil preprocessing"
    )


class SingleTransactionSchema(BaseModel):
    amount: float = Field(..., gt=0)
    product_code: str
    card_type: str
    email: str
    transaction_time: str
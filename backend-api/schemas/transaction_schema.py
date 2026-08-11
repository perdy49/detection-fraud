from pydantic import BaseModel, Field
from typing import List


class TransactionSchema(BaseModel):
    features: List[float] = Field(
        ...,
        description="Daftar fitur transaksi hasil preprocessing"
    )
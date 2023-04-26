from datetime import datetime

from pydantic import BaseModel


class InstrumentCreate(BaseModel):
    # id: int
    instrument_name: str
    price: float
    currency_id: int
    quantity: int
    figi: str
    #date: datetime
    instrument_type_id: int
    account_id: int
    operation_type_id: int

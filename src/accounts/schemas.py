from pydantic import BaseModel

from datetime import datetime

from typing import Optional



class Account(BaseModel):
    # id: int
    account_name: str
    broker_name:str
    #date: datetime
    user_id: int

class UpdateAccount(BaseModel):
    account_name: Optional[str]
    broker_name:Optional[str]    


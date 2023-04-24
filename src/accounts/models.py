from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, ForeignKey
from models import user
from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from database import Base

metadata = MetaData()

account = Table(
    "account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("account_name", String, nullable=False), # имя счёта
    Column("broker_name", String, nullable=False), # имя брокера
    Column("date", TIMESTAMP, default=datetime.utcnow),
    Column("user_id", Integer, ForeignKey(user.c.id)), # id пользователя
    
)

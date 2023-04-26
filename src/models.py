from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Table, Column, Integer, String, Float, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from database import Base

from sqlalchemy.orm import relationship


metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False), # логин
    Column("username", String, nullable=False), # имя
    Column("registered_at", TIMESTAMP, default=datetime.utcnow), # время регистрации
    Column("role_id", Integer, ForeignKey(role.c.id)), # роль. На данный момент у всех одна роль - user
    Column("hashed_password", String, nullable=False), # хэшированный пароль
    Column("is_active", Boolean, default=True, nullable=False), # пользователь активен(не заблочен)
    Column("is_superuser", Boolean, default=True, nullable=False), # лучше true иначе недоступны crud для user
    Column("is_verified", Boolean, default=False, nullable=False),
)

# соответсвует таблицы user, без этой штуки аутентификация и авторизация работать не будут
class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True) 
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey(role.c.id))
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


account = Table(
    "account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("account_name", String, nullable=False), # имя счёта
    Column("broker_name", String, nullable=False), # имя брокера
    Column("date", TIMESTAMP(timezone=False), default=datetime.utcnow), # время регистрации счёта
    Column("user_id", Integer, ForeignKey(user.c.id)), # id пользователя
)

currency_type = Table(
    "currency_type",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('carrency_name', String, nullable=False, default="add name"), # наименование валюты
    Column('rate', Float, nullable=False, default='0.00'), # курс валюты
)

total_quantity_and_avg_price_instrument_account = Table(
    "total_quantity_and_avg_price_instrument_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('instrument_name', String, nullable=False),  # имя ценной бумаги
    Column('total_quantity', Integer, nullable=False), # общее количество
    Column('avg_price', Float, nullable=False), # средняя цена
    Column("currency_id", Integer, nullable=False), # id счёта
    Column("account_id", Integer, ForeignKey(account.c.id) , nullable=False), # id счёта
    Column("instrument_type_id", Integer, nullable=False) # id типа инструмента: акции, облигации и т д

)

instrument_type = Table(
    "instrument_type",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('instrument_type_name', String, nullable=False), # типы ценной бумаги: акции, облигациии, валюта и т д и т п.
)

operation_type = Table(
    "operation_type",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('operation_type_id', String, nullable=False), # Покупка или продажа
)


instrument = Table(
    "instrument",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('instrument_name', String, nullable=False), # имя инструмента
    Column('price', Float, nullable=False, default=0.00), # цена 1 шт.
    Column('currency_id', Integer, ForeignKey(currency_type.c.id) , nullable=False), # валюта 
    Column("quantity", Integer , nullable=False), # количество
    Column("figi", String, nullable=True), # тикер
    Column("date", TIMESTAMP), # дата операции
    Column("instrument_type_id", Integer, ForeignKey(instrument_type.c.id), nullable=False), # типы ценной бумаги: акции, облигациии, валюта и т д и т п.
    Column("account_id", Integer, ForeignKey(account.c.id) , nullable=False), # id счёта
    Column("operation_type_id", Integer, ForeignKey(operation_type.c.id) , nullable=False) # Покупка или продажа
)


    

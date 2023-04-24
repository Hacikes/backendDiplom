from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, ForeignKey

metadata = MetaData()

operation = Table(
    "operation",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("quantity", String), # количество
    Column("figi", String), # тикер
    Column("instrument_type", String, nullable=True),
    Column("date", TIMESTAMP),
    Column("type", String), # тип операции, например, выплата купонов
)

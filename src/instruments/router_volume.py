from ast import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select, insert, update, delete
from sqlalchemy.orm import selectinload
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_
import jsonify
from typing import Dict, Union, List

from database import get_async_session
from models import instrument, account, user, total_quantity_and_avg_price_instrument_account, currency_type, instrument_type
from instruments.schemas import InstrumentCreate

router = APIRouter(
    prefix="/intruments_volume",
    tags=["Intrument_volume"]
)


# Получение процента объёма для счёта по типу инструмента
@router.get("/{account_id}/percent_by_instrument_type", description="Получение процента объёма для счёта по типу инструмента. Использовать в диаграмме для счёта")
async def get_percent_for_instrument_type_for_account(account_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                instrument_type.c.instrument_type_name,
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity) / (
                    select(
                        func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity)
                    ).select_from(total_quantity_and_avg_price_instrument_account)
                    .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                    .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
                ) * 100.0
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .join(instrument_type, instrument_type.c.id == total_quantity_and_avg_price_instrument_account.c.instrument_type_id)
            .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
            .group_by(instrument_type.c.instrument_type_name)
        )
        result = await session.execute(query)
        percent_by_instrument_type = [{row[0]: row[1]} for row in result.all()]
        return {"percent_by_instrument_type": percent_by_instrument_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": e})
    

# Получение процента объёма для пользователя по всем счетам по типу инструмента
@router.get("/user/{user_id}/percent_by_instrument_type", description="Получение процента объёма для пользователя по всем счетам по типу инструмента. Использовать в диаграмме для пользователя")
async def get_percent_for_instrument_type_for_user(user_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.user_id == user_id)
            .group_by(account.c.id)
            .subquery()
        )
        
        query = (
            select(
                instrument_type.c.instrument_type_name,
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity) / func.max(subquery.c.total_value) * 100.0
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         #.join(instrument, instrument.c.id == total_quantity_and_avg_price_instrument_account.c.instrument_id)
                         .join(instrument_type, instrument_type.c.id == total_quantity_and_avg_price_instrument_account.c.instrument_type_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         .join(subquery, subquery.c.account_id == account.c.id)
                         )
            .where(account.c.user_id == user_id)
            .group_by(instrument_type.c.id, instrument_type.c.instrument_type_name)
        )
        
        result = await session.execute(query)
        percent_by_instrument_type = [{row[0]: row[1]} for row in result.all()]
        return {"percent_by_instrument_type": percent_by_instrument_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})
    

# Получение объёма инструмента для счёта
@router.get("/{account_id}/percent_by_instrument_name", description="Получение объёма инструмента для счёта. Использовать в диаграмме для счёта")
async def get_percent_for_instrument_name_for_account(account_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity)
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )
        result = await session.execute(query)
        total_amount_by_instrument_name = {row[0]: row[1] for row in result.all()}
        total_amount = sum(total_amount_by_instrument_name.values())
        percent_by_instrument_name = {name: (amount/total_amount)*100 for name, amount in total_amount_by_instrument_name.items()}
        return {"percent_by_instrument_name": percent_by_instrument_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": e})
    

# Получение объёма инструмента для пользователя    
@router.get("/user/{user_id}/percent_for_instrument_name_for_user", description="Получение объёма инструмента для пользователя. Использовать в диаграмме для пользователя")
async def get_percent_for_instrument_name_for_user(user_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.user_id == user_id)
            .group_by(account.c.id)
            .subquery()
        )

        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity).label('total_amount'),
                func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity) * 100 /
                (select(func.sum(currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity))
                 .select_from(total_quantity_and_avg_price_instrument_account
                              .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                              .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                              .join(user, user.c.id == account.c.user_id)
                              )
                 .where(user.c.id == user_id)
                 )
                .label('share')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(user, user.c.id == account.c.user_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         .join(subquery, subquery.c.account_id == account.c.id)
                         )
            .where(user.c.id == user_id)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )

        result = await session.execute(query)
        percent_for_instrument_name_for_account = [{row[0]: {'total_amount': row[1], 'share': row[2]}} for row in result.all()]
        return {"percent_for_instrument_name_for_account": percent_for_instrument_name_for_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})
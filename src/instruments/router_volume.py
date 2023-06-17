from ast import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select, insert, update, delete, case
from sqlalchemy.orm import selectinload
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_
import jsonify
from typing import Dict, Union, List, Tuple

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
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            )
            .where(account.c.id == account_id)
            .group_by(account.c.id)
            .subquery()
        )
        query = (
            select(
                instrument_type.c.instrument_type_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) / func.max(subquery.c.total_value) * 100.0
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                .join(instrument_type, instrument_type.c.id == total_quantity_and_avg_price_instrument_account.c.instrument_type_id)
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                .join(subquery, subquery.c.account_id == account.c.id)
            )
            .where(account.c.id == account_id)
            .group_by(instrument_type.c.id, instrument_type.c.instrument_type_name)
        )
        result = await session.execute(query)
        percent_by_instrument_type = [{row[0]: row[1]} for row in result.all()]
        return {"percent_by_instrument_type": percent_by_instrument_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": e})
    

# Получение процента объёма для пользователя по всем счетам по типу инструмента
@router.get("/{user_id}/percent_by_instrument_type_by_user",description="Получение процента объёма для пользователя по всем счетам по типу инструмента. Использовать в диаграмме для пользователя")
async def get_percent_for_instrument_type_for_user(user_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
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
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) / func.max(subquery.c.total_value) * 100.0
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
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
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.id == account_id)
            #.where(account.c.user_id == user_id)
            .group_by(account.c.id)
            .subquery()
        )

        query =(
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) * 100 /
                (
                    select(
                        func.sum(
                            case(
                                (
                                    total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                                    currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                                    ),
                                else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                            )
                        )
                    )
                    .select_from(total_quantity_and_avg_price_instrument_account
                                 .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                                 .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                                 #.join(user, user.c.id == account.c.user_id)
                                 )
                    #.where(user.c.id == user_id)
                    .where(account.c.id == account_id)
                ).label('share')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         #.join(user, user.c.id == account.c.user_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         .join(subquery, subquery.c.account_id == account.c.id)
                         )
            #.where(user.c.id == user_id)
            .where(account.c.id == account_id)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )
    #     result = await session.execute(query)
    #     total_amount_by_instrument_name = {row[0]: row[1] for row in result.all()}
    #     total_amount = sum(total_amount_by_instrument_name.values())
    #     percent_by_instrument_name = {name: (amount/total_amount)*100 for name, amount in total_amount_by_instrument_name.items()}
    #     return {"percent_by_instrument_name": percent_by_instrument_name}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": e})
        result = await session.execute(query)
        percent_for_instrument_name_for_account = [{row[0]: {'total_amount': row[1], 'share': row[2]}} for row in result.all()]
        return {"percent_for_instrument_name_for_account": percent_for_instrument_name_for_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})
    

# Получение объёма инструмента для пользователя    
@router.get("/user/{user_id}/percent_for_instrument_name_for_user", description="Получение объёма инструмента для пользователя. Использовать в диаграмме для пользователя")
async def get_percent_for_instrument_name_for_user(user_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.user_id == user_id)
            .group_by(account.c.id)
            .subquery()
        )

        query =(
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) * 100 /
                (
                    select(
                        func.sum(
                            case(
                                (
                                    total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                                    currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                                    ),
                                else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                            )
                        )
                    )
                    .select_from(total_quantity_and_avg_price_instrument_account
                                 .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                                 .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                                 .join(user, user.c.id == account.c.user_id))
                    .where(user.c.id == user_id)
                ).label('share')
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
        return {"percent_for_instrument_name_for_user": percent_for_instrument_name_for_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})

# Получение доли валюты во всех инструментах для счёта, для круговой диаграммы
@router.get("/{account_id}/percent_currency_on_all_instruments_by_account", description="Получение доли каждой валюты во всех инструментах для счёта")
async def get_percent_currency_on_all_instruments(account_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                currency_type.c.carrency_name,
                func.sum(
                    case(
                        
                            (
                                total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                                total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                            ),
                        
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ) / (
                    select(
                        func.sum(
                            case(
                                
                                    (
                                        total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                                        total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                                    ),
                                
                                else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                            ) / 100
                        )
                    )
                    .select_from(
                        total_quantity_and_avg_price_instrument_account
                        .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                        .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                    )
                    .where(account.c.id == account_id)
                ).label('share')
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            )
            .where(account.c.id == account_id)
            .group_by(currency_type.c.carrency_name)
        )
        result = await session.execute(query)
        # percent_currency_on_all_instruments = result.fetchall()
        # json_str = json.dumps(percent_currency_on_all_instruments, default=str, ensure_ascii=False)
        # json_dict = json.loads(json_str)
        # return json.dumps(json_dict, ensure_ascii=False)

        percent_currency_on_all_instruments = [{str(row[0]): row[1]} for row in result.all()]
        return {"percent_currency_on_all_instruments": percent_currency_on_all_instruments}

    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })

# Получение доли валюты во всех инструментах для пользователя, для круговой диаграммы
@router.get("/{user_id}/percent_currency_on_all_instruments_by_user", description="Получение доли каждой валюты во всех инструментах для пользователя")
async def get_percent_currency_on_all_instruments(user_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                currency_type.c.carrency_name,
                func.sum(
                    case(
                        
                            (
                                total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                                total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                            ),
                        
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ) / (
                    select(
                        func.sum(
                            case(
                                
                                    (
                                        total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                                        total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                                    ),
                                
                                else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                            ) / 100
                        )
                    )
                    .select_from(
                        total_quantity_and_avg_price_instrument_account
                        .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                        .join(user, user.c.id == account.c.user_id)
                        .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                    )
                    .where(user.c.id == user_id)
                ).label('share')
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                .join(user, user.c.id == account.c.user_id)
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            )
            .where(user.c.id == user_id)
            .group_by(currency_type.c.carrency_name)
        )
        result = await session.execute(query)
        percent_currency_on_all_instruments = [{str(row[0]): row[1]} for row in result.all()]
        return {"percent_currency_on_all_instruments": percent_currency_on_all_instruments}

    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })

# Получение доли компаний для счёта, для круговой диаграммы
@router.get("/{account_id}/percent_of_companies_for_account", description="Получение доли компаний для счёта, для круговой диаграммы")
async def get_percent_of_companies_by_account(account_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                )
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.id == account_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_type_id == 1)
            .subquery()
        )

        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ) * 100 / subquery
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         #.join(user, user.c.id == account.c.user_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.id == account_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_type_id == 1)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )

        result = await session.execute(query)
        percent_of_companies_for_account1 = [{row[0]: {'total_amount': row[1], 'share': row[2]}} for row in result.all()]
        return {"percent_of_companies_for_account": percent_of_companies_for_account1}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})

# Получение доли компаний для пользователя, для круговой диаграммы
@router.get("/{user_id}/percent_of_companies_for_user", description="Получение доли компаний для пользователя, для круговой диаграммы")
async def get_percent_of_companies_by_user_id(user_id: int, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                )
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.user_id == user_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_type_id == 1)
            .subquery()
        )

        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                            total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                        ),
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                ) * 100 / subquery
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(user, user.c.id == account.c.user_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(user.c.id == user_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_type_id == 1)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )

        result = await session.execute(query)
        percent_of_companies_for_user1 = [{row[0]: {'total_amount': row[1], 'share': row[2]}} for row in result.all()]
        return {"percent_of_companies_for_user": percent_of_companies_for_user1}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})


# Получение доли одного инструмента по имени для счёте
@router.get("/{account_id}/percent_by_instrument_name_for_one_instrument", description="Получение объёма одного инструмента для счёта. Использовать на экране деталей инструментов")
async def get_percent_by_instrument_name_for_one_instrument(account_id: int, instrument_name: str, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.id == account_id)
            .group_by(account.c.id)
            .subquery()
        )

        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) * 100 /
                (
                    select(
                        func.sum(
                            case(
                                (
                                    total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                                    currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                                ),
                                else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                            )
                        )
                    )
                    .select_from(total_quantity_and_avg_price_instrument_account
                                 .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                                 .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                                 )
                    .where(account.c.id == account_id)
                    #.where(total_quantity_and_avg_price_instrument_account.c.instrument_name == instrument_name)
                ).label('share')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         .join(subquery, subquery.c.account_id == account.c.id)
                         )
            .where(account.c.id == account_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_name == instrument_name)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
        )

        result = await session.execute(query)
        percent_by_instrument_name_for_one_instrument = [
            {row[0]: {'total_amount': row[1], 'share': row[2]}} for row in result.all()
        ]
        return {"percent_by_instrument_name_for_one_instrument": percent_by_instrument_name_for_one_instrument}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})


# Получение доли одного инструмента по имени для пользователя    
@router.get("/user/{user_id}/percent_by_instrument_name_for_one_instrument_for_user", description="Получение доли одного инструмента по имени для пользователя . Использовать на экране деталей инструментов")
async def get_percent_by_instrument_name_for_one_instrument_for_user(user_id: int, instrument_name: str, session=Depends(get_async_session)):
    try:
        subquery = (
            select(
                account.c.id.label('account_id'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_value')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(account.c.user_id == user_id)
            .group_by(account.c.id)
            .subquery()
        )

        query =(
            select(
                total_quantity_and_avg_price_instrument_account.c.instrument_name, 
                total_quantity_and_avg_price_instrument_account.c.currency_id,
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ).label('total_amount'),
                func.sum(
                    case(
                        (
                            total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                            currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                        ),
                        else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                    )
                ) * 100 /
                (
                    select(
                        func.sum(
                            case(
                                (
                                    total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(['RUB', 'EUR', 'USD', 'HKD', 'CHY']),
                                    currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.total_quantity
                                    ),
                                else_=currency_type.c.rate * total_quantity_and_avg_price_instrument_account.c.avg_price * total_quantity_and_avg_price_instrument_account.c.total_quantity
                            )
                        )
                    )
                    .select_from(total_quantity_and_avg_price_instrument_account
                                 .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                                 .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                                 .join(user, user.c.id == account.c.user_id))
                    .where(user.c.id == user_id)
                ).label('share')
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
                         .join(user, user.c.id == account.c.user_id)
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         .join(subquery, subquery.c.account_id == account.c.id)
                         )
            .where(user.c.id == user_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_name == instrument_name)
            .group_by(total_quantity_and_avg_price_instrument_account.c.instrument_name)
            .group_by(total_quantity_and_avg_price_instrument_account.c.currency_id)
    )

        result = await session.execute(query)
        percent_by_instrument_name_for_one_instrument_for_user = [{row[0]: {'': row[1], 'total_amount': row[2], 'share': row[2]}} for row in result.all()]
        return {"percent_by_instrument_name_for_one_instrument_for_user": percent_by_instrument_name_for_one_instrument_for_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})
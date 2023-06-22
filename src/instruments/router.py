from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select, insert, update, delete, case
from sqlalchemy.orm import selectinload
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_

from database import get_async_session
from models import instrument, account, user, total_quantity_and_avg_price_instrument_account, currency_type, instrument_type, operation_type
from instruments.schemas import InstrumentCreate

router = APIRouter(
    prefix="/intruments",
    tags=["Intrument"]
)

# Вывод всех операций, со всех счетов пользователя
@router.get("/{id:int}", description="Вывод всех операций, со всех счетов пользователя")
async def get_operation_by_user_id(id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(instrument)
            .join(account, account.c.id == instrument.c.account_id)
            .join(user, user.c.id == account.c.user_id)
            .where(user.c.id == id)
        )
        result = await session.execute(query)
        operations_by_user = [{row[0]: {
            'instrument_name': row[1], 
            'price': row[2], 
            'currency': row[3], 
            'quantity': row[4], 
            'figi': row[5], 
            'date': row[6], 
            'instrument_type_id': row[7], 
            'account_id': row[8], 
            'operation_type_id': row[9]
            }
            } for row in result.all()]
        return {"all_operation_by_user": operations_by_user}
        # Закоменченная херня выше передаёт не в формате JSON, а как-то очень странно, но оставлю её на всякий случай
        # instruments = result.fetchall()
        # # print(instruments)
        # json_str = json.dumps(instruments, default=str, ensure_ascii=False)
        # # print(json_str)
        # json_dict = json.loads(json_str)
        # # print(json_dict)
        # return json.dumps(json_dict, ensure_ascii=False)
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })
    
    
# Вывод всех операций, что есть на счёте
@router.get("/{account_id}", description="Вывод всех операций, что есть на счёте")
async def get_operation_by_account_id(id: int,session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(instrument).where(instrument.c.account_id == id)
        result = await session.execute(query)
        operations_by_account = [{row[0]: {
            'instrument_name': row[1], 
            'price': row[2], 
            'currency': row[3], 
            'quantity': row[4], 
            'figi': row[5], 
            'date': row[6], 
            'instrument_type_id': row[7], 
            'account_id': row[8], 
            'operation_type_id': row[9]
            }
            } for row in result.all()]
        return {"all_operation_by_account": operations_by_account}
        # accounts = result.fetchall()
        # json_str = json.dumps(accounts, default=str)
        # json_dict = json.loads(json_str)
        # return json.dumps(json_dict, ensure_ascii=False)
    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })

# Добавление инструмента на конкретный счёт    
@router.post("/{id}", description="Добавление инструмента на конкретный счёт ")
async def add_instrument(new_instrument: InstrumentCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = insert(instrument).values(**new_instrument.dict())
        await session.execute(stmt)
        await session.commit()
        return {"status": "success"}
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })
    
# Удаление инструмента со счёта     
@router.delete('/{id}', description="Удаление инструмента со счёта ")
async def delete_instrument_by_account_id(id: int,  session: AsyncSession = Depends(get_async_session)):
    stmt = delete(instrument).where(instrument.c.id == id)
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}

# Получение информации о инструментах на счёте: об их количестве и средней цены, по каждой бумаге
@router.get("/total_instruments_by_account_id/{account_id}", description="Получение информации о инструментах на счёте: об их количестве и средней цены, по каждой бумаге")
async def get_total_instruments_by_account_id(account_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.id,
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                total_quantity_and_avg_price_instrument_account.c.total_quantity,
                total_quantity_and_avg_price_instrument_account.c.avg_price,
                total_quantity_and_avg_price_instrument_account.c.currency_id,
                currency_type.c.carrency_name,
                total_quantity_and_avg_price_instrument_account.c.account_id,
                total_quantity_and_avg_price_instrument_account.c.instrument_type_id,
                instrument_type.c.instrument_type_name
            )
            .select_from(
                total_quantity_and_avg_price_instrument_account
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                .join(instrument_type, instrument_type.c.id == total_quantity_and_avg_price_instrument_account.c.instrument_type_id)
            )
            .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
        )
        result = await session.execute(query)
        instruments_by_account = [
            {
                row[0]: {
                    'instrument_name': row[1],
                    'total_quantity': row[2],
                    'avg_price': row[3],
                    'currency_id': row[4],
                    'currency_name': row[5],
                    'account_id': row[6],
                    'instrument_type_id': row[7],
                    'instrument_type_name': row[8],
                }
            } for row in result.all()
        ]
        return {"instruments_by_account": instruments_by_account}
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })


# Получение информации о инструментах у пользователя: об их количестве и средней цены, по каждой бумаге
@router.get("/total/{id:int}", description="Получение информации о инструментах у пользователя: об их количестве и средней цены, по каждой бумаге")
async def get_total_intruments_by_user_id(id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(total_quantity_and_avg_price_instrument_account)
            .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
            .join(user, user.c.id == account.c.user_id)
            .where(user.c.id == id)
        )
        result = await session.execute(query)
        instruments_by_user = [{row[0]: {
            'instrument_name': row[1], 
            'quantity': row[2], 
            'avg_price': row[3], 
            'currency_id': row[4], 
            'account_id': row[5], 
            'instrument_type_id': row[6]
            }
            } for row in result.all()]
        return {"instruments_by_user": instruments_by_user}
        # instruments = result.fetchall()
        # # print(instruments)
        # json_str = json.dumps(instruments, default=str, ensure_ascii=False)
        # # print(json_str)
        # json_dict = json.loads(json_str)
        # # print(json_dict)
        # return json.dumps(json_dict, ensure_ascii=False)
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })

# Получение общего объёма денег в рублях со счёта по всем инструментам, включая валюту
@router.get("/{account_id}/total_volume_RUB", description="Получение общего объёма денег в рублях со счёта по всем инструментам, включая валюту")
async def get_total_volume_in_RUB(account_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                func.sum(
                    case(
                        
                        (total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                        total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate),
                        
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                )
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
            # .join(user, user.c.id == account.c.user_id)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .where(account.c.id == account_id)
        )
        result = await session.execute(query)
        total_volume_in_RUB = result.scalar()
        return total_volume_in_RUB
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })

# Получение общего объёма денег в рублях со всех счетов и по всем инструментам пользователя, включая валюту
@router.get("/{user_id}/total_volume_in_RUB", response_model=float, description="Получение общего объёма денег в рублях со всех счетов и по всем инструментам пользователя, включая валюту")
async def get_total_volume_in_RUB_by_user_id(user_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                func.sum(
                    case(
                        
                        (total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                        total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate),
                        
                        else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                    )
                )
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
            .join(user, user.c.id == account.c.user_id)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .where(user.c.id == user_id)
        )
        result = await session.execute(query)
        total_volume_in_RUB = result.scalar()
        return total_volume_in_RUB
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })


    
# Получение свободного кеша для счёта по всем валютам. Вывод в рублях
@router.get("/{account_id}/total_value_for_instrument_type_id", description="Получение свободного кеша для счёта по всем валютам. Вывод в рублях")
async def get_free_value_for_account(account_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.total_quantity
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_name == 'RUB')
        )
        result = await session.execute(query)
        total_value_for_instrument_type_id = result.scalar()
        return {"total_value_for_instrument_type_id": total_value_for_instrument_type_id}
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })
    
# Получение свободного кеша пользователя по всем счетам и валютам. Вывод в рублях
@router.get("/user/{user_id}/total_value_for_instrument_type_id", description="Получение свободного кеша пользователя по всем счетам и валютам. Вывод в рублях")
async def get_free_value_for_user(user_id: int, session=Depends(get_async_session)):
    try:
        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.total_quantity
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                .join(account).join(user)
                .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            )
            .where(user.c.id == user_id)
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_name == 'RUB')
        )
        result = await session.execute(query)
        total_value_for_instrument_type_id = result.scalar()
        return {"total_value_for_instrument_type_id": total_value_for_instrument_type_id}
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": e
        })


# Получения свободных денег в разных валютах для счёта
@router.get("/{account_id}/free_currency_for_account", description="Получения свободных денег в разных валютах для счёта")
async def get_free_currency_for_account(account_id: int, currency_name: str, session=Depends(get_async_session)):
    try:
        query = (
            select(
                total_quantity_and_avg_price_instrument_account.c.id,
                total_quantity_and_avg_price_instrument_account.c.instrument_name,
                total_quantity_and_avg_price_instrument_account.c.total_quantity,
                total_quantity_and_avg_price_instrument_account.c.avg_price,
                currency_type.c.carrency_name,
                total_quantity_and_avg_price_instrument_account.c.account_id
            )
            .select_from(total_quantity_and_avg_price_instrument_account
                         .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
                         )
            .where(total_quantity_and_avg_price_instrument_account.c.instrument_type_id == 3)
            .where(total_quantity_and_avg_price_instrument_account.c.account_id == account_id)
            .where(currency_type.c.carrency_name == currency_name)
        )
        result = await session.execute(query)
        free_currency_for_account = [{row[0]: {
            'instrument_name': row[1], 
            'total_quantity': row[2], 
            'avg_price': row[3], 
            'currency_name': row[4], 
            'account_id': row[5]
            }
            } for row in result.all()]
        return {"free_currency_for_account": free_currency_for_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "data": None, "details": str(e)})

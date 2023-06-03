from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete, func, case, or_
import json
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import account, instrument, user, total_quantity_and_avg_price_instrument_account, currency_type, instrument_type
from accounts.schemas import Account, UpdateAccount

router = APIRouter(
    prefix='/accounts',
    tags=['Account']
)


# @router.get("/")
# async def get_accounts(id: int ,session: AsyncSession = Depends(get_async_session)):
#     try:
#         query = select(account).where(account.c.user_id == id)
#         result = await session.execute(query)
#         accounts_by_user = [{row[0]: {
#             'account_name': row[1], 
#             'broker_name': row[2], 
#             'date': row[3], 
#             'user_id': row[4], 
#             }
#             } for row in result.all()]
#         return {"accounts_by_user": accounts_by_user}
#         # accounts = result.fetchall()
#         # json_str = json.dumps(accounts, default=str)
#         # json_dict = json.loads(json_str)
#         # return json.dumps(json_dict, ensure_ascii=False)
#     except Exception:
#         # Передать ошибку разработчикам
#         raise HTTPException(status_code=500, detail={
#             "status": "error",
#             "data": None,
#             "details": "User don't have account"
#         })


@router.get("/")
async def get_accounts(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(account).where(account.c.user_id == id)
        result = await session.execute(query)
        accounts_by_user = [
            {
                row[0]: {
                    'account_name': row[1],
                    'broker_name': row[2],
                    'date': row[3],
                    'user_id': row[4],
                    'total_volume_by_account_in_RUB': await get_total_volume_in_RUB(row[0], session) or 0
                }
            }
            for row in result.all()
        ]
        return {"accounts_by_user": accounts_by_user}
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "User doesn't have any accounts"
        })

async def get_total_volume_in_RUB(account_id: int, session: AsyncSession):
    try:
        query = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                total_quantity_and_avg_price_instrument_account.c.instrument_name.in_(["RUB", "EUR", "USD", "HKD", "CHY"]),
                                total_quantity_and_avg_price_instrument_account.c.total_quantity * currency_type.c.rate
                            ),
                            else_=total_quantity_and_avg_price_instrument_account.c.total_quantity * total_quantity_and_avg_price_instrument_account.c.avg_price * currency_type.c.rate
                        )
                    ),
                    0  # Если результат равен null, устанавливаем значение 0
                )
            )
            .select_from(total_quantity_and_avg_price_instrument_account)
            .join(account, account.c.id == total_quantity_and_avg_price_instrument_account.c.account_id)
            .join(currency_type, currency_type.c.id == total_quantity_and_avg_price_instrument_account.c.currency_id)
            .where(account.c.id == account_id)
        )
        result = await session.execute(query)
        total_volume_in_RUB = result.scalar()
        return total_volume_in_RUB
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })




    
@router.post("/")
async def add_specific_operations(new_account: Account, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(account).values(**new_account.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}

@router.put('/{id}')
async def put_specific_operations(id: int, update_account: UpdateAccount, session: AsyncSession = Depends(get_async_session)):
    stmt = update(account).values(**update_account.dict()).where(account.c.id == id)
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}

# Delete account and his instruments
@router.delete('/{id}')
async def delete_specific_operations(id: int,  session: AsyncSession = Depends(get_async_session)):
    
    stmt2 = delete(instrument).where(instrument.c.account_id == id)
    stmt = delete(account).where(account.c.id == id)
    await session.execute(stmt2)
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}
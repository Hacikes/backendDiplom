from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
import json
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import account, instrument
from accounts.schemas import Account, UpdateAccount

router = APIRouter(
    prefix='/accounts',
    tags=['Account']
)

@router.get("/")
async def get_accounts(id: int ,session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(account).where(account.c.user_id == id)
        result = await session.execute(query)
        accounts = result.fetchall()
        json_str = json.dumps(accounts, default=str)
        json_dict = json.loads(json_str)
        return json.dumps(json_dict, ensure_ascii=False)
    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "User don't have account"
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
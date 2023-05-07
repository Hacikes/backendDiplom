from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
import json
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import user
from auth.schemas import ForgotPassword

router = APIRouter(
    prefix='/forgot_password',
    tags=['ForgotPassword']
)


@router.get("/")
async def forgot_password(email: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(user).where(user.c.email == email)
        result = await session.execute(query)
        user_by_id = result.fetchall()
        if not user_by_id:
            raise HTTPException(status_code=404, detail={
                "status": "error",
                "data": None,
                "details": "User not found"
            })
        # json_str = json.dumps(user_by_id, default=str)
        # json_dict = json.loads(json_str)
        return ('User found')
    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })




# Вроде правильно написанный роут, тот что выше я обычно писал для get запросов
# @router.post("/")
# async def forgot_password(forgot_password: ForgotPassword ,session: AsyncSession = Depends(get_async_session)):
#     stmt = insert(account).values(**new_account.dict())
#     await session.execute(stmt)
#     await session.commit()
#     return {"status": "success"}


        # Создание кода сброса и сохранение его в дб
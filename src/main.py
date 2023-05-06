from fastapi import FastAPI

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate, UserUpdate
from accounts.router import router as router_account
from instruments.router import router as router_operation
from instruments.router_volume import router as router_volume

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
""" CORS политики мать его """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    secure = False,
    SameSite=None
)

app = FastAPI(
    title="Investing App"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/user",
    tags=["User"],
)

# Berrar auth Routers
from auth.base_config_berrar import auth_backend_berrar, fastapi_users_berrar
app.include_router(
    fastapi_users_berrar.get_auth_router(auth_backend_berrar),
    prefix="/auth_berrar",
    tags=["Auth_berrar"],
)

app.include_router(
    fastapi_users_berrar.get_register_router(UserRead, UserCreate),
    prefix="/auth_berrar",
    tags=["Auth_berrar"],
)

app.include_router(
    fastapi_users_berrar.get_users_router(UserRead, UserUpdate),
    prefix="/user_berrar",
    tags=["User_berrar"],
)

app.include_router(router_account)
app.include_router(router_operation)
app.include_router(router_volume)

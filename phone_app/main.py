import fastapi
from phone_app.db.database import SessionLocal
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from phone_app.api import user, phone
from starlette.middleware.sessions import SessionMiddleware
from phone_app.config import SECRET_KEY
import uvicorn


async def init_redis():
    return redis.from_url('redis://localhost', encoding='utf-8', decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await  FastAPILimiter.init(redis)
    yield
    await  redis.aclose()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




phone_fast = fastapi.FastAPI(title='Phone site', lifespan=lifespan)


phone_fast.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")


phone_fast.include_router(phone.phone_router)
phone_fast.include_router(user.auth_router)



if __name__ == "__main__":
    uvicorn.run(phone_fast, host="127.0.0.1", port=8000)

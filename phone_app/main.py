from fastapi import FastAPI, HTTPException
from phone_app.api import phone
import redis.asyncio as redis
from contextlib import asynccontextmanager
from phone_app.db.database import SessionLocal
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
import uvicorn
from phone_app.api import auth, phone, user_profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await init_redis()
    await FastAPILimiter.init(redis_client)
    yield
    await redis_client.close()

delivery_app = FastAPI(title="Phone_FAST", lifespan=lifespan)


delivery_app.include_router(phone.phone_router)
delivery_app.include_router(auth.auth_router)
delivery_app.include_router(user_profile.user_router)


async def init_redis():
    return redis.from_url('redis://localhost', encoding='utf-8', decode_responses=True)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(delivery_app, host="127.0.0.1", port=8000)

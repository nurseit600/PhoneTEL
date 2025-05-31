from phone_app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from starlette.requests import Request
from fastapi_limiter.depends import RateLimiter
from phone_app.db.database import SessionLocal
from typing import Optional, List
from phone_app.db.schema import UserSchema, UserLoginSchema
from phone_app.db.models import User, RefreshToken, PhoneFeatures
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session


auth_router = APIRouter(prefix='/auth', tags=['Auth'])


oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')
password_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_password(plain_password, hash_password):
    return password_context.verify(plain_password, hash_password)


def get_password_hash(password):
    return password_context.hash(password)


@auth_router.post('/register/')
async def register(user: UserSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == user.username).first()
    email_db = db.query(User).filter(User.email == user.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail='Username бар экен')
    elif email_db:
        raise HTTPException(status_code=400, detail='Email бар экен')

    new_hash_pass = get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=new_hash_pass
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": 'User registered successfully'}


@auth_router.post("/login/", dependencies=[Depends(RateLimiter(times=3, seconds=200))])
async def login(from_date: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == from_date.username).first()
    if not user or not verify_password(from_date.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    token_db = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(token_db)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/logout")
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    db.delete(token)
    db.commit()

    return {"message": "Logged out successfully"}


@auth_router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": token_entry.user.email})
    return {"access_token": new_access_token, "token_type": "bearer"}
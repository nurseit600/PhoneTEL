from phone_app.db.models import User
from phone_app.db.schema import UserSchema
from phone_app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from typing import List


user_router = APIRouter(prefix='/user', tags=['User'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.get('/', response_model=List[UserSchema])
async def user_list(db: Session = Depends(get_db)):
    return db.query(User).all()


@user_router.get('/{user_id}', response_model=UserSchema)
async def user_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id). first()
    if user is None:
        raise HTTPException(status_code=400, detail='User not found')
    return user


@user_router.put('/{user_id}',  response_model=UserSchema)
async def user_update(user_id: int, user: UserSchema, db: Session = Depends(get_db)):

    user_db = db.query(User).filter(User.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=400, detail='User not found')

    user_db.user_name = User(**user.dict())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.delete('/{user_id}')
async def user_delete(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=400, detail='User not found')

    db.delete(user_db)
    db.commit()
    return {'message': 'This category is deleted'}
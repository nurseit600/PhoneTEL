from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
from phone_app.db.models import PhoneFeatures
from phone_app.db.schema import PhoneFeaturesSchema
from phone_app.db.database import SessionLocal
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


phone_router = APIRouter(prefix='/phone', tags=['PhoneFeatures'])

BASE_DIR = Path(__file__).resolve().parent.parent.parent

model_path = BASE_DIR / 'phone_price_job.pkl'
scaler_path = BASE_DIR / 'scaler (1).pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@phone_router.post('/', response_model=PhoneFeaturesSchema)
async def create_phone(phone: PhoneFeaturesSchema, db: Session = Depends(get_db)):
    db_phone = PhoneFeatures(**phone.dict())
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone


@phone_router.get('/', response_model=List[PhoneFeaturesSchema])
async def phone_list(db: Session = Depends(get_db)):
    return db.query(PhoneFeatures).all()


@phone_router.get('/{phone_id}', response_model=PhoneFeaturesSchema)
async def phone_detail(phone_id: int, db: Session = Depends(get_db)):
    phone = db.query(PhoneFeatures).filter(PhoneFeatures.id == phone_id).first()
    if phone is None:
        raise HTTPException(status_code=404, detail='phone not found')
    return phone


@phone_router.put('/{phone_id}', response_model=PhoneFeaturesSchema)
async def phone_update(phone_id: int, phone: PhoneFeaturesSchema, db: Session = Depends(get_db)):
    phone_db = db.query(PhoneFeatures).filter(PhoneFeatures.id == phone_id).first()
    if phone_db is None:
        raise HTTPException(status_code=404, detail='phone not found')

    for field, value in phone.dict().items():
        setattr(phone_db, field, value)

    db.commit()
    db.refresh(phone_db)
    return phone_db


@phone_router.delete('/{phone_id}')
async def phone_delete(phone_id: int, db: Session = Depends(get_db)):
    phone_db = db.query(PhoneFeatures).filter(PhoneFeatures.id == phone_id).first()
    if phone_db is None:
        raise HTTPException(status_code=404, detail='phone not found')

    db.delete(phone_db)
    db.commit()
    return {'message': 'phone deleted successfully'}


model_columns = [
    'Rating',
    'Num_Ratings',
    'RAM',
    'ROM',
    'Battery',
    'Front_Cam'
]


@phone_router.post('/predict/')
async def predict_price(phone: PhoneFeaturesSchema, db: Session = Depends(get_db)):
    input_data = {
        'Rating': phone.rating,
        'Num_Ratings': phone.num_ratings,
        'RAM': phone.ram,
        'ROM': phone.rom,
        'Battery': phone.battery,
        'Front_Cam': phone.front_cam
    }
    input_df = pd.DataFrame([input_data])
    scaled_df = scaler.transform(input_df)
    predicted_price = model.predict(scaled_df)[0]
    print(model.predict(scaled_df))
    return {'predicted_price': round(predicted_price)}

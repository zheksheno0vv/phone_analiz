from phone_app.db.models import Phone
from phone_app.db.schema import PhoneSchema
from phone_app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import  Depends,HTTPException,APIRouter
from typing import Optional,List
from pathlib import Path
import joblib
import pandas as pd
import numpy  as np
from sklearn.preprocessing import  StandardScaler



phone_router = APIRouter(prefix='/phone',tags=['Phone'])
BASE_DIR = Path(__file__).resolve().parent.parent.parent

model_path = BASE_DIR / 'phone_price_model_job.pkl'
scaler_path = BASE_DIR /'scaler.pkl'


model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@phone_router.post('/create',response_model=PhoneSchema)
async def phone_create(phone:PhoneSchema,db:Session=Depends(get_db)):
    phone_db = Phone(**phone.dict())
    db.add(phone_db)
    db.commit()
    db.refresh(phone_db)
    return phone_db

@phone_router.get('/',response_model=List[PhoneSchema])
async def phone_list(db:Session = Depends(get_db)):
    return db.query(Phone).all()

@phone_router.get('/{phone_id}/',response_model=PhoneSchema)
async def phone_detail(phone_id:int,db:Session=Depends(get_db)):
    phone_db = db.query(Phone).filter(Phone.id == phone_id).first()


    if phone_db is  None:
        raise HTTPException(status_code=400,detail='мындай малымат жок')
    return phone_db


@phone_router.delete('/phone_id')
async def phone_delete(phone_id:int,db:
                       Session = Depends(get_db)):
    phone_db = db.query(Phone).filter(Phone.id == phone_id).first()


    if phone_db is None:
        raise HTTPException(status_code=400,detail='мындай малымат жок')


    db.delete(phone_db)
    db.commit()
    return {'message':'This House is deleted'}



model_columns =  [
    'ROM',
    'RAM',
    'Battery',
    'Rating',
    # 'Price_INR'
]

@phone_router.post('/predict/')
async def predict_price(phone: PhoneSchema, db: Session = Depends(get_db)):
    input_data = {

        'ROM': phone.ram,
        'RAM': phone.rom,
        'Battery': phone.battery,
        'Rating': phone.rating,
        # 'Price_INR': phone.price_inr

    }


    input_df = pd.DataFrame([input_data])
    scaled_df =scaler.transform(input_df)
    predicted_price =model.predict(scaled_df)[0]
    return {'predicted_price':round(predicted_price)}

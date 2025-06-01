from jose import jwt
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from fastapi_limiter.depends import RateLimiter
from phone_app.db.database import SessionLocal
from typing import Optional
from phone_app.db.schema import UserProfileSchema
from phone_app.db.models import UserProfile,RefreshToken
from fastapi import Depends,HTTPException,status,APIRouter
from sqlalchemy.orm import Session
from starlette.requests import Request
from phone_app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTE, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM, settings








auth_router = APIRouter(prefix='/auth',tags=['Auth'])




oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')
password_context = CryptContext(schemes=['bcrypt'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if  expires_delta else  timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE))
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def create_refresh_token(date: dict):
    return create_access_token(date,expires_delta=timedelta(days= REFRESH_TOKEN_EXPIRE_DAYS))


def verify_password(plan_password,hash_password):
    return password_context.verify(plan_password,hash_password)

def get_password_hash(password):
    return password_context.hash(password)


@auth_router.post('/login',dependencies =[Depends(RateLimiter(times=3,seconds=10))])
async def login(from_date:OAuth2PasswordRequestForm =Depends(),db:Session =Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == from_date.username).first()
    if not user or not verify_password(from_date.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Mалымат тура эмес')
    access_token = create_access_token({'sub':user.username})
    refresh_token =create_refresh_token({'sub':user.username})
    token_db = RefreshToken(token=refresh_token,user_id=user.id)
    db.add(token_db)
    db.commit()


    return {'access_token':access_token,'refresh_token':refresh_token,'token_type':'bearer'}




@auth_router.post('/logout/')
async def logout(refresh_token:str,db:Session = Depends(get_db)):


    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not  stored_token:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Mалымат тура эмес')
    db.delete(stored_token)
    db.commit()
    return {'massage':'Вышли'}


@auth_router.post('/register/')
async def register(user:UserProfileSchema,db:Session=Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username==user.username).first()
    if user_db:
        return  HTTPException(status_code=400,detail='username  bar ')
    new_hash_pash = get_password_hash(user.password)
    new_user = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone_number=user.phone_number,
        age=user.age,
        status=user.status,
        hashed_password=new_hash_pash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post('/refresh/')
def refresh(refresh_token:str,db:Session =Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Малымат тура эмес')
    access_token = create_refresh_token({'sub': token_entry.user.id})

    return {'access_token':access_token,'token_type':'bearer'}
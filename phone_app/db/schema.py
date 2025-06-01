from typing import Optional
from phone_app.db.models import StatusChoices
from pydantic import BaseModel
from datetime import datetime


class UserProfileSchema(BaseModel):
    id:int
    first_name:str
    last_name:str
    username:str
    password:str
    phone_number:Optional[str]
    profile_image:Optional[str]
    age:Optional[int]
    status:StatusChoices
    date_register:datetime

class PhoneSchema(BaseModel):
    id:int
    rom:int
    ram:int
    battery:int
    rating:float
    # price_inr: Optional[int] = None

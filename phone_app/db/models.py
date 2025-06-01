from phone_app.db.database import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Integer, String,Enum,DateTime,ForeignKey,Text,DECIMAL,Float
from typing import Optional,List
from enum import Enum as PyEnum
from passlib.hash import bcrypt
from datetime import datetime






class StatusChoices(str,PyEnum):
    client ='client'
    owner ='owner'

class UserProfile(Base):

    __tablename__= 'user_profile'

    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    first_name:Mapped[str] = mapped_column(String(32))
    last_name:Mapped[str] = mapped_column(String(32))
    username:Mapped[str] = mapped_column(String,unique=True)
    hashed_password: Mapped[str] = mapped_column(String,nullable=False)
    phone_number:Mapped[Optional[str]]=mapped_column(String,nullable=True)
    profile_image:Mapped[Optional[str]] = mapped_column(String,nullable=True)
    age :Mapped[Optional[int]] =mapped_column(Integer,nullable=True)
    status:Mapped[StatusChoices] =mapped_column(Enum(StatusChoices),default=StatusChoices.client)
    date_register: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow())

    def set_passwords(self,password:str):
        self.hashed_password = bcrypt.hash(password)

    def check_password(self,password:str):
        return bcrypt.verify(password,self.hashed_password)


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    token:Mapped[str]=mapped_column(String,unique=True,nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow())
    user_id:Mapped[int]=mapped_column(ForeignKey('user_profile.id'))
    user:Mapped['UserProfile'] =relationship('UserProfile',back_populates='token')


class Phone(Base):
    __tablename__ = 'phone'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rom: Mapped[int] = mapped_column(Integer)
    ram: Mapped[int] = mapped_column(Integer)
    battery: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)
    # price_inr: Mapped[Optional[int]] = mapped_column(Integer)

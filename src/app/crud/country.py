from sqlalchemy.orm import Session
from models import Member
from schemas import MemberCreate, MemberUpdate
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
import sys
sys.path.append(r'D:/API ENV/crud.py') 
import schemas,models
from pymysql.err import IntegrityError




def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return db_user

def get_country_info(db: Session, country_id: int):
    return db.query(models.Country_Info).filter(models.Country_Info.Country_Id == country_id).first()

def get_all_country_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Country_Info).offset(skip).limit(limit).all()

def update_country_info(db: Session, country_id: int, country_info: schemas.update_country):
    db_country_info = db.query(models.Country_Info).filter(models.Country_Info.Country_Id == country_id)
    if db_country_info:
        for attr, value in country_info.dict().items():
            setattr(db_country_info, attr, value)
        db.commit()
        db.refresh(db_country_info)
    return db_country_info
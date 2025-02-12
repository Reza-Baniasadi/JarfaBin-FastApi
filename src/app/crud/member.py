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

def get_member(db: Session, member_id: int):
    return db.query(Member).filter(Member.Member_id == member_id).first()

def get_members(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Member).offset(skip).limit(limit).all()
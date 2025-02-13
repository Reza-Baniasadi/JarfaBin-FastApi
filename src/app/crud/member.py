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

def update_member(db: Session, member_id: int, member_update: MemberUpdate):
    member = db.query(Member).filter(Member.Member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    update_data = member_update.dict(exclude_unset=True)
    db.query(Member).filter(Member.Member_id == member_id).update(update_data)
    db.commit()
    db.refresh(member)
    return  {"message":"Member updated Successfully"}


def delete_member(db: Session, member_id: int):
    member = db.query(models.Member).filter(models.Member.Member_id == member_id).first()
    if member:
        db.delete(member)
        db.commit()
        return  {"message":"Member deleted Successfully"}
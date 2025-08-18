from sqlalchemy.orm import Session
from fastapi import HTTPException
from pymysql.err import IntegrityError
from typing import List

from models import Member as DBMember, Country_Info as DBCountry
from schemas import MemberCreate as MemberSchema, MemberUpdate as CountryUpdateSchema


def add_member(db: Session, member_data: MemberSchema) -> DBMember:
    """Create a new member in the database."""
    new_member = DBMember(**member_data.dict())
    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return new_member


def fetch_country(db: Session, country_id: int) -> DBCountry | None:
    """Get a single country info by ID."""
    return db.query(DBCountry).filter(DBCountry.Country_Id == country_id).first()


def fetch_all_countries(db: Session, skip: int = 0, limit: int = 100) -> List[DBCountry]:
    """Get a list of all countries with pagination."""
    return db.query(DBCountry).offset(skip).limit(limit).all()


def modify_country(db: Session, country_id: int, updates: CountryUpdateSchema) -> DBCountry | None:
    """Update a country's information."""
    country_query = db.query(DBCountry).filter(DBCountry.Country_Id == country_id)
    country_record = country_query.first()
    if not country_record:
        raise HTTPException(status_code=404, detail="Country not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(country_record, field, value)

    db.commit()
    db.refresh(country_record)
    return country_record

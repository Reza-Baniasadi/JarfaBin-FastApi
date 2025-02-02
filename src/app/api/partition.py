from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Partition
from schemas import PartitionCreate, PartitionOut, PartitionUpdate
from database import get_db


router = APIRouter()

@router.post("/", response_model=PartitionOut)
def create_partition(payload: PartitionCreate, db: Session = Depends(get_db)):
    db_partition = Partition(name=payload.name, description=payload.description)
    db.add(db_partition)
    db.commit()
    db.refresh(db_partition)
    return db_partition
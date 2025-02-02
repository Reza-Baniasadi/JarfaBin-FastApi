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

@router.get("/{partition_id}", response_model=PartitionOut)
def get_partition(partition_id: str, db: Session = Depends(get_db)):
    db_partition = db.query(Partition).filter(Partition.id == partition_id).first()
    if db_partition is None:
        raise HTTPException(status_code=404, detail="Partition not found")
    return db_partition
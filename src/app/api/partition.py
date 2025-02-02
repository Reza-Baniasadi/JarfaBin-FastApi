from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Partition
from schemas import PartitionCreate, PartitionOut, PartitionUpdate
from database import get_db
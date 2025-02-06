from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from accounting_models import Transaction
from accounting_schemas import TransactionCreate, TransactionOut
from accounting_database import get_db
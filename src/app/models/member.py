from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String,ForeignKey,Boolean,Float,DateTime
from database import Base
from sqlalchemy import event


class Member(Base):
    __tablename__ = "Members"

    Member_id = Column(Integer,primary_key= True,index = True)
    First_name = Column(String(20))
    Middle_name = Column(String(20))  #optional Attribute
    Last_name = Column(String(20))
    Email = Column(String(150), index=True,unique=True, nullable=False)
    Country_Id = Column(Integer, ForeignKey("Country_Info.Country_Id", onupdate='CASCADE', ondelete='CASCADE'))
    Contact_Number = Column(String(20),unique=True, nullable=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    account_status = Column(Integer)
    processed_by_id = Column(Integer, ForeignKey("Users.id", onupdate='CASCADE', ondelete='CASCADE'))

    processed_by = relationship("User", backref="processed_by", passive_deletes=True)
    deposits = relationship("Deposit", back_populates="member", passive_deletes=True)
    withdrawals = relationship('Withdrawal', back_populates='member', passive_deletes=True)
    transaction_logs = relationship('TransactionLog', back_populates='member', passive_deletes=True)
    currency_info  = relationship('Country_Info', back_populates='member', passive_deletes=True)
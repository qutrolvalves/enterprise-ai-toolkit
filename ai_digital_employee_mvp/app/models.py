from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime
Base = declarative_base()

class CustomerRequest(Base):
    __tablename__ = 'customer_requests'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    status = Column(String, default='pending')
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

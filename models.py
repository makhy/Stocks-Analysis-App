from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from database import Base

class CryptoItem(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True)
    shortname = Column(String, unique=True)
    price = Column(Numeric(10,2))
    ma50 = Column(Numeric(10,2))
    ma200 = Column(Numeric(10,2))

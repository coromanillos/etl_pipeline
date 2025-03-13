##############################################
# Title: Schema Script
# Author: Christopher Romanillos
# Description: Defines schema for postgres
# ETL pipeline. 
# Date: 11/23/24
# Version: 1.0
##############################################
from sqlalchemy import Column, Integer, BigInteger, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class IntradayData(Base):
    """
    SQLAlchemy model for intraday time-series data.
    Defines schema for storing OHLCV data with timestamps.
    """
    __tablename__ = 'intraday_data'  # Table name in PostgreSQL

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # Scalable ID
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)  # Unique time-series data
    open = Column(Float, nullable=False)  # OHLC and volume data
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # When record was first inserted

# To create the table:
# - Import 'Base' into a setup script.
# Use `Base.metadata.create_all(engine)` with a properly configured engine.
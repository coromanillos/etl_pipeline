##############################################
# Title: Schema Script
# Author: Christopher Romanillos
# Description: Defines schema for Postgres ETL pipeline.
# Date: 11/23/24
# Version: 1.1
##############################################

from datetime import datetime
from sqlalchemy import Column, BigInteger, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IntradayData(Base):
    """
    SQLAlchemy model for intraday time-series data.
    Defines schema for storing OHLCV data with timestamps.
    """
    __tablename__ = 'intraday_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# To create the table:
# - Import 'Base' into a setup script.
# - Use `Base.metadata.create_all(engine)` with a properly configured engine.

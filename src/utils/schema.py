##############################################
# Title: Schema Script
# Author: Christopher Romanillos
# Description: Defines schema for Postgres ETL pipeline.
# Date: 11/23/24
# Version: 1.2 (SQLAlchemy 1.4 compatible)
##############################################

from datetime import datetime
from sqlalchemy import Column, BigInteger, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, List, Type

Base = declarative_base()

class IntradayData(Base):
    __tablename__ = "intraday_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def get_table_column_types() -> Dict[str, Type]:
    """Return mapping of column names to SQLAlchemy types."""
    return {
        "timestamp": DateTime,
        "open": Float,
        "high": Float,
        "low": Float,
        "close": Float,
        "volume": BigInteger,
    }

def get_required_columns() -> List[str]:
    """Return list of required column names."""
    return ["timestamp", "open", "high", "low", "close", "volume"]

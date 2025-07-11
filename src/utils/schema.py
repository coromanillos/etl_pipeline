##############################################
# Title: Schema Script
# Author: Christopher Romanillos
# Description: Defines schema for Postgres ETL pipeline.
# Date: 11/23/24
# Version: 1.2 (SQLAlchemy 2.x compatible)
##############################################

from datetime import datetime
from sqlalchemy import Column, BigInteger, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class IntradayData(Base):
    __tablename__ = "intraday_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, unique=True, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

def get_table_column_types():
    return {
        "timestamp": DateTime,
        "open": Float,
        "high": Float,
        "low": Float,
        "close": Float,
        "volume": BigInteger,
    }

def get_required_columns():
    return ["timestamp", "open", "high", "low", "close", "volume"]

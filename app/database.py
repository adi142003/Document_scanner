
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./scanner.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)  # filename
    datatype = Column(String)  # sensitive data type
    value = Column(String)  # detected information
    date = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

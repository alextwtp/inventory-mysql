from sqlalchemy import Column, DateTime, Integer, String, func

from config.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(String(50), nullable=False, unique=True)
    item_name = Column(String(100), nullable=False)
    qty = Column(Integer, nullable=False, default=0)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
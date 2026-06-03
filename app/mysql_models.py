from sqlalchemy import Column, DateTime, Integer, String, func, CheckConstraint
from sqlalchemy.orm import validates
from db import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Use CheckConstraint to ensure the pid is in Uppercase
    pid = Column(
        String(50), 
        CheckConstraint("pid = UPPER(pid)", name="check_pid_uppercase"), 
        nullable=False, 
        unique=True
    )    
    item_name = Column(String(100), nullable=False)
    qty = Column(Integer, nullable=False, default=0)
    receiver = Column(String(100), nullable=False)    
    shipper = Column(String(100), nullable=False)    

    # Validate the pid and return upper case for it   
    @validates("pid")
    def validate_pid_uppercase(self, key, value):
        if value is not None:
            return value.upper()
        return value

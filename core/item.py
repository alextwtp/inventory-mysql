from dataclasses import dataclass
from typing import Optional

@dataclass
class Item:
    pid: str
    name: str
    current_qty: int=0
    time_now: Optional[str] = None
    buyer: Optional[str] = None
    last_update: Optional[str] = None
    shipper: Optional[str] = None
    row: Optional[int] = None
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.mysql_models import Inventory  # noqa: F401 - register model with Base.metadata
from core.exceptions import AppError
from core.inventory_mysql_service import InventoryMySQLService
from core.item import Item
from repository.mysql_repository import MySQLRepository


app = FastAPI(title="Inventory MySQL API")


class InventoryRequest(BaseModel):
    pid: str
    name: str = ""
    qty: int
    receiver: str = ""
    shipper: str = ""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session) -> InventoryMySQLService:
    repo = MySQLRepository(db)
    return InventoryMySQLService(repo)


def item_response(item: Item, message: str) -> dict:
    return {
        "status": "success",
        "message": message,
        "item": {
            "pid": item.pid,
            "name": item.name,
            "current_qty": item.current_qty,
            "buyer": item.buyer,
            "shipper": item.shipper,
        },
    }


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "message": "Inventory MySQL API is running"}


@app.get("/item/{pid}")
def get_item(pid: str, db: Session = Depends(get_db)) -> dict:
    service = get_service(db)

    try:
        item = service.get_item(pid)
        return item_response(item, "Item found")
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error") from exc


@app.post("/inventory/in")
def inventory_in(req: InventoryRequest, db: Session = Depends(get_db)) -> dict:
    service = get_service(db)

    try:
        item = service.inventory_in(
            pid=req.pid,
            name=req.name,
            qty=req.qty,
            receiver=req.receiver,
            shipper=req.shipper,
        )
        return item_response(item, "Inventory-in success")
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error") from exc


@app.post("/inventory/out")
def inventory_out(req: InventoryRequest, db: Session = Depends(get_db)) -> dict:
    service = get_service(db)

    try:
        item = service.inventory_out(
            pid=req.pid,
            name=req.name,
            qty=req.qty,
            receiver=req.receiver,
            shipper=req.shipper,
        )
        return item_response(item, "Inventory-out success")
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error") from exc

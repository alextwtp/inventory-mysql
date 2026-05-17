from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel, Field
from config import constants as cons
from core.item import Item
from typing import Optional
from core.inventory_service import InventoryService
from repository.excel_repository import ExcelRepository
from fastapi.responses import JSONResponse
from core.exceptions import AppError
from core.exceptions import (  
    NegativeError,  
    NoneListError, 
    NoItemError,
    StockShortError,
    UnknownError,    
    NameLackError,  
   )


app = FastAPI(title="Inventory API")
api_router = APIRouter(prefix="/api")

# repository + service
FILE_NAME= cons.MAIN_FILENAME
repo = ExcelRepository(FILE_NAME)
service = InventoryService(repo)

class InventoryRequest(BaseModel):
    pid: str 
    qty: int = Field(ge=1, description="入庫數量必須大於等於 1")
    name: Optional[str] = None  # 這是更標準的 Optional 寫法
    receiver: Optional[str] = None 
    shipper: Optional[str] = None 
       

@app.exception_handler(AppError)             #處裡自訂錯誤
def handle_app_error(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": exc.__class__.__name__,
            "message": str(exc),
        }
    )
@app.exception_handler(Exception)             #處理未知錯誤
def handle_all_error(request, exc):
    status_code = getattr(exc, "status_code", 500)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,   
            "error": exc.__class__.__name__,
            "message": str(exc),
        },
    )

   
def success_response(data, message=None): 

    return {
        "success": True,
        "data": data,
        "error": None,
        "message": message
    }
  
# ------------------------
# 查詢商品
# ------------------------
@app.get("/")                 # uvicoren 首頁, 指定網址 127.0.0.1:8000 or 8000....
def read_root():
    return {"hello": "world"}

@api_router.get("/item/{pid}")
def get_item_api(pid: str):
    service.ensure_file_dir_and_path()
    work_file,work_list=service.get_file_and_list()
    mode=""
    row=service.get_row(work_list,pid,mode)                                         
    item = service.get_item(work_list,row)      
    if item is None:
        raise NoItemError(status_code=404, detail="Item not found")
    item.row=row
    return item
# ------------------------
# 入庫
# ------------------------
@api_router.post("/inventory/in")
def inventory_in(req:InventoryRequest):   
    try:
        item = service.inventory_count_in_and_write(
            pid=req.pid,
            qty=req.qty,
            name=req.name, 
            receiver=req.receiver,
            shipper=req.shipper        
        )  
        return success_response(item, "進貨成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------
# 出庫
# ------------------------
@api_router.post("/inventory/out")
def inventory_out(req:InventoryRequest):
    try:
        item:Item = service.inventory_count_out_and_write(
            pid=req.pid,
            qty=req.qty,
            name=req.name, 
            receiver=req.receiver,
            shipper=req.shipper         
        )                                 
        return success_response(item, "出貨成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# 3. 關鍵：掛載動作要在 app 出現後
app.include_router(api_router)
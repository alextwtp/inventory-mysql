from repository.excel_repository import ExcelRepository
from openpyxl import Workbook, load_workbook
from pathlib import Path
import pytest
import shutil

app=ExcelRepository(path="data/inventory.xslx")

def test_read_item():
    path="data/inventory.xlsx"
    # 1. 先執行 load，取得真正的工作表物件 (sheet)
    
    work_file,work_sheet= app.load_file_and_list(path)        
    row=6
    item = app.read_item(work_sheet, row) 
    assert item.current_qty == 10

import shutil

def test_write_item(tmp_path):
    # 1. 準備環境 
    original = "data/inventory.xlsx" 
    temp_file = tmp_path/"test_write.xlsx"
    shutil.copy2(original, temp_file)
    
    # 2. 初始化
    app = ExcelRepository(str(temp_file))
    work_file,work_sheet= app.load_file_and_list(app.path)
    
    # 3. 準備寫入的 dict
    
    new_values = {
        "編號": "K007",
        "品名": "測試商品", 
        "目前庫存": 88
    }
    
    # 4. 執行寫入    
    app.write_item(work_sheet, 6, new_values)
    
    # 5. 驗證 (直接再讀一次第 6 列，確認資料變了)
    updated_item = app.read_item(work_sheet, 6)
    assert updated_item.current_qty == 88    

import core as cor
import os
import re
import shutil
from core.item import Item
from config import constants as cons
from config.database import SessionLocal
from pathlib import Path
from datetime import datetime
from openpyxl.utils import get_column_letter
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from core.exceptions import (
    ExcelFormatError,                  
    StockShortError,
    FileInuseError,           
    ReadError,  
    WriteError,
)
#======================================
# [1] 檔案路徑與時間：讓程式「永遠只在自己資料夾工作」
# ============================================================

def now_str() -> str:
    """現在時間（字串），存入 最近更新 / DATE_PREV1 """  
    DATE_FMT=  cons.DATE_FMT           
    return datetime.now().strftime(DATE_FMT)

def today_ymd() -> str:
    """今天日期（YYYY-MM-DD），用在『每日備份檔名』"""
    return datetime.now().strftime("%Y-%m-%d")
        
class ExcelRepository:
    def __init__(self, path):
        self.path = Path(path)
        self._cache = None

    def complete_the_write(self,mode,row,name,pid,current_qty,qty,receiver,shipper,new_qty)->Item:
        path = self.file_path()                           
        self.ensure_filepath(path)                      
        LAST_BACKUP=cons.LAST_BACKUP  
        self.last_backup_path(LAST_BACKUP)              
        self.backup_before_update(path, LAST_BACKUP ) 

        try:
          wb, ws = self.load_file_and_list(path)
        except PermissionError:
            raise FileInuseError("⚠ 檔案使用中,請先關閉 Excel 檔案")            
        except Exception:                      
            raise ReadError("讀取 Excel 失敗")       
       
        if "Log" not in wb.sheetnames:
            log_ws = wb.create_sheet("Log")
            log_ws.append(["時間", "編號", "品名", "動作", "數量", "買貨人"])
            self.sort_log_by_id(ws)
        else:
            log_ws = wb["Log"]
            self.sort_log_by_id(ws)
                      
        write_data = {}      #建立一個名為 write_data 的空字典 (Dictionary)         
        delta = qty if mode == "IN" else -qty  # 進貨: +值 出貨 -值                  

        if mode =="OUT":                       
            if not receiver : 
                delta=0
                return

        if row == ws.max_row + 1:                                                      
            if name is None:
                return                  
            write_data = {
                "編號": pid,
                "品名": name.strip(),
                "目前庫存": delta,
                "最近更新": now_str(),
                "買貨人": receiver,
                "前次庫存": None,
                "出貨人": None
            }
        else:                                                                      
            if new_qty < 0:
                    raise StockShortError("庫存不足")            
           
            write_data = {
                "編號": pid,
                "品名": name.strip(),
                "目前庫存": new_qty,
                "最近更新": now_str(),
                "買貨人": receiver,
                "前次庫存": current_qty,
                "出貨人": shipper
            }                                                                                                               
        
        
      # ========= 寫入 Excel（唯一一次） =========
        #print("EXCE-101_COMP-2",pid,row,new_qty, name)       
        self.write_item(ws, row, write_data) 
        # 排序
        self.sort_sheet_by_id(ws)
        # ⭐ 重新找到排序後的位置
        row = self.find_row_by_id(ws, pid)

        sheet_num=1
        self.format_sheet(ws,sheet_num)    
            
        if os.path.getsize(path) == 0:
            raise WriteError ("Excel 寫入失敗（檔案大小為 0）")     
        if not os.path.exists(path):
            return False  # 檔案不存在，視為未開啟 
        
        try: 
            self.safe_save_workbook(wb, path)
            self._cache = None
        except:  
            raise FileInuseError("⚠ 檔案使用中，請先關閉 Excel")
                    
    # ========= 寫入 Log =========
        log_ws = wb["Log"]    
        action = "進貨" if delta > 0 else "出貨"
        person = receiver if mode == "OUT" else ""

    # 1️⃣ 先新增一筆
        log_ws.append([
            now_str(),
            write_data["編號"],
            write_data["品名"],
            action,
            abs(delta),
            person
        ])

    # 2️⃣ 取得剛新增那一列        
        pid = write_data["編號"]               

    # 4️ 依「編號」排序
        self.sort_log_by_id(log_ws)
        sheet_num=2
        self.format_sheet(log_ws,sheet_num)
        self.color_all_log_groups(log_ws)  
    # 5️⃣ 最後才存檔（非常重要）
        self.safe_save_workbook(wb, path)
        self._cache = None
    # 傳回值        
        return Item(             
            pid=pid,
            name=name,
            current_qty=new_qty,
            time_now=now_str(),
            buyer=receiver,
            shipper=shipper,
            row=row
        )   

    def app_dir(self):
        return Path(__file__).resolve().parent.parent/ "data"        
    

    def last_backup_path (self,LAST_BACKUP) -> str:  
                     
            return os.path.join(self.app_dir(), LAST_BACKUP)
           
    """Excel 完整路徑 = 程式資料夾 + inventory.xlsx"""                       
                
    def file_path (self) -> str:
            EXCEL_FILENAME= cons.MAIN_FILENAME                  
            return os.path.join(self.app_dir(), EXCEL_FILENAME)
            
    """Excel 完整路徑 = 程式資料夾 + inventory.xlsx"""
       
   
    #============================================================
    #[2] Excel 初始化 / 讀取：確保檔案與表頭一定正確
    #============================================================
    def ensure_filepath(self,path) -> None:      
        
        if os.path.exists(path):
            return

        wb = Workbook()
        ws = wb.active
        ws.title = cons.SHEET_NAME    ##cor.  
        HEADERS=cons.HEADERS 
        ws.append(HEADERS)

        widths = [12, 20, 15, 25, 15, 15, 25]

        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        wb.save(path)

    def safe_save_workbook(self, wb, path: str) -> None:
        """
        原子保存（很實務）：
        直接 wb.save(path) 有機率在中途被中斷（關程式/斷電/防毒掃描）而造成壞檔。
        做法：先存成 .tmp，再用 os.replace 一次性替換（比較安全）
        """      
        tmp = path + ".tmp"
        wb.save(tmp)
        os.replace(tmp, path)

    def load_file_and_list(self, path: str):  
        """
        打開 Excel + 取得工作表。
        同時做『表頭驗證』：避免有人手動改 Excel 欄位，程式寫錯位置。
        """
        SHEET_NAME=cons.SHEET_NAME  ##cor.
        HEADERS =cons.HEADERS   ##cor

        if self._cache is not None:
            return self._cache  
  
        wb = load_workbook(path)
        # 如果工作表不存在就建立（一般不會發生，但防呆）
        if SHEET_NAME not in wb.sheetnames:
            ws = wb.create_sheet(SHEET_NAME)
            ws.append(HEADERS)
        else:
            ws = wb[SHEET_NAME]
        
        # 驗證第一列表頭必須完全一致
        first_row = [c.value for c in ws[1]]
        if first_row != HEADERS:
            raise ExcelFormatError(
                "Excel 表頭格式不正確。\n"
                f"請確認第 1 列欄位為：{', '.join(HEADERS)}"
            )
        self._cache = (wb, ws)           
        return wb,ws

    def backup_before_update(self,path: str,last_backup:str) -> None:
        
        # 1. 檢查來源檔是否存在
        if not os.path.exists(path):
            print(f"錯誤：找不到來源檔案 {path}")
            return        
        # 2. 嘗試複製cls
        try:            
            shutil.copy2(Path(path), Path(path).with_name(last_backup))
            print(f"成功：已將 {path} 複製至 {last_backup}")
        except PermissionError:
            print(f"警告：檔案 {path} 正被其他程式(如 Excel)開啟中，無法複製！")                       
            print("請關閉檔案後重試...")                           
        return

                        
# ============================================================
# [4] Excel 資料操作（Data Access Layer 的概念）
# ============================================================

    def sort_sheet_by_id(self,ws):
        """
        將第2列以後的資料依 ID 數字排序
        不動表頭
        """
        data = []
        HEADERS =cons.HEADERS ##cor.

        # 讀取所有資料列
        for r in range(2, ws.max_row + 1):
            row_values = []
            empty = True

            for c in range(1, len(HEADERS) + 1):
                val = ws.cell(row=r, column=c).value
                row_values.append(val)
                if val not in (None, ""):
                    empty = False

            if not empty:
                data.append(row_values)
        # sort by ID　if ID start with Alphabet (A~Z)
        data.sort(key=lambda x: str(x[0]).lower())

        # 依 ID 排序（第1欄）
        #data.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 999999)

        ws.delete_rows(2, ws.max_row)

        for i, row_data in enumerate(data, start=2):
            for c, val in enumerate(row_data, start=1):
              ws.cell(row=i, column=c).value = val      


    def format_sheet(self,ws, sheet_num):
        """
        美化 Excel：
        - 表頭粗體
        - 表頭置中
        - 所有欄位置中
        - 凍結第一列
        - 欄寬固定
        """
        HEADERS=cons.HEADERS  ##cor.

        # 凍結第一列
        ws.freeze_panes = "A2"  # 凍結地一列

        # 表頭格式
        header_font = Font(size=14,bold=True)
        center_align = Alignment(horizontal="center", vertical="center")

        for col in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = header_font
            cell.alignment = center_align
        
        # 所有資料列置中
        for r in range(2, ws.max_row + 1):
            for c in range(1, len(HEADERS) + 1):
                ws.cell(row=r, column=c).alignment = center_align
        # 欄寬微調（你可以之後再改）
        if sheet_num==1:
            widths=[12, 20, 15, 25, 15, 15, 25]
            for i, w in enumerate(widths, start=1):
                ws.column_dimensions[get_column_letter(i)].width = w
                
        else:
            if sheet_num ==2:
                widths=[25, 12, 15, 15, 15, 25]
                for i, w in enumerate(widths, start=1):
                    ws.column_dimensions[get_column_letter(i)].width = w
        

    def find_row_by_id(self,ws, pid: str) -> int | None:        
        """
        在工作表中找 ID 所在列（從第 2 列開始找）
        找到回 row index（int），找不到回 None
        """      
        pid = pid.strip()        
        if not pid:  
            return None                         

        for r in range(2, ws.max_row + 1):
            val = ws.cell(row=r, column=1).value  # column 1 = ID
            if val is None:
                continue
            if str(val).strip() == pid:
                return r
            
        return None    
   
    def read_item(self,ws, row: int)->Item:
        """讀出某一列的所有欄位，組成 dict（key=欄位名）"""        
        pid = ws.cell(row=row, column=1).value
        name = ws.cell(row=row, column=2).value
        qty = ws.cell(row=row, column=3).value
        time_now = ws.cell(row=row, column=4).value
        buyer = ws.cell(row=row, column=5).value
        last_update=ws.cell(row=row, column=6).value
        shipper = ws.cell(row=row, column=7).value       
        return Item(             
            pid=pid,
            name=name,
            current_qty=qty,
            time_now=time_now,
            buyer=buyer,
            last_update=last_update,
            shipper=shipper
        )          
 

    def write_item(self, ws, row: int, values: dict) -> None:   
        """把 dict 寫回某一列（欄位順序由 HEADERS 決定）"""
        print("EX-371-WRITE-ITEM",row)
        HEADERS=cons.HEADERS   ##cor.
        for i, h in enumerate(HEADERS, start=1):
            ws.cell(row=row, column=i).value = values.get(h)  
        print("EX-375-WRITE_ITEM-DONE",row)


    def sort_log_by_id(self,ws):
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        rows.sort(key=lambda r: str(r[1]).lower())  # 第2欄 = 編號

        ws.delete_rows(2, ws.max_row)

        for r in rows:
            ws.append(r) 

    def color_all_log_groups(self,ws):
        from openpyxl.styles import PatternFill

        current_pid = None
        color_index = -1


        for row in ws.iter_rows(min_row=2):
            pid = row[1].value   # B欄 = 編號

            if pid != current_pid:
                current_pid = pid
                LOG_COLORS=cons.LOG_COLORS  ##cor.
                color_index = (color_index + 1) % len(LOG_COLORS)
                fill = PatternFill(start_color=LOG_COLORS[color_index],
                                end_color=LOG_COLORS[color_index],
                                fill_type="solid")

            for cell in row:
                cell.fill = fill

    def qty_to_int(self,x) -> int:
        """Excel 讀出來可能是 None/空字串，統一轉成 int（預設 0）"""
        if x is None or str(x).strip() == "":
            return 0
        try:
            return int(x)
        except Exception:
            return 0
    
  
        

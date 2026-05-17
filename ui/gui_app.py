import os
import re
import tkinter as tk
import requests
import json
from config import constants as cons
from core.item import Item
from tkinter import messagebox, simpledialog
from tkinter import Toplevel, Label, Entry, Button
from dataclasses import dataclass
from typing import Optional
from core.exceptions import(    
    NegativeError,
    NoneListError, 
    NoItemError,    
   )

def normalize_id(s: str) -> str:
        """ID 去掉前後空白"""
        return (s or "").strip()

@dataclass
class ItemSave:
    pid: Optional[str] = ""
    item_name: Optional[str] = ""    
    current_qty: Optional[int] = 0              # 數量變動
    time_now: Optional[str] = ""
    buyer: Optional[str] = ""
    shipper: Optional[str] = ""
    row_index: Optional[int] = 0                 # 這是你最關心的 row

    workfile: Optional[str] =""
    worksheet:Optional[str] =""

class ui_item:
    item_id: Optional[str] = ""
    name: Optional[str] = ""    
    current_qty: Optional[int] = 0              # 數量變動
    time_now: Optional[str] = ""
    receiver: Optional[str] = ""
    shipper: Optional[str] = ""
    last_qty: Optional[int] = 0   
    _row_: Optional[int] = 0                 # 這是你最關心的 row


def show_custom_error(title, message):
    # 建立彈出視窗
    err_win = tk.Toplevel()
    err_win.title(title)
    
    # 設定最小寬度，防止訊息太短時視窗縮成一團
    err_win.minsize(300, 150)
    
    # 訊息標籤：wraplength 設定文字超過 350 像素就自動換行
    msg_label = tk.Label(err_win, text=message, wraplength=350, justify="left", padx=20, pady=20)
    msg_label.pack(expand=True)

    # 關閉按鈕
    tk.Button(err_win, text="確定", width=10, command=err_win.destroy).pack(pady=10)

# 使用範例：只需要呼叫這個 function 並傳入文字即可
# show_custom_error("系統錯誤", "這是一段超級長的錯誤訊息..." * 10)
def show_result_error(message):
    print("❌", message)
    messagebox.showerror("錯誤", message)

def show_result_success(message):
    print("✅", message)
    messagebox.showinfo("成功", message)


class InventoryApp:     
    def __init__(self, root: tk.Tk, service):        
        WINDOW_TITLE="庫存更新系統 v2.1"  
        # ---- 視窗基本設定             
        self.root = root   
        self.service = service
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)
        self.item_save=ItemSave() 
        self.prior_pid=0            
    
        # ---- 第一次啟動：確保 Excel 存在 + 每日備份
        self.service.ensure_file_dir_and_path()
        
        # ---- UI 狀態（mode：進貨/出貨）       
        self._lookup_after_id = None  # 用在 debounce：避免每打 1 個字就查一次 Excel
        self._mode = None             # "IN" or "OUT"
        self._last_item = None        # 最近查到的 item（非必要，但留著可擴充）

        # ---- Tk 變數（UI 上顯示/輸入用）
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar(value="（新產品,按進貨後請輸入編號）")
        self.var_nowqty = tk.StringVar(value="")
        self.var_qty = tk.StringVar()  # 員工輸入的「數量」（純數字）

         # 初始化一個空的 StringVar
        self.var_warn = tk.StringVar(value="") 
        # 初始化標籤，預設可能是黑色或隱藏
        self.lbl_warn = tk.Label(root, textvariable=self.var_warn, fg="black")
        self.lbl_warn.grid()    

         
     
        # ---- 建立畫面元件  
        self._build_ui()   

        # ---- 重點：ID 有變動就安排「自動查詢」
        self.var_id.trace_add("write", lambda *_: self._schedule_auto_lookup())

        # ---- 初始 focus：讓員工一開就能打 ID
        self.ent_id.focus_set()

    def gui_error_msg1(self):  
        show_custom_error("錯誤", "新商品不能出貨")      

    def gui_error_msg2 (self,current_qty):
        show_custom_error("錯誤", "庫存只剩: current_qty")   
  
    def msg_in_or_out_warning(self):
        show_custom_error("提醒", "請先按【進貨】或【出貨】")          
     
    def receiver_asking(self):
        receiver=""        
        receiver = simpledialog.askstring("買貨人", "請輸入買貨人（必填）：")
        return receiver
            
    def msg_closefile_warning(self):
        messagebox.showerror("錯誤", "檔案使用中，請先關閉 Excel") 

    def msg_str_warning(elf,e):
        messagebox.showerror("錯誤", str(e))     

    def msgbox_id_warning(self):         
        messagebox.showwarning("提醒", "請輸入產品編號") 
        self.ent_id.focus_set()        
    
    def need_positive_warning(self):  
        messagebox.showwarning("提醒", "數量請輸入正整數")
        self.ent_qty.focus_set()           

    # -------------------------
    # UI 排版與事件綁定
    # -------------------------
    def _build_ui(self):
        window_width  = 500
        window_height = 400
        
    # 1. 取得螢幕的寬度與高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 2. 計算置中的座標公式
        # x = (螢幕寬 - 視窗寬) / 2
        # y = (螢幕高 - 視窗高) / 2
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        # 3. 設定幾何尺寸與位置：寬x高+X偏移+Y偏移
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
 
        pad = 10  

        tk.Label(self.root, text="庫存更新系統", font=("Microsoft JhengHei", 16, "bold"))\
            .grid(row=0, column=0, columnspan=4, padx=pad, pady=(pad, 6), sticky="w")

        # [Step-1] 輸入 ID   
        tk.Label(self.root, text="產品編號：", font=("Microsoft JhengHei", 12))\
            .grid(row=1, column=0, padx=pad, pady=5, sticky="e")
        
        self.ent_id = tk.Entry(self.root, textvariable=self.var_id, width=22, font=("Consolas", 12))
        self.ent_id.grid(row=1, column=1, padx=0, pady=5, sticky="w")

        # 手動查詢 / 歷史（主管查用）  
        tk.Button(self.root, text="查詢", width=8, command=self.lookup).grid(row=1, column=2, padx=(6, 0), pady=5)
        tk.Button(self.root, text="歷史", width=8, command=self.show_history).grid(row=1, column=3, padx=(6, pad), pady=5)

        # [Step-2] 顯示品名 & 庫存（由 lookup 讀 Excel 後更新）
        tk.Label(self.root, text="產品名稱：", font=("Microsoft JhengHei", 12))\
            .grid(row=2, column=0, padx=pad, pady=5, sticky="e")
        tk.Label(self.root, textvariable=self.var_name, font=("Microsoft JhengHei", 12, "bold"))\
            .grid(row=2, column=1, columnspan=3, padx=0, pady=5, sticky="w")

        tk.Label(self.root, text="目前庫存：", font=("Microsoft JhengHei", 12))\
            .grid(row=3, column=0, padx=pad, pady=5, sticky="e")
        tk.Label(self.root, textvariable=self.var_nowqty, font=("Consolas", 12))\
            .grid(row=3, column=1, columnspan=3, padx=0, pady=5, sticky="w")

        # 低庫存警示文字（顯示/不顯示）
        self.lbl_warn = tk.Label(self.root, textvariable=self.var_warn, font=("Microsoft JhengHei", 11, "bold"))
        self.lbl_warn.grid(row=4, column=1, columnspan=3, padx=0, pady=(0, 6), sticky="w")

        # [Step-3] 選擇操作模式：進貨 or 出貨（決定 delta 正負）
        tk.Label(self.root, text="操作：", font=("Microsoft JhengHei", 12))\
            .grid(row=5, column=0, padx=pad, pady=5, sticky="e")
        self.btn_in = tk.Button(self.root, text="進貨", width=10, command=lambda: self.set_mode("IN"))
        self.btn_in.grid(row=5, column=1, padx=(0, 6), pady=5, sticky="w")

        self.btn_out = tk.Button(self.root, text="出貨", width=10, command=lambda: self.set_mode("OUT"))
        self.btn_out.grid(row=5, column=2, padx=(0, 6), pady=5, sticky="w")

        # [Step-4] 輸入數量（純數字）
        tk.Label(self.root, text="數量：", font=("Microsoft JhengHei", 12))\
            .grid(row=6, column=0, padx=pad, pady=5, sticky="e")

        # validate="key"：每打 1 個字就檢查，不符合就不讓輸入（防呆）
        vcmd = (self.root.register(self._validate_qty_entry), "%P")
        self.ent_qty = tk.Entry(
            self.root, textvariable=self.var_qty, width=22, font=("Consolas", 12),
            validate="key", validatecommand=vcmd   
        )
        self.ent_qty.grid(row=6, column=1, padx=0, pady=5, sticky="w")

        tk.Label(self.root, text="只輸入數字，例如：3", fg="gray")\
            .grid(row=6, column=2, columnspan=2, padx=(6, pad), pady=5, sticky="w")

        # [Step-5] 確認更新 → 寫回表單    
                           
        self.btn_confirm = tk.Button(self.root, text="確認更新", width=16, height=2, command=self.confirm_update)
        self.btn_confirm.grid(row=7, column=0, columnspan=4, padx=pad, pady=(10, pad)) 

        # 快捷鍵：
        # - 在 ID 輸入框按 Enter：手動查詢 + 跳到數量欄
        # - 在 數量框按 Enter：直接更新（員工最快流程）
        # - Esc：快速關閉
        self.ent_id.bind("<Return>", lambda e: (self.lookup(), self.ent_qty.focus_set()))
        self.ent_qty.bind("<Return>", lambda e: self.confirm_update())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # 初始：沒有選擇進/出，所以按鈕不凸顯
        self._refresh_mode_buttons()
 
    def _validate_qty_entry(self, proposed: str) -> bool:
        """
        Entry 即時防呆：  
        - 允許空字串（方便刪掉重打）
        - 或純數字
        """
        if proposed == "":
            return True        
        return bool(re.fullmatch(r"\d+", proposed))

    def _schedule_auto_lookup(self):
        """
        自動查詢（debounce 的概念）：
        - 使用者打字會連續觸發 trace
        - 我們先取消上一個 after，再重新排程
        - 只有「停下來超過 300ms」才真的去查 Excel
        """
        AUTO_LOOKUP_DELAY_MS= cons.AUTO_LOOKUP_DELAY_MS  
        if self._lookup_after_id is not None:
            self.root.after_cancel(self._lookup_after_id)
        self._lookup_after_id = self.root.after(AUTO_LOOKUP_DELAY_MS, self.lookup_silent)

    def _set_display_unknown(self, msg: str):
        """當查不到 ID 或還沒輸入 ID 時，畫面顯示用"""
        self.var_name.set(msg)
        self.var_nowqty.set("")
        self.var_warn.set("")
        self._last_item = None  

    def _set_display_item(self, pid: str, item:dict):
        """
        查到商品後，更新畫面：
        - 顯示品名、庫存
        - 判斷低庫存，顯示紅字警示
        """
        LOW_STOCK_THRESHOLD= cons.LOW_STOCK_THRESHOLD         
        if item is None:
            return
        else:          
            name = str(item.name or "")            
            try:
                qty = self.service.make_qty_to_int(item)           
            except NegativeError("""數量不可為負值""") as e:
                print(f"輸入錯誤：{e}") # 會印出：輸入錯誤：數量不可小於 0               
                
        self.var_name.set(name if name else "（未命名）")
        #print("UI279", str(qty))
        self.var_nowqty.set(str(qty))    

        if qty <= LOW_STOCK_THRESHOLD:                         
            self.var_warn.set(f"⚠ 低庫存提醒：目前 {qty}（門檻 {LOW_STOCK_THRESHOLD}）")
            self.lbl_warn.configure(fg="red")
        else:
            self.var_warn.set("")
            self.lbl_warn.configure(fg="black")                                                  
        # 把 row 等資訊留著（未來擴充可用） 
        self._last_item = item
        self._last_pid = item.pid   


    def _refresh_mode_buttons(self):
        """
        小小 UX：讓員工知道自己選的是進貨還是出貨
        tkinter 的 relief="sunken" 看起來像被按下去
        """
        if self._mode == "IN":
            self.btn_in.configure(relief="sunken")
            self.btn_out.configure(relief="raised")
        elif self._mode == "OUT":
            self.btn_in.configure(relief="raised")
            self.btn_out.configure(relief="sunken")
        else:
            self.btn_in.configure(relief="raised")
            self.btn_out.configure(relief="raised")

    def set_mode(self, mode: str):
        """按進貨/出貨後設定模式，並把 focus 送到數量欄（加速操作）"""        
        self._mode = mode
        self._refresh_mode_buttons()
        self.ent_qty.focus_set()
    
    # ============================================================
    # [流程核心-1] 查詢：輸入 ID → 讀 Excel → 顯示品名/庫存
    # ============================================================
    def lookup_silent(self):
        """
        自動查詢版（silent）：
        - 不彈訊息框
        - 只更新畫面（更像「即時提示」）
        """
        pid = normalize_id(self.var_id.get())       
        if not pid:                               
            self._set_display_unknown("（請輸入編號）")
            return        
        try:                                        
            work_file,work_list = self.service.get_file_and_list()                                  
        except NoneListError: 
            self._set_display_unknown("讀取 file 失敗")                      
            return
        
        self.item_save.workfile=work_file
        self.item_save.worksheet=work_list

        mode=self._mode
        row=0
        
        try:
            row=self.service.get_row(work_list,pid,mode)                                                       
        except NoItemError:                                   
            self._set_display_unknown("(找不到此編號,請重新輸入)")
            return
        
        if pid == self.prior_pid:            
            self.save_prior_information(pid,row,work_list)
            return

        if row is not None:
            try:               
                item = self.service.get_item(work_list,row)                                                                                                                     
                item.row = row                    
                self.save_item_information(item,row)                
                self._set_display_item(pid, item) 
            except NoItemError:                                               
                self._set_display_unknown("(找不到此編號,請重新輸入)")
                return

    def save_prior_information(self, pid, row, work_list):
        item = self.service.get_item(work_list,row)
        self.item_save.pid=ui_item.pid                     
        self.item_save.item_name=ui_item.name
        self.item_save.current_qty=ui_item.current_qty
        self.item_save.time_now=ui_item.time_now       
        self.item_save.buyer=ui_item.receiver
        self.item_save.shipper=ui_item.shipper     
        self.item_save.row_index= ui_item._row_ 
        self.var_name.set(str(ui_item.name))
        self.var_nowqty.set(str(ui_item.current_qty))        
    
    def lookup(self):
        """
        手動查詢版（按按鈕或 ID 按 Enter）：
        - 若找不到，會彈窗提示使用者該怎麼新增
        """
        pid = normalize_id(self.var_id.get())

        if not pid:
            messagebox.showwarning("提醒", "請輸入產品編號")
            self.ent_id.focus_set()
            return
        
        try:
            work_file, work_list = self.service.get_file_and_list()           
        except NoneListError as e:
            messagebox.showerror("讀取 file 失敗", str(e))
            return  
        mode=self._mode    
        try:
            row=self.service.get_row(work_list,pid,mode)
        except NoItemError :
            #print("IS383",row)             
            self._set_display_unknown("（找不到此編號,請重新輸入）")
            messagebox.showinfo(
                "查詢結果",
                f"找不到 編號：{pid}\n\n若要新增：\n1) 按【進貨】\n2) 輸入數量\n3) 按【確認更新】"
            )
            return
        
       
        try:          
            item = self.service.get_item(work_list,row)       
        except NoItemError:           
            self._set_display_unknown("（找不到此品項）")
            return                                       
                  
        if row is not None:           
           item.row = row  
        #print("UI399")      
        self._set_display_item(pid, item)
    
    def is_positive_int_str(self,s: str) -> bool:
        """
        數量輸入規則（員工只輸數字）：
        - 必須是純數字
        - 且 > 0
        """
        s = (s or "").strip()
        if not re.fullmatch(r"\d+", s):
            return False
        return int(s) > 0
    
    # ============================================================
    # [流程核心-2] 歷史：顯示目前/前一次/前兩次
    # ============================================================
    def show_history(self): 
        """按『歷史』按鈕：開一個小視窗顯示三個版本"""
        pid = normalize_id(self.var_id.get())
        if not pid:
            messagebox.showwarning("提醒", "請先輸入產品編號")
            return

        try:
            workfile, work_list = self.service.get_file_and_list()  ####
        except NoneListError:
            messagebox.showerror("讀取 file 失敗")
            return
        
        mode=self._mode
        try:
            row = self.service.get_row(work_list, pid, mode)
        except NoItemError:
            messagebox.showinfo("歷史", f"找不到編號：{pid}")
            return

        try:   
            #print("G-418-into_get_item")
            item=self.service.get_item(work_list,row)                                             
        except NoItemError:
            self._set_display_unknown("（找不到此品項）")
            return                                                      
        
        name = (str(item.name) or "")
        
        def fmt(q, d):
            # 讓 None / 空值顯示為（空），不然看起來像 bug 
            #print("G394", item)           
            qv = getattr(item, q, None)  
            dv = getattr(item, d, None) 
            #print("G397-qv&dv",qv,dv)
            qv = "（空）" if qv is None or str(qv).strip() == "" else str(qv)
            dv = "（空）" if dv is None or str(dv).strip() == "" else str(dv)
            return qv, dv
        
        now_q, now_d = fmt("current_qty","time_now")        
        p1_q,p1_d = fmt ("last_update","")  
                          

        top = tk.Toplevel(self.root)
        top.title("歷史紀錄")
        top.resizable(False, False)  

        pad = 12
        tk.Label(top, text=f"編號：{pid}", font=("Microsoft JhengHei", 12, "bold"))\
            .grid(row=0, column=0, columnspan=3, padx=pad, pady=(pad, 4), sticky="w")
        tk.Label(top, text=f"品名：{name}", font=("Microsoft JhengHei", 12))\
            .grid(row=1, column=0, columnspan=3, padx=pad, pady=(0, 10), sticky="w")

        for c, h in enumerate(["版本", "數量", "日期"]):
            tk.Label(top, text=h, font=("Microsoft JhengHei", 11, "bold"))\
                .grid(row=2, column=c, padx=pad, pady=(0, 6), sticky="w")

        rows = [("目前", now_q, now_d), ("前次", p1_q,p1_d)]
        for i, (ver, q, d) in enumerate(rows, start=3):
            tk.Label(top, text=ver, font=("Microsoft JhengHei", 11))\
                .grid(row=i, column=0, padx=pad, pady=3, sticky="w")
            tk.Label(top, text=q, font=("Consolas", 11))\
                .grid(row=i, column=1, padx=pad, pady=3, sticky="w")
            tk.Label(top, text=d, font=("Consolas", 11))\
                .grid(row=i, column=2, padx=pad, pady=3, sticky="w")

        tk.Button(top, text="關閉", command=top.destroy, width=10)\
            .grid(row=10, column=0, columnspan=3, padx=pad, pady=(10, pad))

    # ============================================================
    # [流程核心-3] 更新：進貨/出貨 + 數量 → 寫回 Excel
    # ============================================================
    def confirm_update(self):  
       
        pid = normalize_id(self.var_id.get())   
    
        if not pid:                                        
            self.msgbox_id_warning() 
            return      
        if self._mode not in ("IN", "OUT"):     
            self.msg_in_or_out_warning()              
            return          
       
        if self.item_save.current_qty > 0:
            current_qty=self.item_save.current_qty 
        else: 
            current_qty=0

        qty_str = (self.var_qty.get() or "").strip()
        qty = int(qty_str)          
        mode=self._mode 
        new_qty =0  
        row=0        
        receiver=""       
        delta = qty if mode == "IN" else -qty  # 進貨: +值 出貨 -值\        
                    
        if not self.is_positive_int_str(qty_str) or qty==0:   
            self.need_positive_warning()         
            return         
        if self.item_save.row_index > 0:
            row=self.item_save.row_index       
                
        if row ==0:
            if delta < 0:
                #print("UI517", row, delta)
                messagebox.showerror("錯誤", "新商品不能出貨")
                return
            item_name = simpledialog.askstring("新增商品", f"找不到 ID：{pid}\n請輸入產品名稱：")
            if not item_name:
                return                                                                                              
        
        # ===== v1.5 出貨必填買貨及出貨人 =====
        receiver = ""                 
        shipper =""
        if self._mode == "OUT":       
            receiver=self.receiver_asking_color()
            if not receiver:
                return
            shipper=self.shipper_asking_color()
            if not shipper:
                return  
        #print("UI540",row, pid)               
        if row==0:
            row = self.item_save.worksheet.max_row + 1
        else:                                                                                                             
            pid= self.item_save.pid            
            item_name= self.item_save.item_name
            current_qty= self.item_save.current_qty           
            row=self.item_save.row_index 

        #print("UI551",row,pid,item_name,qty,current_qty)              
        payload = {
                "pid": pid,
                "qty": qty,
                "name":item_name,
                "receiver":receiver,
                "shipper":shipper,                
            }
        
        #print("🔥 準備呼叫 API")

        if mode=="IN": 
            print("🔥 call IN API")
            response=requests.post(
                "http://127.0.0.1:8000/api/inventory/in",
            json=payload
            )
        else:
            print("🔥 call OUT API")
            response = requests.post(
                "http://127.0.0.1:8000/api/inventory/out",
                json=payload
            )
        
        result = response.json()
        if not result["success"]:
            # 1️⃣ 顯示錯誤
            show_result_error(result["message"])            
            # 2️⃣ 停止流程（超重要）
            return       
       
        show_result_success(result["message"])
        data = json.loads(response.text)
        inner_data = data.get('data')                                     
        print("🔥 API 回傳:", response.status_code, response.text)   
 
        # # ========= UI 用資料（和 Excel 分離） =========
        ui_item.pid=inner_data["pid"]
        ui_item.name=inner_data["name"] 
        ui_item.current_qty= inner_data["current_qty"]                     
        ui_item.time_now=inner_data["time_now"]
        ui_item.receiver=inner_data["buyer"]
        ui_item.last_qty=inner_data["last_update"]
        ui_item.shipper=inner_data["shipper"]
        ui_item._row_ = inner_data["row"]  
                                                  
        self._set_display_item(pid, ui_item)
        self.prior_pid=pid
        self._reset_for_next() 
       
        action = "進貨" if delta > 0 else "出貨"
        extra = f"\n買貨人：{receiver}" if self._mode == "OUT" and receiver else ""         
        
        messagebox.showinfo(
            "完成",
            f"更新成功\n\n編號：{ui_item.pid}\n品名：{ui_item.name}\n"
            f"動作：{action}\n數量：{abs(delta)}\n目前庫存：{ui_item.current_qty}"
            f"{extra}"
        )    
    
        
    import sys
    def _reset_for_next(self): 
        """                              
        更新後 UX：   
        - 清空數量
        - 取消模式（避免下一筆忘了切換造成錯誤）
        - focus 回到 ID，並全選（方便直接打下一個 ID）
        """
        self.var_qty.set("") 
        self.var_id.set("")
        self.item_save.row_index=0
        self._mode = None            
        self._refresh_mode_buttons()
        self.ent_id.focus_set()
        self.ent_id.selection_range(0, tk.END)   
           
    def save_item_information(self, item, row):                                                    
        self.item_save.pid=item.pid                     
        self.item_save.item_name=item.name
        self.item_save.current_qty=item.current_qty
        self.item_save.time_now=item.time_now       
        self.item_save.buyer=item.buyer  
        self.item_save.shipper=item.shipper     
        self.item_save.row_index= row     

    def receiver_asking_color(self):
        self.root.withdraw()
        receiver = ""
        asking_count=0
        while not receiver:            
        # 傳入 綠色 代表收貨   
            receiver = self.custom_askstring("收貨程序", "請輸入買貨人（必填）：", "#E8F5E9")
            asking_count=asking_count+1
            if asking_count >= 3:
                show_custom_error("錯誤","無買貨人此筆交易將不成立")
                break
        self.root.deiconify()
        return receiver.strip()

    def shipper_asking_color(self):
        self.root.withdraw()
        shipper = ""
        asking_count=0
        while not shipper:    
            # 傳入 黃色 代表出貨
            shipper = self.custom_askstring("出貨程序", "請輸入出貨人（必填）：", "#FFF9C4")
            asking_count=asking_count+1
            if asking_count >= 3:
                show_custom_error("錯誤","無出貨人此筆交易將不成立")
                break
        self.root.deiconify()
        return shipper.strip()  
       

    def custom_askstring(self, title, prompt, bg_color):
        # 建立一個置頂的小視窗
        dialog = Toplevel(self.root)
        dialog.title(title)
        
        # --- 置中邏輯開始 ---
        width = 500
        height = 400
        
        # 獲取螢幕解析度
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # 計算置中座標的公式
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 設定視窗大小與位置： "寬x高+左邊距+上邊距"
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    # --- 置中邏輯結束 ---

        dialog.configure(bg=bg_color)
        dialog.grab_set()

        result = {"value": ""}

        def on_confirm():
            result["value"] = entry.get()
            dialog.destroy()

        Label(dialog, text=prompt, bg=bg_color, font=("Arial", 12)).pack(pady=10)
        entry = Entry(dialog, font=("Arial", 14))
        entry.pack(pady=5)
        entry.focus_set()
        
        entry.bind("<Return>", lambda e: on_confirm())
        Button(dialog, text="確定", command=on_confirm, width=10).pack(pady=10)

        self.root.wait_window(dialog)
        return result["value"] # 建議回傳值，方便後續使用
  



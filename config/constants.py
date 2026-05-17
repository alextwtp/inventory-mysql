
# =========================
# [A] 可調設定（你未來最常改的地方）
# =========================


MAIN_FILENAME = "inventory.xlsx"    # Excel 檔名（與 exe 放同資料夾）
LAST_BACKUP="last_backup.xlsx"
SHEET_NAME = "Inventory"             # 工作表名稱
DATE_FMT = "%Y-%m-%d %H:%M:%S"       # 日期格式（存到 Excel 內）
WINDOW_TITLE = "庫存更新系統 v2.1"
LOW_STOCK_THRESHOLD = 5              # 低庫存門檻：<= 5 就顯示紅字警示
AUTO_LOOKUP_DELAY_MS = 300           # ID 輸入後 0.3 秒自動查詢（debounce）


# =========================
# [B] Excel 欄位定義（Excel 的「資料結構」）
# =========================
# 你當初的需求：ID / 品名 / 數量 / 最近修改日期 + 保留前一次
# 我們把「目前」+「前一次」都放同一列，方便查看、不用另外 log
HEADERS = [
    "編號", "品名",
    "目前庫存", "最近更新","買貨人",
    "前次庫存", "出貨人",
]

LOG_COLORS = [
    "FFF2CC",
    "D9EAD3",
    "D0E0E3",
    "FCE5CD",
    "EAD1DC",
    "CFE2F3"
]

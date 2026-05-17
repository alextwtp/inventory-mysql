import pytest
import requests
import sys

def test_stock_short(client): 

    response = client.post(
    "api/inventory/out",
    json={
        "pid": "UUUU",
        "qty": 500,
        "name": "USB",
        "receiver": "Alex",
        "shipper": "John"
    }
)   
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "StockShortError" 


@pytest.fixture
def lock_excel_file():
    if sys.platform != "win32":
        pytest.skip(
            "Windows-only fixture: FileInUseError detection depends on msvcrt and Windows file locking behavior."
        )

    import msvcrt

    file_path = "data/inventory.xlsx"
    # 用 r+ 讀寫模式開啟，確保檔案指標存在
    f = open(file_path, "r+")
    try:
        # 強制獨佔鎖定 1 個位元組（這足以讓 pandas/openpyxl 報 PermissionError）
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        print("\n[系統鎖定] 檔案已成功鎖定，準備測試 409...")
        yield f
    finally:
        # 測試結束，釋放鎖定並關閉
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        f.close()
        print("[系統解鎖] 鎖定已解除。")

def test_file_inuse_error(client, lock_excel_file):   
    response = client.post(
        "api/inventory/in",
        json={
            "pid": "UUUU",
            "qty": 30,
            "name": "USB",
            "receiver": "",
            "shipper": ""
        }
    )       
    assert response.status_code == 409
    assert response.json()["error"] == "FileInuseError"
  
def test_no_item_error(client): 

    response = client.post(
    "api/inventory/out",
    json={
        "pid": "",
        "qty": 30,
        "name": "BAG",
        "receiver": "",
        "shipper": ""
    }
    )   
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "NoItemError"

def test_negative_error(client): 
    response = client.post(
    "api/inventory/in",
    json={
        "pid": "A001",
        "qty": -9999,
        "name": "BAG",
        "receiver": "",
        "shipper": ""
    }
    )  
    assert response.status_code == 422
    error = response.json()["detail"]         
    assert error [0]["loc"] == ["body", "qty"]

def test_url_error(client): 
        test_data = {
                "pid": "A001",
                "qty": 50,
                "name":"NEWMOUSE",
                "receiver":"",
                "shipper":"",                
            }  

         # 假設正確是 /inventory/in，我們故意寫 /inventory/in_error
        response = client.post("api/inventory/innnn", json=test_data)
        
        # 對於找不到的路徑，狀態碼應該是 404
        assert response.status_code == 404     
       
def test_unprocessed_error(client): 
        test_data = {
                "pid": "A001",
                "qty": 50,
                "name": 150,
                "receiver":"",
                "shipper":"",                
            }  
         
        response = client.post("api/inventory/in", json=test_data)
        error = response.json()["detail"]          
        assert response.status_code == 422  
        assert error[0]["loc"] == ["body", "name"]    
                                                         
def test_multiple_errors(client):
    # send an emytp JSON data
    response = client.post("api/inventory/in", json={})

    assert response.status_code == 422
    errors = response.json()["detail"]     
    
    # make sure there are 2 errors
    assert len(errors) == 2 

    #不要太依賴 errors 順序

    locs = [error["loc"] for error in errors]
    assert ["body", "pid"] in locs
    assert ["body", "qty"] in locs

    # if depend on errors' priority    
    # # make sure the first error is related to "pid"
    # assert errors[0]["loc"] == ["body", "pid"]
    
    # # make sure the second error is related to "qty"
    # assert errors[1]["loc"] == ["body", "qty"]

def test_inventory_in_success(client):
    response = client.post(
        "api/inventory/in",
        json={
            "pid": "A001",
            "qty": 10,
            "name": "BAG",
            "receiver": "",
            "shipper": ""
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

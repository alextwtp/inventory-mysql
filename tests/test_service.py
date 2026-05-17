from core.inventory_service import InventoryService
from unittest.mock import MagicMock,patch
from core.item import Item
import pytest
from core.exceptions import (
    NegativeError,
    NoItemError,
    StockShortError,
    UnknownError,    
    NameLackError,
    NoneListError,
    ) 
 
app=InventoryService(repo=None)
      
def test_add_normal():
    new_qty= app.inventory_calculate("IN",10,5)
    assert new_qty == 15
  
def test_decuct_normal():             
    new_qty=app.inventory_calculate("OUT",10,6)    
    assert new_qty==4
     
def test_deduct_to_zero():  
    new_qty=app.inventory_calculate("OUT",10,10)  
    assert new_qty == 0

def test_deduct_more_than_available_raises_error():
    with pytest.raises(StockShortError):
        app.inventory_calculate("OUT", 10, 15)    
    
def test_input_not_positive(): 
    with pytest.raises(NegativeError):
        app.inventory_calculate("IN", 10, -16)

# 這是針對 inventory_calculate 的「一對多」測試
@pytest.mark.parametrize("mode, current, change, expected", [
    ("IN", 100, 50, 150),   # 測進貨
    ("OUT", 100, 30, 70),   # 測出貨
    ("OUT", 100, 100, 0),   # 測剛好扣完
])
def test_calculate_logic(mode, current, change, expected):
    service = InventoryService(repo=MagicMock()) 
    result = service.inventory_calculate(mode, current, change)
    assert result == expected

def test_count_out_name_error():
    service = InventoryService(repo=MagicMock())
    with patch.object(service, 'get_file_and_list', return_value=(None, None)):       
        with pytest.raises(NameLackError, match="出貨必須提供買貨及收貨人姓名"):
            service.inventory_count_out_and_write("A01", 10, "手機", "","出貨人")

def test_stock_short_service():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo) 
   
    mock_repo.ensure_filepath.return_value=None
    mock_repo.file_path.return_value="fake.xlsx"
    mock_repo.load_file_and_list.return_value=("f","s")
    mock_repo.find_row_by_id.return_value=6
    mock_repo.read_item.return_value=MagicMock(current_qty=50)
       
    with pytest.raises(StockShortError):
        service.inventory_count_out_and_write("UUUU",200,"USB","Alex","John")

def test_count_out_success():
    mock_repo = MagicMock()
    mock_repo.load_file_and_list.return_value = ("file", "sheet")    
    mock_repo.find_row_by_id.return_value = 90

    fake_item = Item(
        pid="A001",
        current_qty=65,
        name="itemA",
        buyer="XXXX",
        shipper="WWWW")   
        
    mock_repo.complete_the_write.return_value = fake_item 
    mock_repo.read_item.return_value=fake_item 

    service = InventoryService(repo=mock_repo)     
       
    item:Item=service.inventory_count_out_and_write(
        pid="A001",
        qty=18,
        name="itemA",
        receiver="XXXX",
        shipper="WWWW")   
            
    assert item.current_qty == 65

    mock_repo.complete_the_write.assert_called_once_with(
       "OUT", 90, "itemA", "A001", 65, 18, "XXXX", "WWWW", 47
    ) 

def test_count_out_success_new_qty_is_correct():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    fake_item = Item(
        pid="A001",
        name="itemA",
        current_qty=100,
        buyer="",
        shipper=""
    )

    result_item = Item(
        pid="A001",
        name="itemA",
        current_qty=70,
        buyer="Alex",
        shipper="John"
    )

    mock_repo.load_file_and_list.return_value = ("file", "sheet")
    mock_repo.find_row_by_id.return_value = 6
    mock_repo.read_item.return_value = fake_item
    mock_repo.complete_the_write.return_value = result_item

    result = service.inventory_count_out_and_write(
        pid="A001",
        qty=30,
        name="itemA",
        receiver="Alex",
        shipper="John"
    )

    assert result.current_qty == 70
    mock_repo.complete_the_write.assert_called_once()   


def test_helper_functions():
    mode=""
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)  
    mock_repo.find_row_by_id.return_value = 10 
    assert service.get_row("mock_sheet", "A01",mode) == 10  
    mock_item = MagicMock()
    mock_repo.read_item.return_value = mock_item
    assert service.get_item("mock_sheet", 10) == mock_item

def test_count_in_item_not_found_append_new_row():
    # Arrange
    mock_repo = MagicMock()
    mock_ws = MagicMock()
    mock_ws.max_row = 5

    mock_repo.load_file_and_list.return_value = ("file", mock_ws)
    mock_repo.find_row_by_id.return_value = None

    fake_item = {
        "pid": "UNKNOWN",
        "name": "test",
        "qty": 10,
    }
    mock_repo.complete_the_write.return_value = fake_item

    service = InventoryService(repo=mock_repo)

    # Act
    result = service.inventory_count_in_and_write(
        pid="UNKNOWN",
        qty=10,
        name="test",
        receiver="",
        shipper="",
    )

    # Assert
    mock_repo.find_row_by_id.assert_called_once()
    mock_repo.complete_the_write.assert_called_once()

    # 檢查新列是否為 max_row + 1 = 6
    args, kwargs = mock_repo.complete_the_write.call_args
    assert 6 in args or kwargs.get("row") == 6
    assert result == fake_item

def test_count_in_success():
    mock_repo = MagicMock()

    # 🔥 必加（你現在缺這個）
    mock_repo.load_file_and_list.return_value = ("file", "sheet")
    mock_repo.find_row_by_id.return_value = 100
    fake_item = Item(
        pid="A001",
        current_qty=15,
        name="itemA",        
        buyer="",
        shipper=""
    )

    mock_repo.complete_the_write.return_value = fake_item  
    service = InventoryService(repo=mock_repo)   
    item:Item=service.inventory_count_in_and_write(
        pid="A001",
        qty=10,
        name="itemA",
        receiver="",
        shipper=""
    )       
    assert item.current_qty == 15

def test_count_in_existing_item_reads_old_qty_and_writes_new_qty():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    fake_item = Item(
        pid="A001",
        name="itemA",
        current_qty=10,
        buyer="",
        shipper=""
    )

    mock_repo.load_file_and_list.return_value = ("file", "sheet")
    mock_repo.find_row_by_id.return_value = 5
    mock_repo.read_item.return_value = fake_item

    written_item = Item(
        pid="A001",
        name="itemA",
        current_qty=15,
        buyer="",
        shipper=""
    )
    mock_repo.complete_the_write.return_value = written_item

    result = service.inventory_count_in_and_write(
        pid="A001",
        qty=5,
        name="itemA",
        receiver="",
        shipper=""
    )

    assert result.current_qty == 15
    mock_repo.read_item.assert_called_once_with("sheet", 5)
    mock_repo.complete_the_write.assert_called_once()

def test_count_in_write_fail():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.load_file_and_list.return_value = ("f", "s")      
    mock_repo.complete_the_write.side_effect = Exception("writeError")

    service = InventoryService(repo=mock_repo)
    
    # Act + Assert
    with pytest.raises(Exception):
        item=service.inventory_count_in_and_write(
            pid="A001",
            qty=10,
            name="itemA",
            receiver="",
            shipper=""
        )
   
def test_count_out_item_not_found():

    service = InventoryService(repo=MagicMock())
                    
    with (patch.object(service, 'get_file_and_list', return_value=("f","s")),
         patch.object(service, 'get_row', return_value=None),
         patch.object(service, 'ensure_file_dir_and_path')
    ):
        with pytest.raises(NoItemError):
            service.inventory_count_out_and_write("FAKE_ID", 110, "假貨", "收貨人", "出貨員")
   
def test_prepare_write_logic():
    # 1. 建立假 Repo
    mock_repo = MagicMock()   
        
    fake_item = {
        "編號": "K007",
        "品名": "測試",        
        "目前庫存": 110,
        "最近更新": "2023-10-27",
        "買貨人": "",
        "前次庫存": 100,
        "出貨人": ""
    }
    mock_repo.complete_the_write.return_value = fake_item   
    service = InventoryService(repo=mock_repo)
    item = service.prepare_write('IN', 5, "測試", "K007", 100, 10, "", "", 110)    
    assert item["品名"] == "測試"

def test_service_helpers_real_flow():
    mock_repo = MagicMock()
    mode=""
    service = InventoryService(repo=mock_repo)   
    mock_repo.find_row_by_id.return_value = 5
    assert service.get_row("Sheet", "A01", mode) == 5

    mock_item = MagicMock()
    mock_repo.read_item.return_value = mock_item
    assert service.get_item("Sheet", 5) == mock_item
    mock_repo.read_item.assert_called_once_with("Sheet",5)

def test_ensure_path():
    service = InventoryService(repo=MagicMock())   
    service.ensure_file_dir_and_path() 

def test_calc_line_37():
    service = InventoryService(repo=None)   
    with pytest.raises(UnknownError):
        service.inventory_calculate("ERROR", 100, 10)

def test_get_file_and_list_fail_raises_none_list_error():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    mock_repo.file_path.return_value = "fake.xlsx"
    mock_repo.load_file_and_list.return_value = (None, None)

    with pytest.raises(NoneListError, match="讀取 file 失敗"):
        service.get_file_and_list()
    mock_repo.load_file_and_list.assert_called_once()

def test_make_qty_to_int_success():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)
  
    fake_item = MagicMock()
    fake_item.current_qty = "15"
    mock_repo.qty_to_int.return_value = 15

    qty = service.make_qty_to_int(fake_item)
       
    assert qty == 15
    mock_repo.qty_to_int.assert_called_once_with(fake_item.current_qty)

def test_make_qty_to_int_negative_raises_error():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    fake_item = MagicMock(current_qty="-8")
    mock_repo.qty_to_int.return_value = -8

    with pytest.raises(NegativeError, match="數量不可為負值"):
        service.make_qty_to_int(fake_item)

def test_get_item_read_item_returns_none():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    mock_repo.read_item.return_value = None

    with pytest.raises(NoItemError, match="找不到品項"):
        service.get_item("fake_sheet", 10)   

def test_count_in_negative_qty_raises_error():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    fake_item = Item(
        pid="A001",
        name="itemA",
        current_qty=15,
        buyer="",
        shipper=""
    )

    mock_repo.file_path.return_value = "fake.xlsx"
    mock_repo.load_file_and_list.return_value = ("fake_file", "fake_sheet")
    mock_repo.find_row_by_id.return_value = 10
    mock_repo.read_item.return_value = fake_item

    with pytest.raises(NegativeError, match="數量不可為負值"):
        service.inventory_count_in_and_write(
            pid="A001",
            qty=-5,
            name="itemA",
            receiver="",
            shipper=""
        ) 
    mock_repo.find_row_by_id.assert_called_once()
   
def test_prepare_write_calls_complete_the_write_once():
    mock_repo = MagicMock()
    service = InventoryService(repo=mock_repo)

    fake_item = Item(
        pid="A001",
        name="itemA",
        current_qty=20,
        buyer="",
        shipper=""
    )
    mock_repo.complete_the_write.return_value = fake_item

    item = service.prepare_write(
        "IN", 10, "itemA", "A001", 15, 5, "", "", 20
    )

    assert item == fake_item
    mock_repo.complete_the_write.assert_called_once_with(
        "IN", 10, "itemA", "A001", 15, 5, "", "", 20
    )

def test_count_out_write_fail():
    mock_repo = MagicMock()
    mock_repo.load_file_and_list.return_value = ("f", "s")
    mock_repo.find_row_by_id.return_value = 10

    fake_item = Item(
        pid="A001",
        name="itemA",
        current_qty=500,
        buyer="",
        shipper=""
    )
    mock_repo.read_item.return_value = fake_item
    mock_repo.complete_the_write.side_effect = Exception("writeError")

    service = InventoryService(repo=mock_repo)

    with pytest.raises(Exception, match="writeError"):
        service.inventory_count_out_and_write(
            pid="A001",
            qty=300,
            name="itemA",
            receiver="Alex",
            shipper="John"
        )

    mock_repo.read_item.assert_called_once()
    mock_repo.complete_the_write.assert_called_once()
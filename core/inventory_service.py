from core.item import Item
from config.database import SessionLocal
from core.exceptions import (  
    NegativeError,  
    NoneListError, 
    NoItemError,
    StockShortError,
    UnknownError,    
    NameLackError,  
   )

class InventoryService:
    
    def __init__(self, repo):
        self.repo=repo
        
    def ensure_file_dir_and_path(self):
        self.repo.ensure_filepath(self.repo.file_path()) 
        return                                         
        
    def make_qty_to_int(self,item_id):
        qty=self.repo.qty_to_int(item_id.current_qty)
        if qty < 0:           
            raise NegativeError("""數量不可為負值""")     
        return qty                        

    def get_current_qty(self, pid):
        current_qty = self.repo.load_item()
        return current_qty
    
    def get_file_and_list(self):
        work_file, work_list= self.repo.load_file_and_list(self.repo.file_path())                    
        if not work_file or not work_list:
            raise NoneListError("讀取 file 失敗") 
        return work_file, work_list
    
    def get_row(self, work_list,pid,mode):        
        row=self.repo.find_row_by_id(work_list, pid)       
        return row  

    def get_item(self,work_list,row)-> Item:       
        if row is None: 
            return                                                          
        item:Item=self.repo.read_item(work_list,row)                   
        if not item:            
            raise NoItemError("找不到品項")            
        return item
    
    def inventory_count_in_and_write(self,pid,qty,name,receiver,shipper) ->Item:
        mode="IN"
        current_qty=0
        row=0
        self.ensure_file_dir_and_path()
        work_file,work_list= self.get_file_and_list()        
        row=self.get_row(work_list,pid,mode) 
        #print("IS-56",row)            
                
        if row is None :             
            row= work_list.max_row+1              
        else:  
            item = self.get_item(work_list,row)
            current_qty= item.current_qty            
        receiver=""
        shipper=""                                                                                      
        new_qty = self.inventory_calculate(mode,current_qty,qty)                                 
        item=self.prepare_write (mode,row,name,pid,current_qty,qty,receiver,shipper, new_qty)
        return item 


    def inventory_count_out_and_write(self,pid,qty,name,receiver,shipper)->Item:
        mode="OUT"
        row=0       
        current_qty=0
        
        self.ensure_file_dir_and_path()
        work_file,work_list= self.get_file_and_list()               
        row=self.get_row(work_list,pid, mode)  
        if not row :            
            raise NoItemError("找不到品項")                 
        if not receiver or not shipper:
            raise NameLackError("出貨必須提供買貨及收貨人姓名") 
                                  
        item = self.get_item(work_list,row)              
        current_qty=item.current_qty                                                                                         
        new_qty = self.inventory_calculate(mode,current_qty,qty) 
        item=self.prepare_write (mode,row,name,pid,current_qty,qty,receiver,shipper, new_qty)       
        return item               
    
    def prepare_write (self,mode,row,name,pid,current_qty,qty,receiver,shipper,new_qty)-> Item:                       
        item:Item=self.repo.complete_the_write(mode,row,name,pid,current_qty,qty,receiver,shipper,new_qty)
        print("IS-91",row)
        return item
    

    def inventory_calculate(self,mode: str,current_qty: int, qty: int)-> int:  
        if qty < 0:  
            raise NegativeError("數量不可為負值")
        if mode == "IN":
            new_qty=current_qty + qty            
            return new_qty
        if mode == "OUT":            
            if qty > current_qty:
                raise StockShortError("庫存不足")
            else:               
                new_qty=current_qty - qty                
                return new_qty        
            
        raise UnknownError("未知模式")       
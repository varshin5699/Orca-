from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
from torch import Tensor
import heapq
class Request:
    def __init__(self,**args: Dict[str, Union[str, int, float, bool, torch.Tensor]])->None:
        self.arr_ts = datetime.now(timezone.utc).timestamp()
        self.max_tokens = args.get("max_tokens", None)
        self.current_token_idx = args.get("seq_len", 0)
        self.request_id = args.get("request_id", None)
        self.states = ["INITIATION","RUNNING","INCREMENT","COMPLETED"]
        self.state = self.states[0]
        self.tokens = args.get("input_tokens", [])
    
    def update_token_idx(self):
        self.current_token_idx += 1
    
    def update_state(self, new_state:str)->None:
        self.state = new_state
    
class RequestPool:
    def __init__(self):
        self.initiation_pool: List[Request] = []
        self.increment_pool: List[Request] = []
        ## should the running queue be here or in the engine?
    
    def add_request(self, request: Request)->None:
        heapq.heappush(self.initiation_pool, (request.arr_ts, request))
    
    def move_to_increment_pool(self, request: Request)->None:
        request.update_state("INCREMENT")
        heapq.heappush(self.increment_pool, (request.arr_ts, request))
 
        

from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
from torch import Tensor
import heapq
class Request:
    def __init__(self,**args: Dict[str, Union[str, int, float, bool, Tensor]])->None:
        self.arr_ts = datetime.now(timezone.utc).timestamp()
        self.max_tokens = args.get("max_tokens", None)
        self.current_token_idx = args.get("seq_len", 0)
        self.request_id = args.get("request_id", None)
        self.states = ["INITIATION","RUNNING","INCREMENT","COMPLETED"]
        self.state = self.states[0]
        self.tokens = args.get("input_tokens", [])
        self.model_dim = args.get("model_dim", None)

    def update_tokens(self, new_tokens: Tensor)->None:
        self.tokens.extend(new_tokens)

    def update_token_idx(self):
        self.current_token_idx += 1
    
    def update_state(self, new_state:str)->None:
        self.state = new_state
    
class RequestPool:
    def __init__(self):
        ## implementing 2 separate queues as it is easier to schedule since Orca prefers the prefill of requests over decode while scheduling

        self.initiation_pool: List[Request] = []
        self.increment_pool: List[Request] = []
        ## should the running queue be here or in the engine?
    
    def add_request(self, request: Request)->None:
        heapq.heappush(self.initiation_pool, (request.arr_ts, request))
    
    def move_to_increment_pool(self, request: Request)->None:
        #remove the request from the initiation pool and add to INCREMENT heap
        self.initiation_pool.remove((request.arr_ts, request))
        request.update_state("INCREMENT")
        heapq.heappush(self.increment_pool, (request.arr_ts, request))
        #this function would be called when the INITIATION is completed and returns from the engine.
    
    def complete_request(self, request: Request)->None:
        #remove the request from the increment pool and mark it as completed
        self.increment_pool.remove((request.arr_ts, request))
        request.update_state("COMPLETED")
        ## this function would be called when the INCREMENT is complete, i.e,the request is completed and returns to the entrypoint

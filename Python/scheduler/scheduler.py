from utils.kv_block_allocator import can_allocate_request
from utils.requests_utils import RequestPool, Request   
from utils.model_utils import Model
from typing import List, Tuple
from utils.random_uuid import random_uid
import torch
import asyncio

class Scheduler:
    def __init__(self, max_bs: int, request_pool: RequestPool)->None:
        self.max_bs = max_bs
        self.batch=[]
        self.request_pool = request_pool
        self.batch_id = random_uid()

    async def schedule(self, modelinfo: Model)-> List[Request]:
        #fetch request that aren't in RUNNING (assuming all the completed are swept away)
        #for each request, check if kv would allow
        #if yes, add to batch, mark as running, as well
        #update the GPU memory info after each addition
        #finally return the batch to be run in the engine
        
        self.batch = []
        nt = 0
        for request in self.request_pool.pool:
            if request.state not in ["RUNNING", "COMPLETED"] and can_allocate_request(request, modelinfo, new_tokens=nt):
                self.batch.append(request)
                request.update_state("RUNNING")
                nt += request.max_tokens
                if len(self.batch) >= self.max_bs:
                    break
        return self.batch_id, self.batch
    
## Orca keeps build batches as long as n_batches == n_workers, asynchronously.
        

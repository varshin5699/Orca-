## This python script is used to check if there's enough space on the GPU vRAM to 
## allocate a request based on the number of max_tokens.
from torch import tensor, finfo, iinfo
import torch
from utils.model_utils import Model
from utils.requests_utils import Request

def can_allocate_request(request: Request, modelinfo : Model, delta : float = 0.001, new_tokens :int = 0) -> bool:
    input_tokens = request.get("input_tokens", None)
    if not input_tokens:
        return RuntimeError("No input tokens found in the request.")
    tensor = request.get("input_tokens", None)
    if not tensor:
       return RuntimeError("No input tokens found in the request.") 
    dtype = tensor.dtype
    if dtype.is_floating_point:
        byte_size = torch.finfo(dtype).bits // 8
    else:
        byte_size = torch.iinfo(dtype).bits // 8 ## this also takes care of the torch quantized dtypes
    ##TODO: include packed formats as well

    memory_required = (request.max_tokens + len(input_tokens)) * byte_size * modelinfo.model_dim ## model dim is required to calculate the memory required for the KV cache, which is max_tokens * model_dim * byte_size
    
    free_mem, _ = torch.cuda.mem_get_info(device=modelinfo.device) ## this gives the remaining memory on the GPU in bytes
    return memory_required < free_mem*(1-delta) ## keeping a delta to avoid out of memory errors, as there might be some fragmentation in the GPU memory.
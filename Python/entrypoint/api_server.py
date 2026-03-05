'''
    Involves a get and a post method to handle calls from the client, and running multiple requests at the same time. 
    The generate method abstracts the different iterations of the model, and either streams or provides the full response at the end.
'''
from fastapi import FASTAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
from asyncio import run, gather 
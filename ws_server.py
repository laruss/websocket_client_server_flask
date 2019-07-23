import asyncio
import websockets
from settings import *

connected = set()

async def consumer(message):
    # message in "completed","failed"
    _dict = open_json()
    print(message)
    _dict.update({'status':message})
    save_json(_dict)

async def producer():
    not_calling = True
    while not_calling:
        sleep(1)
        assembly = _get_assembly_num()
        if assembly != '':
            print(assembly)
            not_calling = False
            _set_assembly_num()
    return assembly

def _get_assembly_num():
    _dict = open_json()
    return _dict["assembly"]

def _set_assembly_num():
    _dict = open_json()
    _dict.update({'assembly':''})
    save_json(_dict)

async def producer_handler(websocket, path):
    connected.add(websocket)
    print("Client's connected")
    try:
        while True:
            mes = await producer()
            await websocket.send(mes)
            async for message in websocket:
                await consumer(message)
                break
    finally:
        print("Client's unconnected")
        connected.remove(websocket)

start_server = websockets.serve(producer_handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
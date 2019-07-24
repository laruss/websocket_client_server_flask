import asyncio
import websockets
from settings import *

connected = set()
message_to_send = None

async def consumer(message):
    # message in "completed","failed"
    _dict = open_json()
    print(message)
    _dict.update({'status':message})
    save_json(_dict)

async def producer(websocket):
    global message_to_send
    not_calling = True
    while not_calling:
        sleep(1)
        assembly = _get_assembly_num()
        if assembly != '':
            not_calling = False
            _set_assembly_num()
    try:
        await websocket.send('ping')
    except:
        print('no consumers, failed')
        return None
    return assembly

async def set_no_clients_to(boolean):
    _dict = open_json()
    _dict.update({'no_clients':boolean})
    save_json(_dict)

def _get_assembly_num():
    _dict = open_json()
    return _dict["assembly"]

def _set_assembly_num():
    _dict = open_json()
    _dict.update({'assembly':''})
    save_json(_dict)

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket, path):
    while True:
        mes = await producer(websocket)
        if mes: await websocket.send(mes)
        else: await consumer('failed')
        async for message in websocket:
            await consumer(message)
            break

async def handler(websocket, path):
    connected.add(websocket)
    print('consumer connected')
    await set_no_clients_to(False)
    try:
        await asyncio.wait([producer_handler(websocket, path) for ws in connected])
    finally:
        await consumer('failed')
        await set_no_clients_to(True)
        connected.remove(websocket)
        print('consumer disconnected')


start_server = websockets.serve(handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

# async def main_loop():
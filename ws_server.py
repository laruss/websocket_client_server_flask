import asyncio
import websockets, os
from settings import *
from time import sleep

assembly = ''
test_result = ''
test_request_sent = False
client_connected = False

def error_handler(func):
    async def decorator(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except:
            print("client disconnected")
            return False
    return decorator

class Server:

    def get_port(self):
        return os.getenv('WS_PORT', '8765')

    def get_host(self):
        return os.getenv('WS_HOST', '0.0.0.0')

    def start(self):
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    @error_handler
    async def ping(self, websocket):
        await websocket.send('ping')
        # print('pinged')
        await asyncio.sleep(SECS_TO_PING)
        return True

    @error_handler
    async def send_test_request(self, websocket):
        global test_request_sent
        if assembly and not test_request_sent:
            print("Sending assembly to ws_client")
            await websocket.send(assembly)
            test_request_sent = True
            print("assembly was sent to ws_client")
        return True

    @error_handler
    async def check_test_results(self, websocket):
        global test_result
        if assembly and test_request_sent and not test_result:
            message = await websocket.recv()
            if message != 'pong':
                test_result = message
                print('Test results were recieved :', message)
        return True


    async def handler(self, websocket, path):
        global client_connected
        print("client is connected")
        client_connected = True
        while client_connected:
            client_connected = await self.ping(websocket)
            await asyncio.sleep(0)
            if client_connected:
                client_connected = await self.send_test_request(websocket)
                await self.check_test_results(websocket)


def check_assembly_num():
    global assembly
    _dict = open_json()
    if _dict["assembly"]:
        assembly = _dict["assembly"]
        _dict.update({'assembly':''})
        save_json(_dict)
        print("Assembly in json was changed to", assembly)

def set_test_result():
    global test_result, assembly, test_request_sent
    _dict = open_json()
    _dict.update({'status':test_result})
    save_json(_dict)
    print("test results were wrote to JSON")
    test_result = ''
    test_request_sent = False
    assembly = ''

async def json_handler():
    while True:
        await asyncio.sleep(1)
        if not assembly:
            check_assembly_num()
        else:
            if test_result:
                set_test_result()

async def ws_status_checker():
    global test_result
    while True:
        await asyncio.sleep(2)
        if assembly and not client_connected and not test_request_sent:
            test_result = 'failed'
            print("Client is disconnected, not test_request_sent, test_result set to failed")

if __name__ == '__main__':
  ws = Server()
  loop = asyncio.get_event_loop()
  loop.create_task(json_handler())
  loop.run_until_complete(ws.start())
  loop.create_task(ws_status_checker())
  loop.run_forever()
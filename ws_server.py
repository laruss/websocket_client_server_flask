import asyncio
import websockets, os
from settings import *
from time import sleep
from quart import Quart, request, Response, jsonify

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
        print("Websocket Server is running on {}:{}".format(self.get_host(), self.get_port()))
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

async def ws_status_checker():
    global test_result
    while True:
        await asyncio.sleep(2)
        if assembly and not client_connected and not test_request_sent:
            await asyncio.sleep(5)
            test_result = 'failed'
            print("Client is disconnected, not test_request_sent, test_result set to failed")

# http-server
app = Quart(__name__)

@app.route('/')
async def mainPage():
    return "This is a main page of webserver. Go to /start_tests/?assembly=<assembly_number> to run tests"

@app.route("/start_tests/", methods=['GET'])
async def runTests():
    global assembly, test_result
    secs_passed = 0
    try:
        if client_connected:
            assembly = request.args['assembly']
            resp = Response('success')
            while not test_result:
                await asyncio.sleep(1)
                secs_passed += 1
                if secs_passed > SECS_TO_FAIL_RESPONSE:
                    print('timeout failed')
                    test_result = 'failed'
                    break
                print(secs_passed)
            if test_result == 'failed':
                resp = Response('failed', status=400)
        else:
            resp = Response('failed', status=400)
        test_result = ''
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except KeyError:
        return mainPage()

if __name__ == '__main__':
  ws = Server()
  loop = asyncio.get_event_loop()
  loop.run_until_complete(ws.start())
  loop.create_task(ws_status_checker())
  app.run(port=5001, loop=loop)
#!/usr/bin/env python

import asyncio
import websockets

def run_tests(assembly):
    print("completed")
    return "completed"

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            assembly = await websocket.recv()
            if assembly:
                print(assembly)
                status = run_tests(assembly)
                await websocket.send(status)

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
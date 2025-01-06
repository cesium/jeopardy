import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
import threading
import globals
import time

logging.basicConfig(level=logging.INFO)


class Server:

    def __init__(self):
        self.clients = set()
        
    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')
        with globals.state_condition:
            await ws.send(globals.state.to_JSON())

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            logging.info("trying to send")
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.send_to_clients(message)


async def timerThread(server,counter):
    while True:
        with globals.state_condition:
            globals.state_condition.wait()
            await checkAndSend(server,globals.state)

async def checkAndSend(server,state):
    # check something
    # send message
    logging.info("in check and send")
    await server.send_to_clients(state.to_JSON())

# helper routine to allow thread to call async function
def between_callback(server,counter):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(timerThread(server,counter))
    loop.close()


def websockets_thread(host :str ,port : int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # start server
    server = Server()
    start_server = websockets.serve(server.ws_handler,host,port)
    counter = 0 
    print(f"WS Server running on {host}:{port}")

    # start timer thread
    threading.Thread(target=between_callback,args=(server,counter,)).start()

    # start main event loop
    loop.run_until_complete(start_server)
    loop.run_forever()
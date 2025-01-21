from cortex import Cortex
import asyncio
import keyboard
import sys
import time

class Demo:
    def __init__(self, client_id, client_secret, debug):
        self.client_id = client_id
        self.client_secret = client_secret
        self.debug = debug

        self.token = None
        self.headset_id = None
        self.session_id = None

        self.cortex = Cortex(self.client_id, self.client_secret, self.debug)

    async def setup(self):
        res = await self.cortex.authorize(self.client_id, self.client_secret)
        self.token = res['result']['cortexToken']
        await self.cortex.control_device("refresh")
        res = await self.cortex.query_headsets()
        self.headset_id = res['result'][0]['id']
        await self.cortex.control_device("connect", self.headset_id)

    async def start_stream(self):
        res = await self.cortex.create_session(self.token, "active", self.headset_id)
        self.session_id = res['result']['id']
        await self.cortex.subscribe(self.token, self.session_id, ['pow'])
    
    async def stop_stream(self):
        await self.cortex.update_session(self.token, self.session_id, "close")


async def wait_for_keypress():
    loop = asyncio.get_event_loop()
    # Read input asynchronously
    await loop.run_in_executor(None, sys.stdin.read, 1)

async def main():
    client_id = ''
    client_secret = ''
    debug = True

    demo = Demo(client_id, client_secret, debug)

    print("cortex object created ----------\n")

    await demo.cortex.connect()

    print("CONNECTION ESTABLISHED ----------\n")

    print("starting setup...\n")
    await demo.setup()

    print("PRESS ENTER TO START/STOP STREAM ---------\n")
    await wait_for_keypress()

    print("starting stream...\n")
    await demo.start_stream()

    time.sleep(1)

    await wait_for_keypress()

    await demo.stop_stream()

    print("STREAM STOPPED\n")

    await demo.cortex.close()

    print("CONNECTION CLOSED\n")

asyncio.run(main())

    




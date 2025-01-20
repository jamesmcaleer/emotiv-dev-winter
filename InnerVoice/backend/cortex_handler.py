from cortex import Cortex

class CortexHandler:
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
        await self.cortex.subscribe(self.token, self.session_id, ['met'])
    
    async def stop_stream(self):
        await self.cortex.update_session(self.token, self.session_id, "close")

    
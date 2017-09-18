"""
MIT License

Copyright (c) 2017 verixx / king1600

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import asyncio
import traceback
from pycord.utils import Emitter
from pycord.models import ClientUser
from pycord.utils import Collection
from pycord.utils import get_event_loop
from pycord.api import HttpClient, ShardConnection
from pycord.models import Channel, Guild, Message, User
import time


class Client(Emitter):
    def __init__(self, shard_count=-1):
        super().__init__()
        self.token = ""
        self.is_bot = True
        self.loop = get_event_loop()
        self.running = asyncio.Event()
        self.api = HttpClient(self.loop)
        self.shards = [] if shard_count < 1 else list(range(shard_count))
        self.users = Collection(User)
        self.guilds = Collection(Guild)
        self.channels = Collection(Channel)
        self.messages = Collection(Message)

    def __del__(self):
        if self.is_bot:
            self.close()

    async def _close(self):
        for shard in self.shards:
            await shard.close()
        self.running.set()

    def close(self):
        self.loop.run_until_complete(self._close())

    async def start(self, token, bot):
        self.is_bot = bot
        self.token = self.api.token = token

        # get gateway info
        endpoint = "/gateway"
        if self.is_bot:
            endpoint += "/bot"
        info = await self.api.get(endpoint)
        url = info.get("url")

        # get amouont of shards
        shard_count = info.get("shards", 1)
        if len(self.shards) < 1:
            self.shards = list(range(shard_count))
        else:
            shard_count = len(self.shards)

        # spawn shard connections
        for shard_id in range(shard_count):
            shard = ShardConnection(self, shard_id, shard_count)
            self.shards[shard_id] = shard
            self.loop.create_task(shard.start(url))

        # wait for client to stop running
        await self.running.wait()

    def login(self, token, bot=True):
        self._boot_up_time = time.time()
        try:
            self.loop.run_until_complete(self.start(token, bot))
        except KeyboardInterrupt:
            pass
        except Exception as err:
            traceback.print_exc()
        finally:
            self.close()

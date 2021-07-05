
import discord
import os
import sys
import asyncio
import datetime
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

from utils import url_request



logger = logging.getLogger(__file__)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

class MyClient(discord.Client):

    _BACKGROUND_TASK_TIMER = 300

    # URLS
    _LC_RANDOM_PROBLEM_URL = "https://leetcode.com/problems/random-one-question/all"

    def __init__(self, db_conn_str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect to database
        self.db = create_engine(db_conn_str)

        # create bg_task
        self.bg_tasks = {
            "leetcode_potd" : self.leetcode_potd
        }

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}")

        for bg_name, bg_task in self.bg_tasks.items():
            self.loop.create_task(bg_task())
            logger.info(f"{bg_name} launched.")
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # ping/pong functionality
        if message.content.lower() == "ping":
            await message.channel.send("pong")

        # save msg to database

    async def leetcode_potd(self):
        await self.wait_until_ready()

        # get the lc channel
        channel = self.get_channel(int(os.environ.get("CHANNEL_LEETCODE")))

        # ger random prob
        resp = await url_request(self._LC_RANDOM_PROBLEM_URL)
        potd_url = resp.url
        msg = f"Problem of the Day: \n" + str(potd_url)

        # loop and check for background task
        while not self.is_closed():
            if datetime.datetime.now().hour == 10:
                await channel.send(msg)
            await asyncio.sleep(self._BACKGROUND_TASK_TIMER)
        


if __name__ == "__main__":
    logger.info("Loading environment variables")
    load_dotenv()
    logger.info("Starting application")
    client = MyClient(db_conn_str="sqlite:///dev.db")
    client.run(os.environ.get("TOKEN"))

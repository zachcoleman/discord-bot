
import discord
import os
import sys
import asyncio
import datetime
import logging
import sqlite3
import random

from dotenv import load_dotenv

from queries import CREATE_MESSAGES, SAVE_MSG

# set up logging
logger = logging.getLogger(__file__)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

# registers
from _commands import _COMMAND_REGISTRY
from _background import _BACKGROUND_REGISTRY
from _random_msg import _RANDOM_REGISTRY

class GitBot(discord.Client):

    # imported methods (not necessary cause in registers)
    # from _commands import ping, pong, hist
    # from _background import (
    # assign_pips, leetcode_potd, background_backup_database, prune_database
    # )

    def __init__(self, db_file_pth, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # make in memory database
        self.db_file_pth = db_file_pth
        self.db = sqlite3.connect(self.db_file_pth)

        init_queries = [CREATE_MESSAGES]
        for query in init_queries:
            _ = self.db.execute(query)
        self.db.commit()


    async def on_ready(self):
        logger.info(f"Logged on as {self.user}")
        # after ready, launch background tasks
        await self.launch_background(_BACKGROUND_REGISTRY)


    async def launch_background(self, registry: dict):
        for bg_name, bg_task in _BACKGROUND_REGISTRY.items():
            # generate coroutines for task loop
            def generate_bg_rountine(bg_name, bg_task):
                async def bg_coroutine():
                    await self.wait_until_ready()
                    while not self.is_closed():
                        if bg_task["daily_time"] is not None:
                            if datetime.datetime.now().hour == bg_task["daily_time"]:
                                logger.info(f'Background task: {bg_task["method"].__name__} running')
                                await bg_task["method"](self)
                                logger.info(f'Background task: {bg_task["method"].__name__} done')
                                await asyncio.sleep(3600)
                        else:
                            logger.info(f'Background task: {bg_task["method"].__name__} running')
                            await bg_task["method"](self)
                            logger.info(f'Background task: {bg_task["method"].__name__} done')
                                                    
                        await asyncio.sleep(bg_task["sleep_time"])

                    bg_coroutine.__name__ = bg_name  

                return bg_coroutine

            # generate coroutine and add to loop
            tmp = generate_bg_rountine(bg_name, bg_task)
            self.loop.create_task(tmp())
            logger.info(f'Background task: {bg_task["method"].__name__} launched')
    

    async def on_message(self, message):
        # don't respond to self
        if message.author == self.user:
            await self.save_message(message)
            return
        if not message.content:
            return
        
        # handle helping
        if message.content[0] == "?":
            for name, command_dict in _COMMAND_REGISTRY.items():
                if name == message.content[1:].lower():
                    logger.info(f"Info requested for: {name}")
                    await message.channel.send(f"{name}: \n\t{command_dict['info']}")
        
        # dispatch command to respective method
        elif message.content[0] == "!":
            for name, command_dict in _COMMAND_REGISTRY.items():
                if message.content.split(" ")[0][1:].lower() == name:
                    logger.info(f"Command: {name}")
                    await command_dict["method"](self, message)
        
        # apply random commands
        else:
            p = random.random()
            for name, random_dict in _RANDOM_REGISTRY.items():
                if p < random_dict["prob"]:
                    logger.info(f"Random: {name}")
                    await random_dict["method"](self, message)



        # save msg to database
        await self.save_message(message)


    async def save_message(self, message):
        params = [
            str(message.author.name),
            str(message.author.id),
            str(message.channel),
            str(message.channel.id),
            str(datetime.datetime.now()),
            str(message.content),
        ]
        _ = self.db.execute(SAVE_MSG, params)
        self.db.commit()

        logger.info(f"Saving message to db from {message.author.name}")


    async def backup_database(self):
        logger.info("Backing up database")
        if os.path.exists("./data/backup.db"):
            os.remove("./data/backup.db")
        backup_conn = sqlite3.connect("./data/backup.db")
        self.db.backup(backup_conn)
        logger.info("Database backed up")


if __name__ == "__main__":
    logger.info("Loading environment variables")
    load_dotenv()
    logger.info("Starting application")
    intents = discord.Intents.all()
    client = GitBot(db_file_pth="./data/dev.db", intents=intents)
    client.run(os.environ.get("TOKEN"))




import discord
import os
import sys
import asyncio
import datetime
import logging
import sqlite3
import random

from dotenv import load_dotenv

from utils import url_request
from register import background_register, command_register
from queries import CREATE_MESSAGES, SAVE_MSG, PRUNE_DB, HIST, PIP_CALC

# set up logging
logger = logging.getLogger(__file__)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

# registers
_BACKGROUND_REGISTRY = {}
_COMMAND_REGISTRY = {}

class GitBot(discord.Client):

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
        if message.content[0] == "!":
            for name, command_dict in _COMMAND_REGISTRY.items():
                if message.content.split(" ")[0][1:].lower() == name:
                    logger.info(f"Command: {name}")
                    await command_dict["method"](self, message)

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


    @command_register(_COMMAND_REGISTRY, info="list all the commands")
    async def commands(self, msg):
        cmd_list = []
        for name, command_dict in _COMMAND_REGISTRY.items():
            cmd_list.append(f"{name}: \n\t{command_dict['info']}")
        await msg.channel.send("\n".join(cmd_list))


    @command_register(_COMMAND_REGISTRY, info="you ping, I pong")
    async def ping(self, msg):
        await msg.channel.send("pong")
    

    @command_register(_COMMAND_REGISTRY, info="you pong, I ping")
    async def pong(self, msg):
        await msg.channel.send("ping")


    @command_register(_COMMAND_REGISTRY, info="see user history of msgs (limit 10)")
    async def hist(self, msg):
        
        if len(msg.mentions) < 1:
            return
        
        user_name = msg.mentions[0].name
        res = self.db.execute(
            HIST, 
            [user_name]
        )
        hist_msgs = res.fetchall()

        if hist_msgs:
            await msg.channel.send(
                "\n".join([f"{i+1}) " + m[0] for i, m in enumerate(hist_msgs)])
            )


    @background_register(
        _BACKGROUND_REGISTRY, 
        daily_time=16, 
        sleep_time=3600
    )
    async def assign_pips(self):

        guild = self.get_guild(int(os.environ.get("GUILD_ID")))
        members = await guild.fetch_members().flatten()
        members = [m for m in members if m.name != "GitBot"]
        members_dict = {m.name: m.id for m in members}

        res = self.db.execute(
            PIP_CALC, 
            [str(datetime.datetime.now() - datetime.timedelta(days=1))]
        )
        recent_msgs = res.fetchall()

        member_counts = {k: 0 for k in members_dict.keys()}
        for username, msg in recent_msgs:
            if username in member_counts:
                member_counts[username] += len(msg.split(" "))

        member_counts = sorted([(v, k) for k, v in member_counts.items()])
        lowest_score = member_counts[0][0]
        potential_pip = [m for m in member_counts if m[0] == lowest_score]

        to_pip = [random.choice(potential_pip)]
        to_good_employees = [m for m in member_counts if m[1] != to_pip[0][1]]

        pip_role = guild.get_role(int(os.environ.get("BAD_ROLE")))
        good_employees_role = guild.get_role(int(os.environ.get("GOOD_ROLE")))

        msg = ""
        for mem_score, mem_name in to_pip:
            mem = await guild.fetch_member(members_dict[mem_name])
            await mem.remove_roles(pip_role, good_employees_role)
            await mem.add_roles(pip_role)
            msg += f"<@!{members_dict[mem_name]}> scored {mem_score:,} pts and is on PIP. \n"
        
        for mem_score, mem_name in to_good_employees:
            mem = await guild.fetch_member(members_dict[mem_name])
            await mem.remove_roles(pip_role, good_employees_role)
            await mem.add_roles(good_employees_role)
            msg += f"<@!{members_dict[mem_name]}> scored {mem_score:,} pts and is a Good Employee. \n"
            
        await self.get_channel(int(os.environ.get("CHANNEL_GENERAL"))).send(msg)


    @background_register(
        _BACKGROUND_REGISTRY, 
        daily_time=16, 
        sleep_time=3600
    )
    async def leetcode_potd(self):
        # get the lc channel
        channel = self.get_channel(int(os.environ.get("CHANNEL_LEETCODE")))

        # ger random prob
        resp = await url_request("https://leetcode.com/problems/random-one-question/all")
        potd_url = resp.url
        msg = f"Problem of the Day: \n" + str(potd_url)

        if datetime.datetime.now().hour == 10:
            await channel.send(msg)
            asyncio.sleep(3600)


    @background_register(_BACKGROUND_REGISTRY, sleep_time=86400)
    async def background_backup_database(self):
        await self.backup_database()
    
    
    @background_register(_BACKGROUND_REGISTRY, sleep_time=86400)
    async def prune_database(self):
        self.db.execute(
            PRUNE_DB, 
            [str(datetime.datetime.now() - datetime.timedelta(days=90))]
        )
        self.db.commit()
    


if __name__ == "__main__":
    logger.info("Loading environment variables")
    load_dotenv()
    logger.info("Starting application")
    intents = discord.Intents.all()
    client = GitBot(db_file_pth="./data/dev.db", intents=intents)
    client.run(os.environ.get("TOKEN"))



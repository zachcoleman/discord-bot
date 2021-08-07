
import os
import random
import datetime
from registers import background_register
from utils import url_request
from queries import PIP_CALC, PRUNE_DB
from config import PIP_TIMEFRAME, PTS_MAX_LEN

_BACKGROUND_REGISTRY = {}

# 0 - Monday, 1 - Tuesday, 2 - Wednesday, 3 - Thursday, 4 - Friday
# 5 - Saturday, 6 - Sunday

@background_register(_BACKGROUND_REGISTRY, daily_time=16, days=[1, 4])
async def assign_pips(self):

    guild = self.get_guild(int(os.environ.get("GUILD_ID")))
    members = await guild.fetch_members().flatten()
    members = [m for m in members if m.name != "GitBot"]
    members_dict = {m.name: m.id for m in members}

    res = self.db.execute(
        PIP_CALC, 
        [str(datetime.datetime.now() - datetime.timedelta(days=PIP_TIMEFRAME))]
    )
    recent_msgs = res.fetchall()

    member_counts = {k: 0 for k in members_dict.keys()}
    for username, msg in recent_msgs:
        if username in member_counts:
            member_counts[username] += min(len(msg.split(" ")), PTS_MAX_LEN)

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


@background_register(_BACKGROUND_REGISTRY, daily_time=16)
async def leetcode_potd(self):
    # get the lc channel
    channel = self.get_channel(int(os.environ.get("CHANNEL_LEETCODE")))

    # ger random prob
    resp = await url_request("https://leetcode.com/problems/random-one-question/all")
    potd_url = resp.url
    msg = f"Problem of the Day: \n" + str(potd_url)

    await channel.send(msg)


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

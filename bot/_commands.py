

from registers import command_register
from queries import HIST

_COMMAND_REGISTRY = {}

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

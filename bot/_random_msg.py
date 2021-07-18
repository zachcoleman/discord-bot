
import random 
from registers import random_register

_RANDOM_REGISTRY = {}

@random_register(_RANDOM_REGISTRY, prob=0.01)
async def mock(self, msg):
    msg_str = msg.content.lower()
    if len(msg_str) > 10:  # only mock longer messages
        msg_str = "".join(
            [c.lower() if random.random() < 0.5 else c.upper() for c in msg_str]
        )
        await msg.channel.send(msg_str)



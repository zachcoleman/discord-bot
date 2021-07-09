
###### db mgmt queries ######
CREATE_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
	author TEXT,
    author_id TEXT,
    channel TEXT,
    channel_id TEXT,
    datetime TEXT,
    content TEXT 
);
"""

SAVE_MSG = """
insert into messages 
(author, author_id, channel, channel_id, datetime, content)
values
(?, ?, ?, ?, ?, ?);
"""

PRUNE_DB = """
delete from messages 
where datetime < ?
"""

###### command queries ######
HIST = """
select content from messages
where author = ?
order by datetime desc
limit 10;
"""

PIP_CALC = """
select author, content from messages
where datetime >= ?
"""




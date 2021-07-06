
CREATE_MESSAGES = f"""
CREATE TABLE IF NOT EXISTS messages (
	author TEXT,
    author_id TEXT,
    channel TEXT,
    channel_id TEXT,
    datetime TEXT,
    content TEXT 
);
"""
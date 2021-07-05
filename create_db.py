
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

if __name__ == "__main__":
    load_dotenv()
    connection_str = os.environ.get("DBCONNSTR")



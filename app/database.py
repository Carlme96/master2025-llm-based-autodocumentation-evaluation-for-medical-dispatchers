import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import aiosqlite

DATABASE_URL = "sqlite:///../checkpointer.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


conn = sqlite3.connect("sqlite:///../checkpointer.db", check_same_thread=False)
aioconn = aiosqlite.connect("sqlite:///../checkpointer.db", check_same_thread=False)

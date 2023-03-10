from typing import Optional

from sqlmodel import SQLModel, create_engine, Field, Session

from datetime import datetime

from .models import *

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class Beetl(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    obfuscation: str
    slug: str
    name: Optional[str]
    description: Optional[str]
    target: Optional[int]
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)


class Bid(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_id: int
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

from typing import Optional
from sqlmodel import SQLModel, create_engine, Field, Session, delete, select
from datetime import datetime, timedelta
from beetlapi.database.models import *
import uuid as uuid_pkg
import secrets
import os
sqlite_file_name = "database.db"

if os.environ.get('DEVDEVDEV'):
    sqlite_file_name = "/dev/shm/beetldatabase.sqlite"


sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def delete_entries(table: SQLModel, time_ago: timedelta):

    kill_date = datetime.now() - time_ago

    with Session(engine) as session:

        statement = select(table).where(table.updated <= kill_date)
        old_entries = session.exec(statement).all()

        for entry in old_entries:
            session.delete(entry)


class Beetl(SQLModel, table=True):

    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    secretkey: str = Field(
        default_factory=secrets.token_urlsafe,
        nullable=False,
    )
    obfuscation: str
    slug: str
    title: Optional[str]
    description: Optional[str]
    target: Optional[int]
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    method: str
    beetlmode: str

    # shall not be updated by user
    _ignore_fields = ["obfuscation", "slug", "id", "secretkey", "created", "updated"]


class Bid(SQLModel, table=True):

    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    secretkey: str = Field(
        default_factory=secrets.token_urlsafe,
        nullable=False,
    )
    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_obfuscation: str
    beetl_slug: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    # shall not be updated by user
    _ignore_fields = ["secretkey", "beetl_obfuscation", "beetl_slug", "created", "updated"]

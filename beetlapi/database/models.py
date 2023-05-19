from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
import uuid
from typing import Literal

class BeetlCreate(SQLModel):

    obfuscation: str
    slug: str
    method: str
    beetlmode: Literal['public','private']
    title: Optional[str]
    description: Optional[str]
    target: Optional[int]

class BeetlCreateRead(BeetlCreate):

    secretkey: uuid.UUID

class BeetlPatch(BeetlCreate):

    secretkey: uuid.UUID


class BeetlRead(BeetlCreate):

    created: datetime
    updated: datetime


class BidCreate(SQLModel):
    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_obfuscation: str
    beetl_slug: str


class BidCreateRead(BidCreate):
    secretkey: uuid.UUID
    created: datetime
    updated: datetime


class BidRead(BidCreate):

    created: datetime
    updated: datetime

class BidsRead(SQLModel):

    bids_total: int
    bids: list[BidRead]

class BidPatch(BidCreate):

    secretkey: uuid.UUID


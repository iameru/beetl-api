from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


class BeetlCreate(SQLModel):

    obfuscation: str
    slug: str
    method: str
    beetlmode: str
    name: Optional[str]
    description: Optional[str]
    target: Optional[int]


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

class BidPatch(BidCreate):

    id: str
    bidkey: str


class BidRead(BidCreate):

    id: str
    created: datetime
    updated: datetime

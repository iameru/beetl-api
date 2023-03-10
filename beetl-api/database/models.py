from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


class BeetlCreate(SQLModel):
    obfuscation: str
    slug: str
    name: Optional[str]
    description: Optional[str]
    target: Optional[int]


class BeetlRead(SQLModel):
    id: int
    obfuscation: str
    slug: str
    name: Optional[str]
    description: Optional[str]
    target: Optional[int]
    created: datetime
    updated: datetime


class BidCreate(SQLModel):
    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_id: int


class BidPatch(BidCreate):
    id: int


class BidRead(SQLModel):
    id: int
    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_id: int
    created: datetime
    updated: datetime

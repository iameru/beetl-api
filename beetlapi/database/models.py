from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
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

    secretkey: str

class BeetlPatch(BeetlCreate):

    secretkey: str

class BeetlRead(BeetlCreate):

    created: datetime
    updated: datetime

class BeetlDeleteResponse(BeetlRead):

    pass


class BidCreate(SQLModel):

    name: str
    min: int
    mid: Optional[int]
    max: int
    beetl_obfuscation: str
    beetl_slug: str


import uuid
class BidCreateRead(BidCreate):

    id: uuid.UUID
    secretkey: str
    created: datetime
    updated: datetime


class BidRead(BidCreate):

    id: uuid.UUID
    created: datetime
    updated: datetime

class BidsRead(SQLModel):

    bids_total: int
    bids: list[BidRead]

class BidPatch(BidCreate):

    secretkey: str

class BidDelete(BidPatch):

    pass

class BidDeleteResponse(BidRead):
    
    pass

class BidCheckSecretKey(SQLModel):
    secretkey: str
    id: uuid.UUID

class BidCheckSecretKeyResponse(SQLModel):
    status: Literal['success', 'failed']


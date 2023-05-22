from fastapi import FastAPI, HTTPException

from beetlapi.database.main import (
    Beetl,
    BeetlRead,
    BeetlCreate,
    BeetlPatch,
    BeetlCreateRead,
    BidsRead,
    BidCreate,
    BidCreateRead,
    BidRead,
    Bid,
    BidPatch,
)
from beetlapi.database.main import create_db_and_tables, engine
from sqlmodel import Session, select

from datetime import datetime

app = FastAPI(
    title="beetl-api",
    version="1.0.0",
    description="beetl-api is there to help you with your beetl needs.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/beetl", response_model=BeetlCreateRead)
async def post_beetl(beetl: BeetlCreate):

    with Session(engine) as session:
        beetl = Beetl.from_orm(beetl)
        session.add(beetl)
        session.commit()
        session.refresh(beetl)

    return beetl

def _get_beetl(obfuscation:str, slug:str):
    with Session(engine) as session:
        beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == obfuscation)
            .where(Beetl.slug == slug)
        ).first()

    return beetl

@app.get("/beetl", response_model=BeetlRead)
async def get_beetl(obfuscation: str, slug: str):

    beetl = _get_beetl(obfuscation, slug)
    return beetl

@app.patch("/beetl", response_model=BeetlRead)
async def patch_beetl(data: BeetlPatch):
    with Session(engine) as session:
        beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == data.obfuscation)
            .where(Beetl.slug == data.slug)
            .where(Beetl.secretkey == data.secretkey)
        ).first()

        if not beetl:
            raise HTTPException(status_code=404, detail="Beetl not found")
        if data.secretkey != beetl.secretkey:
            raise HTTPException(status_code=404, detail="Beetl not found")

        data = data.dict(exclude_unset=True)

        for key, value in data.items():
            if key in ["obfuscation", "slug", "id", "secretkey", "created", "updated"]:
                continue

            setattr(beetl, key, value)

        setattr(beetl, "updated", datetime.utcnow())
        session.add(beetl)
        session.commit()
        session.refresh(beetl)

    return beetl

@app.post("/bid", response_model=BidCreateRead)
async def post_bid(data: BidCreate):
    with Session(engine) as session:
        bid = Bid.from_orm(data)
        session.add(bid)
        session.commit()
        session.refresh(bid)

    return bid

@app.get("/bids", response_model=BidsRead)
async def get_bids(obfuscation: str, slug: str):
    with Session(engine) as session:
        bids = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == obfuscation)
            .where(Bid.beetl_slug == slug)
        ).all()
        bids_total = len(bids)

        beetl = _get_beetl(obfuscation, slug)

        if beetl.beetlmode == 'public':
            return {'bids': bids, 'bids_total': bids_total}

        if beetl.beetlmode == 'private':
            return {'bids': [], 'bids_total': bids_total}

@app.patch("/bid", response_model=BidRead)
async def patch_bid(data: BidPatch):
    with Session(engine) as session:
        bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == data.beetl_obfuscation)
            .where(Bid.beetl_slug == data.beetl_slug)
            .where(Bid.secretkey == data.secretkey)
        ).first()

        if not bid:
            raise HTTPException(status_code=404, detail="bid not found")

        data = data.dict(exclude_unset=True)

        for key, value in data.items():
            if key in ["secretkey", "beetl_obfuscation", "beetl_slug", "created", "updated"]:
                continue

            setattr(bid, key, value)

        setattr(bid, "updated", datetime.utcnow())
        session.add(bid)
        session.commit()
        session.refresh(bid)

    return bid

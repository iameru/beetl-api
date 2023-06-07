from beetlapi.database.main import (
    Beetl,
    BeetlRead,
    BeetlCreate,
    BeetlPatch,
    BeetlCreateRead,
    BeetlDeleteResponse,
    BidsRead,
    BidCreate,
    BidCreateRead,
    BidRead,
    Bid,
    BidPatch,
    BidDelete,
    BidDeleteResponse
)
from fastapi import FastAPI, HTTPException
from beetlapi.database.main import create_db_and_tables, engine
from sqlmodel import Session, select, delete
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from os import environ

origins =['https://beetl.xyz']
if environ.get('DEVDEVDEV'):
    origins.append( "http://localhost:3000")

app = FastAPI(
    title="beetl-api",
    version="1.0.0",
    description="beetl-api is there to help you with your beetl needs.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

def _get_beetl(obfuscation:str, slug:str):
    with Session(engine) as session:
        beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == obfuscation)
            .where(Beetl.slug == slug)
        ).first()

    return beetl

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

@app.get("/beetl", response_model=BeetlRead)
async def get_beetl(obfuscation: str, slug: str):

    beetl = _get_beetl(obfuscation, slug)
    return beetl

@app.patch("/beetl", response_model=BeetlRead)
async def patch_beetl(data: BeetlPatch):

    beetl = _get_beetl(data.obfuscation, data.slug)
    if beetl.secretkey == data.secretkey:

        with Session(engine) as session:

            data = data.dict(exclude_unset=True)

            for key, value in data.items():
                if key in Beetl._ignore_fields:
                    continue

                setattr(beetl, key, value)
            setattr(beetl, "updated", datetime.utcnow())

            session.add(beetl)
            session.commit()
            session.refresh(beetl)

            return beetl

    raise HTTPException(status_code=404, detail="Beetl not found")

@app.delete('/beetl', response_model=BeetlDeleteResponse)
async def delete_bid(obfuscation: str, slug: str, secretkey: str):

    beetl = _get_beetl(obfuscation, slug)
    if beetl.secretkey == secretkey:

        with Session(engine) as session:

            [session.delete(bid) for bid in session.exec(
                select(Bid)
                .where(Bid.beetl_obfuscation == obfuscation)
                .where(Bid.beetl_slug == slug)
            ).all()]
            session.delete(beetl)
            session.commit()

        return beetl

    raise HTTPException(status_code=404, detail="Beetl not found")

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
            if key in Bid._ignore_fields:
                continue

            setattr(bid, key, value)

        setattr(bid, "updated", datetime.utcnow())
        session.add(bid)
        session.commit()
        session.refresh(bid)

    return bid

@app.delete('/bid', response_model=BidDeleteResponse)
async def delete_bid(beetl_obfuscation: str, beetl_slug: str, secretkey: str):

    with Session(engine) as session:
        bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == beetl_obfuscation)
            .where(Bid.beetl_slug == beetl_slug)
            .where(Bid.secretkey == secretkey)
        ).first()

        if bid:
            session.delete(bid)
            session.commit()

            return bid

    raise HTTPException(status_code=404, detail="Bid not found")


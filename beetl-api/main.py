from fastapi import FastAPI

from .database.main import Beetl, BeetlRead, BeetlCreate
from .database.main import create_db_and_tables, engine
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


@app.get("/beetl", response_model=BeetlRead)
async def get_beetl(obfuscation: str, slug: str):
    with Session(engine) as session:
        beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == obfuscation)
            .where(Beetl.slug == slug)
        ).first()

    return beetl


@app.post("/beetl", response_model=BeetlRead)
async def post_beetl(beetl: BeetlCreate):
    with Session(engine) as session:
        beetl = Beetl.from_orm(beetl)
        session.add(beetl)
        session.commit()
        session.refresh(beetl)

    return beetl


@app.patch("/beetl")
async def put_beetl(data: BeetlCreate):
    with Session(engine) as session:
        beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == data.obfuscation)
            .where(Beetl.slug == data.slug)
        ).first()

        if not beetl:
            raise HTTPException(status_code=404, detail="Beetl not found")

        data = data.dict(exclude_unset=True)

        for key, value in data.items():
            if key in ["obfuscation", "slug", "id", "created", "updated"]:
                continue

            setattr(beetl, key, value)

        setattr(beetl, "updated", datetime.utcnow())
        session.add(beetl)
        session.commit()
        session.refresh(beetl)

    return beetl

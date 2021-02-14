import yfinance as yf
import models
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import CryptoItem

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# templates = Jinja2Templates(directory="templates")

class CryptoRequest(BaseModel):
    ticker: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def fetch_crypto_data(id: int):
    db = SessionLocal()
    crypto = db.query(CryptoItem).filter(CryptoItem.id == id).first()

    yahoo_data = yf.Ticker(crypto.ticker)

    crypto.ma200 = yahoo_data.info['twoHundredDayAverage']
    crypto.ma50 = yahoo_data.info['fiftyDayAverage']
    crypto.price = yahoo_data.info['previousClose']
    crypto.shortname = yahoo_data.info['shortName']
    # crypto.ticker = yahoo_data.info['symbol']

    db.add(crypto)
    db.commit()

@app.post("/add")
async def create_crypto(input: CryptoRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a new crptocurrency and save in the database.
    """
    crypto = CryptoItem()
    crypto.ticker = input.ticker

    db.add(crypto)
    db.commit()

    background_tasks.add_task(fetch_crypto_data, crypto.id)

    return {
        "code": "success",
        "message": "crypto currency created"
    }


@app.post("/delete")
async def delete_crypto(input: CryptoRequest, db: Session = Depends(get_db)):
    """
    Delete an item from the crypto database.
    """

    delete_item = db.query(CryptoItem).filter(
        CryptoItem.ticker == input.ticker).first()

    db.delete(delete_item)
    db.commit()

    return {
        "code": "success",
        "message": "crypto currency deleted"
    }

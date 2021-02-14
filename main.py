import yfinance as yf
import models
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import StockItem

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class StockRequest(BaseModel):
    ticker: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def fetch_stock_data(id: int):
    db = SessionLocal()
    stock = db.query(StockItem).filter(StockItem.id == id).first()

    yahoo_data = yf.Ticker(stock.ticker)

    stock.ma200 = yahoo_data.info['twoHundredDayAverage']
    stock.ma50 = yahoo_data.info['fiftyDayAverage']
    stock.price = yahoo_data.info['previousClose']
    stock.shortname = yahoo_data.info['shortName']
    try:
        stock.forwardpe = yahoo_data.info['forwardPE']
    except:
        pass

    db.add(stock)
    db.commit()


# async def create_stock(background_tasks: BackgroundTasks):
@app.post("/add")
def create_stock(input: StockRequest, db: Session = Depends(get_db)):
    """
    Create a new stock and save in the database.
    """
    stock = StockItem()
    stock.ticker = input.ticker

    db.add(stock)
    db.commit()

    fetch_stock_data(stock.id)

    return {
        "code": "success",
        "message": "stock created"
    }


@app.post("/delete")
async def delete_stock(input: StockRequest, db: Session = Depends(get_db)):
    """
    Delete an item from the stock database.
    """

    delete_item = db.query(StockItem).filter(
        StockItem.ticker == input.ticker).first()

    db.delete(delete_item)
    db.commit()

    return {
        "code": "success",
        "message": "stock deleted"
    }

import requests
import yfinance as yf
import simplejson as json
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
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
    """
    Import stocks data from yfinance API
    """
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


@app.get("/")
def get_stocks_table(request: Request, db: Session = Depends(get_db)):
    """
    Reads the stocks table from the sqlite database.
    """
    stocks = db.query(StockItem)
    stock_table = {
        "Ticker": [item.ticker for item in stocks],
        "Name": [item.shortname for item in stocks],
        "Price": [item.price for item in stocks],
        "50 Days MA": [item.ma50 for item in stocks],
        "200 Days MA": [item.ma200 for item in stocks],
        "Forward PE": [item.forwardpe for item in stocks]
    }

    # db.close()
    return JSONResponse(content=json.dumps({"stocks": stock_table}))

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


@app.post("/update")
def update_table(input: StockRequest, db: Session = Depends(get_db)):
    """
    Replace existing stocks data with the latest data from yfinance
    """

    engine.execute('DELETE FROM Stocks')  # delete all data from table
    for tick in eval(input.ticker):
        stock = StockItem()
        stock.ticker = tick

        db.add(stock)
        db.commit()

        fetch_stock_data(stock.id)

    return {
        "code": "success",
        "message": "stock table updated"
    }

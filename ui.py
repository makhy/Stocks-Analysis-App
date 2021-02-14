import streamlit as st
import requests
import json
import sys
import yfinance as yf
from database import SessionLocal, engine
from models import CryptoItem
import pandas as pd
import altair as alt

add_backend = "http://127.0.0.1:8000/add"
delete_backend = "http://127.0.0.1:8000/delete"


st.title("Crypto currency screener")


with st.sidebar.beta_expander("Info"):
    st.info(f"""
        Click [here](https://finance.yahoo.com/cryptocurrencies/) for the
        full list of stock tickers on Yahoo Finance.
        """)

input_ticker = st.sidebar.text_input("Add crypto by ticker")
remove_ticker = st.sidebar.text_input("Remove crypto by ticker")

if input_ticker:

    try:
        json_input = json.dumps({"ticker": input_ticker})
        response = requests.post(
            add_backend, data=json_input
        )

        st.write("Crypto currency added to database.")
    except:
        st.write("Ticker isn't correct. Try again.")

if remove_ticker:

    try:
        json_rmv = json.dumps({"ticker": remove_ticker})
        response = requests.post(
            delete_backend, data=json_rmv
        )

        st.write("Crypto currency deleted from database.")
    except:
        st.write("Ticker isn't correct. Try again.")

db = SessionLocal()
cryptos = db.query(CryptoItem)
crypto_table = {
    "Ticker": [item.ticker for item in cryptos],
    "Name": [item.shortname for item in cryptos],
    "Price": [item.price for item in cryptos],
    "50 Days MA": [item.ma50 for item in cryptos],
    "200 Days MA": [item.ma200 for item in cryptos],
}
db.close()
df = pd.DataFrame(crypto_table, columns=[
                  'Ticker', 'Name', 'Price', '50 Days MA', '200 Days MA'])

if st.checkbox("Above 50 Days Moving Average"):
    df = df[df['Price'] > df['50 Days MA']]

if st.checkbox("Above 200 Days Moving Average"):
    df = df[df['Price'] > df['200 Days MA']]


st.write(df)

if df is not None:
    if st.sidebar.checkbox("Show historical prices chart", value=True):
        user_hist_ticker = st.selectbox(
            "Select a ticker", list(df['Ticker']))
        user_hist_period = st.selectbox(
        "Select a period", ['1mo', '3mo', '6mo', '1y']
        )
        hist = yf.Ticker(user_hist_ticker).history(period=user_hist_period)
        hist_mini = hist[['Close', 'Volume']].reset_index()
        hist_mini['Volume'] = hist_mini['Volume'].apply(lambda x : x/1000000)

        base = alt.Chart(hist_mini).encode(x='Date')
        bar = base.mark_bar().encode(y='Volume')

        line = base.mark_line(color='red').encode(y='Close')

        c1 = (bar + line).properties(width=600)

        st.altair_chart(c1, use_container_width=True)

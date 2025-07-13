import os
from kiteconnect import KiteConnect
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class ZerodhaKiteClient:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")
        if not self.api_key or not self.access_token:
            raise ValueError("KITE_API_KEY and KITE_ACCESS_TOKEN must be set in environment variables")
        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)

    def get_instrument_token(self, tradingsymbol, exchange="NSE"):
        instruments = self.kite.instruments(exchange)
        for instrument in instruments:
            if instrument["tradingsymbol"] == tradingsymbol and instrument["exchange"] == exchange:
                return instrument["instrument_token"]
        raise ValueError(f"Instrument {tradingsymbol} not found on {exchange}")

    def fetch_historical_data(self, instrument_token, from_date, to_date, interval="day"):
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, "%Y-%m-%d")

        data = self.kite.historical_data(instrument_token, from_date, to_date, interval)
        return pd.DataFrame(data)

    def place_order(self, tradingsymbol, exchange, transaction_type, quantity,
                    order_type="MARKET", product="CNC", variety="regular", price=None, validity="DAY"):
        params = dict(
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product=product,
            variety=variety,
            validity=validity
        )
        if price is not None:
            params["price"] = price

        try:
            order_id = self.kite.place_order(**params)
            print(f"Order placed successfully. Order ID: {order_id}")
            return order_id
        except Exception as e:
            print(f"Order placement failed: {e}")
            return None

    # Convenience methods for buy and sell
    def buy(self, tradingsymbol, exchange, quantity, **kwargs):
        return self.place_order(tradingsymbol, exchange, "BUY", quantity, **kwargs)

    def sell(self, tradingsymbol, exchange, quantity, **kwargs):
        return self.place_order(tradingsymbol, exchange, "SELL", quantity, **kwargs)

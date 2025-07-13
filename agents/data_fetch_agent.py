from utils.kite_client import ZerodhaKiteClient
from utils.data_store import DataStore
import os

# Initialize the client once
client = ZerodhaKiteClient()
data_store = DataStore(base_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))

# Function to fetch data
def data_fetch(tradingsymbol, exchange, from_date, to_date, interval="day", store=True):
    """
    Fetch historical data for a given symbol and store it in the local database.
    
    Args:
        tradingsymbol (str): Trading symbol (e.g., 'RELIANCE')
        exchange (str): Exchange (e.g., 'NSE')
        from_date (str): Start date in YYYY-MM-DD format
        to_date (str): End date in YYYY-MM-DD format
        interval (str): Data interval ('minute', 'day', 'week', 'month')
        store (bool): Whether to store the data in local database
        
    Returns:
        DataFrame: Historical price data
    """
    # Get instrument token and fetch data from Zerodha
    token = client.get_instrument_token(tradingsymbol, exchange)
    df = client.fetch_historical_data(token, from_date, to_date, interval)
    
    # Store data if requested
    if store and not df.empty:
        # Create a table name based on symbol and interval
        table_name = f"{exchange.lower()}_{tradingsymbol.lower()}_{interval}"
        
        # Save to both Parquet and DuckDB for different query patterns
        parquet_path = data_store.save_to_parquet(df, tradingsymbol, interval)
        duckdb_saved = data_store.save_to_duckdb(df, table_name)
        
        if parquet_path and duckdb_saved:
            print(f"Data stored successfully in {parquet_path} and DuckDB table '{table_name}'")
        else:
            print("Failed to store data")
    
    return df

def get_stored_data(tradingsymbol, exchange=None, interval="day", start_date=None, end_date=None):
    """
    Retrieve stored data from the local database.
    
    Args:
        tradingsymbol (str): Trading symbol (e.g., 'RELIANCE')
        exchange (str, optional): Exchange (e.g., 'NSE')
        interval (str): Data interval ('minute', 'day', 'week', 'month')
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        DataFrame: Historical price data
    """
    # Try to get data from Parquet files
    df = data_store.load_from_parquet(tradingsymbol, interval, start_date, end_date)
    
    if df is not None and not df.empty:
        return df
    
    # If not found in Parquet, try DuckDB
    if exchange:
        table_name = f"{exchange.lower()}_{tradingsymbol.lower()}_{interval}"
        query = f"SELECT * FROM {table_name}"
        
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        try:
            return data_store.query_duckdb(query)
        except Exception as e:
            print(f"Error querying DuckDB: {e}")
            return None
    
    return None

def buy(symbol, exchange, quantity=1, order_type="MARKET", price=None):
    """Placeholder for buying functionality"""
    return f"ORDER-BUY-{symbol}-{quantity}"

def sell(symbol, exchange, quantity=1, order_type="MARKET", price=None):
    """Placeholder for selling functionality"""
    return f"ORDER-SELL-{symbol}-{quantity}"

if __name__ == "__main__":
    # Example usage
    df = data_fetch("RELIANCE", "NSE", "2025-06-01", "2025-07-01")
    print(df.head())
    
    # Example of retrieving stored data
    stored_df = get_stored_data("RELIANCE", "NSE", start_date="2025-06-15")
    if stored_df is not None:
        print("\nRetrieved stored data:")
        print(stored_df.head())
    
    buy_order_id = buy("RELIANCE", "NSE", quantity=1)
    sell_order_id = sell("RELIANCE", "NSE", quantity=1, order_type="LIMIT", price=2500)


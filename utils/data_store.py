# Parquet or DuckDB local data read/write logic

import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from datetime import datetime

class DataStore:
    def __init__(self, base_dir="data"):
        """Initialize the data store with a base directory."""
        self.base_dir = base_dir
        self.parquet_dir = os.path.join(base_dir, "parquet")
        self.duckdb_path = os.path.join(base_dir, "market_data.db")
        
        # Create directories if they don't exist
        os.makedirs(self.parquet_dir, exist_ok=True)
        
        # Initialize DuckDB connection
        self.conn = duckdb.connect(self.duckdb_path)
        
    def save_to_parquet(self, df, symbol, interval="day"):
        """Save DataFrame to Parquet file."""
        if df is None or df.empty:
            return None
            
        # Create folder structure: parquet/interval/symbol/
        symbol_dir = os.path.join(self.parquet_dir, interval, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{symbol}_{timestamp}.parquet"
        filepath = os.path.join(symbol_dir, filename)
        
        # Save to Parquet
        df.to_parquet(filepath, engine="pyarrow", compression="snappy")
        return filepath
    
    def load_from_parquet(self, symbol, interval="day", start_date=None, end_date=None):
        """Load data from Parquet files for a symbol."""
        symbol_dir = os.path.join(self.parquet_dir, interval, symbol)
        
        if not os.path.exists(symbol_dir):
            return None
            
        # Get list of all parquet files for this symbol
        files = [os.path.join(symbol_dir, f) for f in os.listdir(symbol_dir) 
                 if f.endswith('.parquet')]
        
        if not files:
            return None
            
        # Read and concatenate all files
        dfs = []
        for file in files:
            df = pd.read_parquet(file)
            dfs.append(df)
        
        if not dfs:
            return None
            
        result = pd.concat(dfs).drop_duplicates()
        result = result.sort_values('date')
        
        # Filter by date if specified
        if start_date or end_date:
            if 'date' in result.columns:
                if start_date:
                    result = result[result['date'] >= start_date]
                if end_date:
                    result = result[result['date'] <= end_date]
        
        return result
    
    def save_to_duckdb(self, df, table_name):
        """Save DataFrame to DuckDB table."""
        if df is None or df.empty:
            return False
            
        try:
            # Create table if it doesn't exist
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df WHERE 1=0")
            
            # Replace data or append data
            self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            return True
        except Exception as e:
            print(f"Error saving to DuckDB: {e}")
            return False
    
    def query_duckdb(self, query):
        """Execute a SQL query on DuckDB."""
        try:
            return self.conn.execute(query).fetchdf()
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def list_symbols(self, interval="day"):
        """List all available symbols in the Parquet store."""
        if not os.path.exists(os.path.join(self.parquet_dir, interval)):
            return []
        return os.listdir(os.path.join(self.parquet_dir, interval))
    
    def list_duckdb_tables(self):
        """List all tables in DuckDB."""
        return self.conn.execute("SHOW TABLES").fetchdf()
    
    def save_analysis_results(self, df, analysis_name, symbol):
        """Save analysis results to a dedicated table."""
        table_name = f"analysis_{analysis_name}_{symbol}"
        return self.save_to_duckdb(df, table_name)
    
    def get_analysis_results(self, analysis_name, symbol):
        """Retrieve analysis results from a dedicated table."""
        table_name = f"analysis_{analysis_name}_{symbol}"
        query = f"SELECT * FROM {table_name}"
        try:
            return self.query_duckdb(query)
        except:
            return None
    
    def close(self):
        """Close the DuckDB connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()
from utils.kite_client import ZerodhaKiteClient

# Initialize the client once
client = ZerodhaKiteClient()

def buy(tradingsymbol, exchange, quantity, **kwargs):
    return client.buy(tradingsymbol, exchange, quantity, **kwargs)

# Function to place sell order
def sell(tradingsymbol, exchange, quantity, **kwargs):
    return client.sell(tradingsymbol, exchange, quantity, **kwargs)
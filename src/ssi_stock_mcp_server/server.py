import logging
import os
from typing import Dict
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP
from ssi_fc_data import fc_md_client, model
import dotenv

@dataclass
class SSIAuthConfig:
    url: str
    auth_type: str
    consumerID: str
    consumerSecret: str

config = SSIAuthConfig(
    url=os.environ.get("FC_DATA_URL", "https://fc-data.ssi.com.vn/"),
    auth_type=os.environ.get("FC_DATA_AUTH_TYPE", "Bearer"),
    consumerID=os.environ.get("FC_DATA_CONSUMER_ID", ""),
    consumerSecret=os.environ.get("FC_DATA_CONSUMER_SECRET", ""),
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

VALID_MARKETS = ["HOSE", "HNX", "UPCOM", "DER"]
mcp = FastMCP("SSI Stock Market Data MCP Server")

def get_fc_client():
    client = fc_md_client.MarketDataClient(config)
    return client

client = get_fc_client()

def _validate_date_params(symbol: str, from_date: str, to_date: str):
    if not all([symbol, from_date, to_date]):
        raise ValueError("symbol, from_date, and to_date are required")

def _process_securities_response(response: Dict) -> Dict:
    """
    Process and validate the securities API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if not isinstance(response, dict):
        raise ValueError("Invalid response format")
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    return response
    
@mcp.tool(
    description="Get list of securities from a specific market (HOSE/HNX/UPCOM/DER)"
)
async def get_securities_list(market: str, page: int = 1, size: int = 100) -> Dict:
    
    """
    Get list of securities from a specified market.
    
    Args:
        market (str): Market code (HOSE/HNX/UPCOM/DER)
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        
    Returns:
        Dict: A dictionary containing securities information with the following structure:
            {
                "message": str,    # Response message from the API
                "status": int,     # Status code (200 for success)
                "totalRecord": int, # Total number of records available
                "data": [          # List of securities
                    {
                        "market": str,      # Market code (HOSE/HNX/UPCOM/DER)
                        "symbol": str,      # Security code/ticker
                        "StockName": str,   # Company name in Vietnamese
                        "StockEnName": str, # Company name in English
                        # ... possibly other fields
                    },
                    # ... more securities
                ]
            }
            
    Raises:
        ValueError: If the market is not one of the valid markets.
    """
    if market not in VALID_MARKETS:
        raise ValueError("Market must be one of: HOSE, HNX, UPCOM, DER")
    req = model.securities(market, page, size)
    response = client.securities(config, req)
    return _process_securities_response(response)

@mcp.tool(
    description="Get detailed information about a specific security"
)
async def get_securities_details(market: str, symbol: str, page: int = 1, size: int = 100) -> Dict:
    
    """
    Get detailed information about a specific security.
    
    Args:
        market (str): Market code (HOSE/HNX/UPCOM/DER)
        symbol (str): Security symbol/ticker
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        
    Returns:
        Dict: A dictionary containing detailed securities information with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": {
                    "RType": str,               # Type indicator, typically "y"
                    "ReportDate": str,          # Report date in format dd/mm/yyyy
                    "TotalNoSym": int,          # Total number of securities returned
                    "repeatedinfoList": [       # List of security details
                        {
                            "Isin": str,              # ISIN code of the security
                            "Symbol": str,            # Trading symbol listed on exchanges
                            "SymbolName": str,        # Name of the security in Vietnamese
                            "SymbolEngName": str,     # Name of the security in English
                            "SecType": str,           # Security type (ST: Stock, CW: Covered Warrant, 
                                                        # FU: Futures, EF: ETF, BO: BOND, OF: OEF, MF: Mutual Fund)
                            "Exchange": str,          # Exchange where the security is traded
                                                        # (HOSE, HNX, HNXBOND, UPCOM, DER)
                            "Issuer": str,            # Security issuer
                            "LotSize": str,           # Trading lot size of the security
                            "IssueDate": str,         # Issue date
                            "MaturityDate": str,      # Maturity date
                            "FirstTradingDate": str,  # First trading date
                            "LastTradingDate": str,   # Last trading date
                            "ContractMultiplier": str, # Contract multiplier
                            "SettlMethod": int,       # Settlement method
                            "Underlying": str,        # Underlying security
                            "PutOrCall": str,         # Option type
                            "ExercisePrice": str,     # Exercise price (for options, CW)
                            "ExerciseStyle": int,     # Exercise style (for CW, options)
                            "ExcerciseRatio": str,    # Exercise ratio (for CW, options)
                            "ListedShare": str,       # Number of listed shares
                            "TickPrice1": float,      # Starting price range 1 for tick rule
                            "TickIncrement1": float,  # Tick increment for price range 1
                            "TickPrice2": float,      # Starting price range 2 for tick rule
                            "TickIncrement2": float,  # Tick increment for price range 2
                            "TickPrice3": float,      # Starting price range 3 for tick rule
                            "TickIncrement3": float,  # Tick increment for price range 3
                            "TickPrice4": float,      # Starting price range 4 for tick rule
                            "TickIncrement4": float,  # Tick increment for price range 4
                        },
                        # ... more securities details
                    ]
                }
            }
            
    Raises:
        ValueError: If the symbol is not provided.
    """
    if not symbol:
        raise ValueError("Symbol is required")
    if market not in VALID_MARKETS:
        raise ValueError("Market must be one of: HOSE, HNX, UPCOM, DER")
    req = model.securities_details(market, symbol, page, size)
    response = client.securities_details(config, req)
    return _process_securities_details_response(response)

def _process_securities_details_response(response: Dict) -> Dict:
    """
    Process and validate the securities details API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if not isinstance(response, dict):
        raise ValueError("Invalid response format")
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response:
        response["data"] = {"repeatedinfoList": []}
    elif not isinstance(response["data"], dict):
        logger.warning("Data field is not a dictionary, normalizing")
        old_data = response["data"]
        response["data"] = {"repeatedinfoList": []}
        if isinstance(old_data, list) and len(old_data) > 0:
            response["data"]["repeatedinfoList"] = old_data
    if "repeatedinfoList" not in response["data"] or not isinstance(response["data"]["repeatedinfoList"], list):
        response["data"]["repeatedinfoList"] = []
        
    return response

@mcp.tool(
    description="Get components of a specific index"
)
async def get_index_components(index: str = "vn100", page: int = 1, size: int = 100) -> Dict:
    
    """
    Get components (constituent stocks) of a specific index.
    
    Args:
        index (str, optional): Index code. Defaults to "vn100".
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        
    Returns:
        Dict: A dictionary containing index components with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [
                    {
                        "IndexCode": str,       # Index code identifier
                        "IndexName": str,       # Name of the index
                        "Exchange": str,        # Exchange where index is listed (HOSE|HNX)
                        "TotalSymbolNo": int,   # Total number of securities in the index
                        "IndexComponent": [     # List of component securities
                            {
                                "Isin": str,        # ISIN code of the security
                                "StockSymbol": str, # Stock symbol/ticker
                            },
                            # ... more component securities
                        ]
                    },
                    # ... possibly more indexes
                ]
            }
            
    Raises:
        ValueError: If the response format is invalid
    """
    if not index:
        raise ValueError("Index code is required")
    req = model.index_components(index, page, size)
    response = client.index_components(config, req)
    return _process_index_components_response(response)

def _process_index_components_response(response: Dict) -> Dict:
    """
    Process and validate the index components API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    for index_data in response["data"]:
        if "IndexComponent" not in index_data or not isinstance(index_data["IndexComponent"], list):
            index_data["IndexComponent"] = []
        if "IndexComponent" in index_data and "TotalSymbolNo" in index_data:
            actual_count = len(index_data["IndexComponent"])
            if index_data["TotalSymbolNo"] != actual_count:
                logger.warning(f"TotalSymbolNo ({index_data['TotalSymbolNo']}) doesn't match actual count ({actual_count})")
                index_data["TotalSymbolNo"] = actual_count
    return response

@mcp.tool(
    description="Get list of indices for a specific exchange",
)
async def get_index_list(exchange: str = "hnx", page: int = 1, size: int = 100) -> Dict:
    
    """
    Get list of indices for a specific exchange.
    
    Args:
        exchange (str, optional): Exchange code (hnx, hose). Defaults to "hnx".
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        
    Returns:
        Dict: A dictionary containing indices information with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [            # List of indices
                    {
                        "IndexCode": str,    # Index code identifier
                        "IndexName": str,    # Name of the index
                        "Exchange": str,     # Exchange where index is listed (HOSE|HNX)
                    },
                    # ... more indices
                ]
            }
            
    Raises:
        ValueError: If the exchange is invalid or the response format is invalid
    """
    if not exchange:
        raise ValueError("Exchange code is required")
    
    req = model.index_list(exchange, page, size)
    response = client.index_list(config, req)
    return _process_index_list_response(response)

def _process_index_list_response(response: Dict) -> Dict:
    """
    Process and validate the index list API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    for index in response["data"]:
        for field in ["IndexCode", "IndexName", "Exchange"]:
            if field not in index:
                logger.warning(f"Missing field {field} in index data")
                index[field] = ""
        if "Exchange" in index and index["Exchange"] not in ["HOSE", "HNX"]:
            logger.warning(f"Unexpected Exchange value: {index['Exchange']}")
    
    return response

@mcp.tool(
    description="Get daily OHLC data for a specific symbol"
)
async def get_daily_ohlc(symbol: str, from_date: str, to_date: str, 
                        page: int = 1, size: int = 100, ascending: bool = True) -> Dict:
    
    """
    Get daily Open-High-Low-Close (OHLC) data for a specific security symbol.
    
    Args:
        symbol (str): Security symbol/ticker
        from_date (str): Start date in format DD/MM/YYYY
        to_date (str): End date in format DD/MM/YYYY
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        ascending (bool, optional): Sort data in ascending order by date. Defaults to True.
        
    Returns:
        Dict: A dictionary containing OHLC data with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [            # List of OHLC data points
                    {
                        "Symbol": str,       # Security symbol/ticker
                        "TradingDate": str,  # Trading date in format dd/mm/yyyy
                        "Time": int,         # Timestamp
                        "Open": float,       # Opening price
                        "High": float,       # Highest price during the day
                        "Low": float,        # Lowest price during the day
                        "Close": float,      # Closing price
                        "Volume": int,       # Total matched volume (normal orders)
                        "Value": float,      # Total matched value (normal orders)
                    },
                    # ... more OHLC data points
                ]
            }
            
    Raises:
        ValueError: If symbol, from_date, or to_date is not provided.
    """
    _validate_date_params(symbol, from_date, to_date)
    req = model.daily_ohlc(symbol, from_date, to_date, page, size, ascending)
    response = client.daily_ohlc(config, req)
    return _process_ohlc_response(response)

def _process_ohlc_response(response: Dict) -> Dict:
    """
    Process and validate the OHLC API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if not isinstance(response, dict):
        raise ValueError("Invalid response format")
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    for ohlc_data in response["data"]:
        if "Symbol" not in ohlc_data:
            logger.warning("Missing Symbol field in OHLC data")
            ohlc_data["Symbol"] = ""
            
        for field in ["Open", "High", "Low", "Close", "Volume", "Value"]:
            if field not in ohlc_data:
                logger.warning(f"Missing {field} field in OHLC data")
                ohlc_data[field] = 0
            else:
                try:
                    if isinstance(ohlc_data[field], str):
                        if field == "Volume":
                            ohlc_data[field] = int(ohlc_data[field])
                        else:
                            ohlc_data[field] = float(ohlc_data[field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid {field} value: {ohlc_data[field]}")
                    ohlc_data[field] = 0
    
    return response

@mcp.tool(
    description="Get intraday OHLC data for a specific symbol"
)
async def get_intraday_ohlc(symbol: str, from_date: str, to_date: str,
                            page: int = 1, size: int = 100, ascending: bool = True, 
                            interval: int = 1) -> Dict:
    
    """
    Get intraday Open-High-Low-Close (OHLC) data for a specific security symbol by tick data.
    
    Args:
        symbol (str): Security symbol/ticker
        from_date (str): Start date in format DD/MM/YYYY
        to_date (str): End date in format DD/MM/YYYY
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        ascending (bool, optional): Sort data in ascending order by time. Defaults to True.
        interval (int, optional): Time interval in minutes. Defaults to 1.
        
    Returns:
        Dict: A dictionary containing intraday OHLC data with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [            # List of intraday OHLC data points
                    {
                        "Symbol": str,       # Security symbol/ticker
                        "TradingDate": str,  # Trading date in format dd/mm/yyyy
                        "Time": int,         # Timestamp of the tick data
                        "Open": float,       # Opening price for the interval
                        "High": float,       # Highest price during the interval
                        "Low": float,        # Lowest price during the interval
                        "Close": float,      # Closing price for the interval
                        "Volume": int,       # Total matched volume during the interval
                        "Value": float,      # Total matched value during the interval
                    },
                    # ... more intraday OHLC data points
                ]
            }
            
    Raises:
        ValueError: If symbol, from_date, or to_date is not provided.
    """
    _validate_date_params(symbol, from_date, to_date)
    req = model.intraday_ohlc(symbol, from_date, to_date, page, size, ascending, interval)
    response = client.intraday_ohlc(config, req)
    return _process_intraday_ohlc_response(response)

def _process_intraday_ohlc_response( response: Dict) -> Dict:
    """
    Process and validate the intraday OHLC API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    for ohlc_data in response["data"]:
        # Ensure required fields exist with appropriate types
        if "Symbol" not in ohlc_data:
            logger.warning("Missing Symbol field in intraday OHLC data")
            ohlc_data["Symbol"] = ""
        for field in ["Open", "High", "Low", "Close", "Volume", "Value"]:
            if field not in ohlc_data:
                logger.warning(f"Missing {field} field in intraday OHLC data")
                ohlc_data[field] = 0
            else:
                try:
                    if isinstance(ohlc_data[field], str):
                        if field == "Volume":
                            ohlc_data[field] = int(ohlc_data[field])
                        else:
                            ohlc_data[field] = float(ohlc_data[field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid {field} value: {ohlc_data[field]}")
                    ohlc_data[field] = 0
        if "Time" not in ohlc_data:
            logger.warning("Missing Time field in intraday OHLC data")
            ohlc_data["Time"] = 0
        if "TradingDate" not in ohlc_data:
            logger.warning("Missing TradingDate field in intraday OHLC data")
            ohlc_data["TradingDate"] = ""
    
    return response

@mcp.tool(
    description="Get daily index data"
)
async def get_daily_index( from_date: str, to_date: str, channel_id: str = "123",
                        index: str = "VN100", page: int = 1, size: int = 100) -> Dict:
    
    """
    Get daily trading results of a composite index.
    
    Args:
        from_date (str): Start date in format DD/MM/YYYY
        to_date (str): End date in format DD/MM/YYYY
        channel_id (str, optional): Channel ID. Defaults to "123".
        index (str, optional): Index code. Defaults to "VN100".
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        
    Returns:
        Dict: A dictionary containing daily index data with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [            # List of daily index data points
                    {
                        "Indexcode": str,        # Index identifier
                        "IndexValue": float,     # Value of the index
                        "TradingDate": str,      # Trading date in format dd/mm/yyyy
                        "Time": int,             # Timestamp
                        "Change": float,         # Change in index value
                        "RatioChange": float,    # Percentage change
                        "TotalTrade": int,       # Total number of matched orders (both normal and put-through)
                        "Totalmatchvol": int,    # Total matched volume
                        "Totalmatchval": float,  # Total matched value
                        "TypeIndex": str,        # Type of index
                        "IndexName": str,        # Name of the index
                        "Advances": int,         # Total number of advancing stocks
                        "Nochanges": int,        # Total number of unchanged stocks
                        "Declines": int,         # Total number of declining stocks
                        "Ceiling": int,          # Total number of stocks at ceiling price
                        "Floor": int,            # Total number of stocks at floor price
                        "Totaldealvol": int,     # Total volume of put-through orders
                        "Totaldealval": float,   # Total value of put-through orders
                        "Totalvol": int,         # Total volume (both normal and put-through)
                        "Totalval": float,       # Total value (both normal and put-through)
                        "TradingSession": str,   # Trading session
                        "Exchange": str,         # Exchange (HOSE, HNX)
                    },
                    # ... more daily index data points
                ]
            }
            
    Raises:
        ValueError: If from_date or to_date is not provided.
    """
    if not all([from_date, to_date]):
        raise ValueError("from_date and to_date are required")
    req = model.daily_index(channel_id, index, from_date, to_date, page, size, '', '')
    response = client.daily_index(config, req)
    return _process_daily_index_response(response)

def _process_daily_index_response( response: Dict) -> Dict:
    """
    Process and validate the daily index API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if not isinstance(response, dict):
        raise ValueError("Invalid response format")
        
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")
        
    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    for index_data in response["data"]:
        if "Indexcode" not in index_data:
            logger.warning("Missing Indexcode field in daily index data")
            index_data["Indexcode"] = ""
            
        if "IndexName" not in index_data:
            logger.warning("Missing IndexName field in daily index data")
            index_data["IndexName"] = ""

        numeric_fields = [
            "IndexValue", "Change", "RatioChange", "TotalTrade", 
            "Totalmatchvol", "Totalmatchval", "Advances", "Nochanges", 
            "Declines", "Ceiling", "Floor", "Totaldealvol", 
            "Totaldealval", "Totalvol", "Totalval"
        ]
        
        for field in numeric_fields:
            if field not in index_data:
                logger.warning(f"Missing {field} field in daily index data")
                index_data[field] = 0
            else:
                try:
                    if isinstance(index_data[field], str):
                        if field in ["TotalTrade", "Totalmatchvol", "Advances", "Nochanges", 
                                    "Declines", "Ceiling", "Floor", "Totaldealvol", "Totalvol"]:
                            index_data[field] = int(index_data[field])
                        else:
                            index_data[field] = float(index_data[field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid {field} value: {index_data[field]}")
                    index_data[field] = 0
        if "TradingDate" not in index_data:
            logger.warning("Missing TradingDate field in daily index data")
            index_data["TradingDate"] = ""
            
        if "Time" not in index_data:
            logger.warning("Missing Time field in daily index data")
            index_data["Time"] = 0
    
    return response

@mcp.tool(
    description="Get daily stock price data( include volume, value, foreign buy/sell volume, foreign buy/sell value, total buy/sell volume, total buy/sell value) for a specific symbol"
)
async def get_stock_price(symbol: str, from_date: str, to_date: str,
                        page: int = 1, size: int = 100, exchange: str = "hose") -> Dict:
    
    """
    Get daily stock price data for a specific security symbol.
    
    Args:
        symbol (str): Security symbol/ticker
        from_date (str): Start date in format DD/MM/YYYY
        to_date (str): End date in format DD/MM/YYYY
        page (int, optional): Page number for pagination. Defaults to 1.
        size (int, optional): Number of records per page. Defaults to 100.
        exchange (str, optional): Exchange code (hose, hnx). Defaults to "hose".
        
    Returns:
        Dict: A dictionary containing stock price data with the following structure:
            {
                "message": str,      # Response message from the API
                "status": int,       # Status code (200 for success)
                "totalRecord": int,  # Total number of records available
                "data": [            # List of stock price data points
                    {
                        "Tradingdate": str,           # Trading date in format dd/mm/yyyy
                        "Symbol": str,                # Security symbol/ticker
                        "Pricechange": str,           # Price change
                        "Perpricechange": str,        # Percentage price change
                        "Ceilingprice": str,          # Ceiling price
                        "Floorprice": str,            # Floor price
                        "Refprice": str,              # Reference price
                        "Openprice": str,             # Opening price
                        "Highestprice": str,          # Highest price
                        "Lowestprice": str,           # Lowest price
                        "Closeprice": str,            # Closing price
                        "Averageprice": str,          # Average price
                        "Closepriceadjusted": str,    # Adjusted closing price
                        "Totalmatchvol": str,         # Total matched volume
                        "Totalmatchval": str,         # Total matched value
                        "Totaldealval": str,          # Total deal value
                        "Totaldealvol": str,          # Total deal volume
                        "Foreignbuyvoltotal": str,    # Total foreign buying volume
                        "Foreigncurrentroom": str,    # Foreign room
                        "Foreignsellvoltotal": str,   # Total foreign selling volume
                        "Foreignbuyvaltotal": str,    # Total foreign buying value
                        "Foreignsellvaltotal": str,   # Total foreign selling value
                        "Totalbuytrade": str,         # Total buy trades
                        "Totalbuytradevol": str,      # Total buy trade volume
                        "Totalselltrade": str,        # Total sell trades
                        "Totalselltradevol": str,     # Total sell trade volume
                        "Netforeivol": str,           # Net foreign volume
                        "Netforeignval": str,         # Net foreign value
                        "Totaltradedvol": str,        # Total traded volume (including matched, put-through, and odd lots)
                        "Totaltradedvalue": str,      # Total traded value (including matched, put-through, and odd lots)
                        "Time": str,                  # Trading time
                    },
                    # ... more stock price data points
                ]
            }
            
    Raises:
        ValueError: If symbol, from_date, or to_date is not provided.
    """
    _validate_date_params(symbol, from_date, to_date)
    req = model.daily_stock_price(symbol, from_date, to_date, page, size, exchange)
    response = client.daily_stock_price(config, req)
    return _process_stock_price_response(response)

def _process_stock_price_response(response: Dict) -> Dict:
    """
    Process and validate the stock price API response.
    
    Args:
        response (Dict): The raw response from the API
        
    Returns:
        Dict: Processed response with standardized fields
        
    Raises:
        ValueError: If the response format is invalid
    """
    if response.get("status") != 200:
        logger.warning(f"API returned non-success status: {response.get('status')}")

    if "data" not in response or not isinstance(response["data"], list):
        response["data"] = []
    
    for price_data in response["data"]:
        required_fields = [
            "Symbol", "Tradingdate", "Time", "Pricechange", "Perpricechange",
            "Ceilingprice", "Floorprice", "Refprice", "Openprice", "Highestprice",
            "Lowestprice", "Closeprice", "Averageprice", "Closepriceadjusted",
            "Totalmatchvol", "Totalmatchval", "Totaldealval", "Totaldealvol",
            "Foreignbuyvoltotal", "Foreigncurrentroom", "Foreignsellvoltotal",
            "Foreignbuyvaltotal", "Foreignsellvaltotal", "Totalbuytrade",
            "Totalbuytradevol", "Totalselltrade", "Totalselltradevol",
            "Netforeivol", "Netforeignval", "Totaltradedvol", "Totaltradedvalue"
        ]
        
        for field in required_fields:
            if field not in price_data:
                logger.warning(f"Missing {field} field in stock price data")
                price_data[field] = ""
            elif price_data[field] is None:
                price_data[field] = ""
    
    return response


dotenv.load_dotenv()
def setup_environment():
    if dotenv.load_dotenv():
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found or could not load it - using environment variables")
    if not config.consumerID:
        print("ERROR: FC_DATA_CONSUMER_ID environment variable is not set")
        print("Please set it to your FC_DATA_CONSUMER_ID")
        return False
    if not config.consumerSecret:
        print("ERROR: FC_DATA_CONSUMER_SECRET environment variable is not set")
        print("Please set it to your FC_DATA_CONSUMER_SECRET")
        return False
    if config.consumerID and config.consumerSecret:
        print("  Authentication: Using secret key")
    return True

def run_server():
    """Run the SSI Stock MCP server."""
    if not setup_environment():
        sys.exit(1)
    print("Running server in standard mode...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()

import requests
import time
from bigbucks.global_logger import setup_global_logger, log_event,get_logger
import logging
# 设置全局日志配置
# setup_global_logger()
logger = get_logger('alvant')
def get_mkt_price(symbol, sleep_t=1):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+symbol+'&interval=1min&datatype=json&apikey=0NEIE2ZVNWF79A53'
    r = requests.get(url)
    data = r.json()
    t = data['Meta Data']['3. Last Refreshed'] # get latest refreshed time
    result = float(data['Time Series (1min)'][t]['4. close']) # get market price
    func_name = "get_mkt_price"
    log_event(logger, f"Market price retrieved for symbol: {symbol}")
    time.sleep(sleep_t)
    return result

def get_hist_price(symbol, sleep_t = 1):
    func_name = "get_hist_price"
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+symbol+'&outputsize=full'+'&apikey=0NEIE2ZVNWF79A53'
    r = requests.get(url)
    result = r.json()
    log_event(logger, f"History price retrieved for symbol: {symbol}")
    time.sleep(sleep_t)
    return result

def get_stock_overview(symbol, sleep_t = 1):
    func_name = "get_stock_overview"
    url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol='+symbol+'&apikey=CXROL1KGUF8XFO46'
    r = requests.get(url)
    result = r.json()
    log_event(logger, f"Stock overview retrieved for symbol: {symbol}")
    time.sleep(sleep_t)
    return result

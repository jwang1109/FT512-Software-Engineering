import os
import numpy as np
from scipy.stats import gmean
from datetime import datetime, timedelta
import statistics
import sqlite3
from bigbucks.db import insert_asset,get_db

error = "No results found"

def get_adj_close_list(symbol, start_date, end_date):
    
    # if the asset doesn't exist in db, fetch from the API
    db = get_db()
    if db.execute("SELECT * FROM assets WHERE symbol = ?", (symbol,)).fetchone()is None:
        insert_asset(db,symbol)
        db.commit()

    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()


    c.execute("SELECT adjusted_close FROM assets WHERE symbol=? AND date>=? AND date<=?",
            (symbol, start_date, end_date))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return error
    adjusted_close = [float(row[0]) for row in rows]
    return adjusted_close

def cal_rtn(adjusted_close):
    rtn_list = []
    for i in range(1, len(adjusted_close)):
        current_price = float(adjusted_close[i])
        prev_price = float(adjusted_close[i-1])
        daily_return = float((current_price - prev_price) / prev_price)
        rtn_list.append(daily_return)
    return rtn_list

def cal_gmean(rtn_list):
    num_trading_days = 252
    cumulative_return = 1
    for r in rtn_list:
        cumulative_return *= (1 + r)
    annual_geomean = gmean([1+r for r in rtn_list]) ** num_trading_days-1
    return annual_geomean

def cal_sd(rtn_list):
    return statistics.stdev(rtn_list)

def get_stock_info(symbol, start_date, end_date):
    adjusted_close = get_adj_close_list(symbol, start_date, end_date)
    if adjusted_close == error:
        return error, error
    rtn_list = cal_rtn(adjusted_close)
    gmean = cal_gmean(rtn_list)
    sd = cal_sd(rtn_list)
    return gmean, sd

def get_all_stock(start_date, end_date):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT symbol, SUM(shares) FROM users_assets GROUP BY symbol")
    data = c.fetchall()
    if not data:
        return error, error
    total_shares = sum([row[1] for row in data])
    weight_list = [round((row[1] / total_shares), 2) for row in data]
    assets = [[row[0], 0, 0] for row in data]
    for i in assets:
        adjusted_close = get_adj_close_list(i[0], start_date, end_date)
        if adjusted_close == error:
            return error, error
        rtn_list = cal_rtn(adjusted_close)
        gmean = cal_gmean(rtn_list)
        i[1] = round(gmean, 4)
        i[2] = round(cal_sd(rtn_list), 4)
    conn.close()
    return assets, weight_list

def get_all_hold(user_id):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""SELECT symbol, shares FROM users_assets WHERE user_id=?""",(user_id,))
    data = c.fetchall()
    if not data:
        return error, error
    conn.close()
    end_date = datetime.now().date()
    days_ago = end_date - timedelta(days=100)
    start_date = days_ago.isoformat()
    assets = [[symbol[0], 0, 0] for symbol in data]
    for i in assets:
        adjusted_close = get_adj_close_list(str(i[0]), str(start_date), str(end_date))
        if adjusted_close is str:
            return error, error
        rtn_list = cal_rtn(adjusted_close)
        gmean = cal_gmean(rtn_list)
        i[1] = round(gmean, 4)
        i[2] = round(cal_sd(rtn_list), 4)
    total_shares = sum(shares for _, shares in data)
    if total_shares == 0:
        return error, error
    weights = [round(shares / total_shares, 4) for _, shares in data]
    return assets, weights

'''
a, b = get_all_hold(2)
c, d = get_all_hold(1)
print("a is", a, "b is", b, "c is", c, "d is", d)
'''

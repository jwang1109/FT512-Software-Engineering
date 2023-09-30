import functools
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
from flask import Blueprint,flash,g,redirect, render_template, request,url_for, jsonify
from flask_login import current_user,login_manager
from bigbucks.auth import login_required
from bigbucks.db import get_db,insert_asset
from alvant import get_mkt_price, get_hist_price
import pytz


bp = Blueprint('transactions', __name__)

class Transaction:
    def __init__(self, user_id, type, symbol, stockPriceDate, timestmp, pricePerShare, shares):
        self.user_id = user_id
        self.type = type
        self.symbol = symbol
        self.stockPriceDate=stockPriceDate
        self.timestmp = timestmp
        self.pricePerShare = pricePerShare
        self.shares = shares

def is_market_hours():
    timezone = pytz.timezone('US/Eastern')
    current_time = datetime.now(timezone)
    market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= current_time <= market_close


@bp.route('/get_stock_price')
def get_stock_price():
    stock_symbol = request.args.get('symbol')
    stock_price_date = request.args.get('date')
    today = datetime.now().strftime('%Y-%m-%d')
    db = get_db()
    if stock_price_date == today:
        price = get_mkt_price(stock_symbol, sleep_t=1)
    else:
        result = db.execute('SELECT adjusted_close FROM assets WHERE symbol = ? AND date = ?', (stock_symbol, stock_price_date)).fetchone()
        if result:
            price = result['adjusted_close']
        else:
                # Handle the case when no matching row is found (e.g., return an error message or set a default price)
            price = None
    return {'price': price}

def tran_update_db(db, tran_type,stock_symbol,price_per_share,stock_price_date, num_shares,user_id, user_balance, total_price):
    transaction = Transaction(type=tran_type,
                              symbol=stock_symbol,
                              pricePerShare=price_per_share,
                              stockPriceDate=stock_price_date,
                              timestmp=datetime.now(),
                              shares=num_shares,
                              user_id=user_id)
    updated_balance=user_balance-total_price
    updated_balance_formatted="{:.2f}".format(updated_balance)

    # Update transactions table
    db.execute('INSERT INTO transactions (user_id, type, symbol, stockPriceDate, timestmp, pricePerShare, shares) VALUES (?, ?, ?, ?, ?, ?,?)',
            (transaction.user_id,transaction.type, transaction.symbol, transaction.stockPriceDate, transaction.timestmp, transaction.pricePerShare, transaction.shares))
    
    # Update balance table
    db.execute('UPDATE accounts SET balance = ? WHERE user_id = ?', (updated_balance_formatted, user_id))

    # Update users_assets table
    existing_asset = db.execute('SELECT * FROM users_assets WHERE user_id = ? AND symbol = ?', (user_id, stock_symbol)).fetchone()

    if existing_asset:
        # If the user already has an asset for this stock, update the shares
        updated_shares = existing_asset['shares'] + num_shares if tran_type == 'buy' else existing_asset['shares'] - num_shares
        db.execute('UPDATE users_assets SET shares = ? WHERE user_id = ? AND symbol = ?', (updated_shares, user_id, stock_symbol))
        if updated_shares == 0:
            db.execute('DELETE FROM users_assets WHERE user_id = ? AND symbol = ?', (user_id, stock_symbol))
    else:
        # If the user doesn't have an asset for this stock, insert a new row
        db.execute('INSERT INTO users_assets (user_id, symbol, shares) VALUES (?, ?, ?)', (user_id, stock_symbol, num_shares))
        
    # Note that db.commit() should be executed outside the function to ensure the changes will be committed



@bp.route('/transaction',methods=['GET', 'POST'])
@login_required
def transaction():
    db = get_db()
    user_id = g.user['id']
    transactions = db.execute(
        'SELECT id, user_id, symbol, type, stockPriceDate, timestmp, pricePerShare, shares FROM transactions WHERE user_id = ? ORDER BY timestmp DESC',
        (user_id,)
    ).fetchall()
    #if not transactions:
        #flash('No transactions found.', 'info')
    
    error = None
    if request.method == 'POST':
        stock_symbol = request.form['symbol'].upper()
        transaction_type = request.form['type']
        num_shares = int(request.form['shares'])
        stock_price_date = request.form['stock_price_date']

        #update db if the symbol doesn't exist
        if db.execute("SELECT * FROM assets WHERE symbol = ?", (stock_symbol,)).fetchone() is None:
            insert_asset(db,stock_symbol)
            db.commit()
        if stock_price_date != datetime.now().strftime('%Y-%m-%d'):
            result = db.execute('SELECT adjusted_close FROM assets WHERE symbol = ? AND date = ?', (stock_symbol, stock_price_date)).fetchone()
            if result:
                price_per_share = result['adjusted_close']
            else:
                price_per_share = None
                error="price is not available for this date. Please choose another date."
                return render_template('transaction/transaction.html', error=error, transactions=transactions)
        else:
            price_per_share = get_mkt_price(stock_symbol, sleep_t=1)
        #if price_per_share == '':
            #price_per_share = None
        #else:
            #price_per_share = float(price_per_share)
        total_price = price_per_share * num_shares
        user_balance = db.execute('SELECT balance FROM accounts WHERE user_id = ?', (user_id,)).fetchone()["balance"]
        if transaction_type == 'buy':
            if user_balance < total_price:
                error = 'Not enough balance on your accounts. Please check your balance!'
            else:
                market_hours = True
                if not market_hours:
                    error = 'Transaction can only be made during market hours. The market hour is from 9:30 AM to 4 PM.'
                else:
                    tran_update_db(db, 'buy',stock_symbol,price_per_share,stock_price_date,num_shares,user_id, user_balance, total_price)
                    db.commit()
            
        elif transaction_type == 'sell':
            market_hours = True
            if not market_hours:
                    error = 'Transaction can only be made during market hours. The market hour is from 9:30 AM to 4 PM.'
            else:
                owned_shares=db.execute('SELECT shares FROM users_assets WHERE user_id = ? AND symbol = ?', (user_id, stock_symbol)).fetchone()
                if owned_shares and owned_shares['shares']>=num_shares:
                    tran_update_db(db, 'sell',stock_symbol,price_per_share, stock_price_date,num_shares,user_id, user_balance,-total_price)
                    db.commit()
                else:
                    error= "Not enough shares to sell. Please check your accounts and assets before makeing transactions."
            
        else:
            pass
        
        if error:
            return render_template('transaction/transaction.html', error=error, transactions=transactions)
        else:
            transactions = db.execute(
                'SELECT * FROM transactions WHERE user_id = ? ORDER BY timestmp DESC',
                (g.user['id'],)
            ).fetchall()
            return render_template('transaction/transaction.html',transaction=transaction, total_price=total_price,price_per_share=price_per_share,transactions=transactions)
    return render_template('transaction/transaction.html',transactions=transactions)

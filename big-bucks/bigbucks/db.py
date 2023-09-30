import sqlite3
import click
from flask import current_app, g
from .alvant import get_hist_price
from .alvant import get_stock_overview


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def insert_asset(db,symbol):
    data = get_hist_price(symbol,sleep_t = 11)
    overview = get_stock_overview(symbol,sleep_t = 11)
    symbol = data['Meta Data']['2. Symbol']
    for date,price in data['Time Series (Daily)'].items():
        db.execute('INSERT OR REPLACE INTO assets(symbol, date, open, high, low, close, adjusted_close, volume)VALUES(?,?,?,?,?,?,?,?)',(symbol,date,price['1. open'], price['2. high'], price['3. low'],price['4. close'],price['5. adjusted close'],price['6. volume']))
    if symbol != 'SPY':
        db.execute('INSERT OR REPLACE INTO assets_overview(symbol,name,description)VALUES(?,?,?)',(overview['Symbol'],overview['Name'],overview['Description']))


       
        
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    
    init_assets = ['AMZN','MSFT','GOOGL','JPM','NFLX','SPY','META','AAPL','TSLA']
    for asset in init_assets:
        insert_asset(db,asset)
    print("Database Initialized") 
    db.commit()


def update_db(app):
    with app.app_context():
        print("Starting database update...")
        db = get_db()
        
        #get unique symbol from assets table
        
        query = db.execute('SELECT DISTINCT symbol FROM assets')
        assets = [row[0] for row in query.fetchall()]

        #update_db
        for asset in assets:
            insert_asset(db,asset)    
            print(f"{asset} updated")
        print("Daily update Completed")
        db.commit()
    


        
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

import functools
from datetime import datetime
from .portfolio_builder import Portfolio
from .portfolio_tools import get_all_hold
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from bigbucks.auth import login_required
from bigbucks.db import get_db
import pandas as pd
import numpy as np
import plotly.express as px
import logging
from global_logger import get_logger, log_event  #
logger = get_logger('home')

bp = Blueprint("home", __name__, url_prefix="")


@bp.route('/home')
def home():
    log_event(logger, 'Accessing the home page', logging.INFO)
    user_id = g.user['id']
    conn = get_db()
    cursor = conn.cursor()
    balance = conn.execute(("SELECT balance FROM accounts WHERE user_id = ?"), (user_id,)).fetchone()

    assets_held = cursor.execute("SELECT symbol FROM users_assets WHERE user_id = ?", (user_id,)).fetchall()
    # check wether all selected assets are existed in assets table, otherwise update
    for asset in assets_held:
        symbol = asset[0]
        result = conn.execute("SELECT * FROM assets WHERE symbol = ?", (symbol,)).fetchone()
        if result is None:
            insert_asset(symbol)
            conn.commit()

    # Do sum
    # I use last day close price stored in db as price per share as frequent market price API callings are not permitted
    # Need a new
    conn = get_db()
    cursor.execute("""
    SELECT ua.user_id, a.symbol, ao.name, ua.shares, a.adjusted_close
    FROM users_assets ua
    LEFT JOIN (
    SELECT a.symbol, a.adjusted_close
    FROM assets a
    JOIN (
    SELECT symbol, MAX(date) AS max_date
    FROM assets
    GROUP BY symbol
    ) b ON a.symbol = b.symbol AND a.date = b.max_date
    ) a ON ua.symbol = a.symbol
    LEFT JOIN assets_overview ao
    ON ua.symbol = ao.symbol
    WHERE ua.user_id = ?""", (user_id,))
    holdings = cursor.fetchall()

    # Plot piechart
    df_holdings = pd.DataFrame(holdings, columns=['user_id', 'symbol', 'name', 'shares', 'adjusted_close'])
    df_holdings["value"] = df_holdings["shares"] * df_holdings["adjusted_close"]
    df_holdings['total_value'] = df_holdings['shares'] * df_holdings['adjusted_close']
    total_value = df_holdings['value'].sum()
    df_holdings['percent_of_portfolio'] = df_holdings['value'] / total_value * 100
    fig = px.pie(df_holdings, values='percent_of_portfolio', names='symbol', title='Portfolio Holdings')
    plot_html = fig.to_html(full_html=False)
    log_event(logger, 'Pie chart for portfolio holdings generated', logging.INFO)

    # Holding analysis
    assets, weight_list = get_all_hold(user_id)
    if assets == weight_list:
        return render_template('home/home.html', holdings=holdings, balance=balance,
                               error=assets)
    weights = np.array(weight_list)
    port = Portfolio(assets)
    free_risk = 0.0339
    port.build_portfolio(weights, free_risk)
    asset_list = [t[0] for t in port.assets]
    chart = port.chart.to_html(full_html=False)
    log_event(logger, 'Holding analysis chart generated', logging.INFO)
    return render_template('home/home.html', holdings=holdings, plot_html=plot_html, balance=balance,
                           portfolio=port, assets=asset_list, chart=chart)
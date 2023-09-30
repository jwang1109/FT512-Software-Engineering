import numpy as np
from portfolio_builder import Portfolio
from portfolio_tools import get_all_stock
from datetime import datetime
from flask import Blueprint, render_template, request, url_for
from bigbucks.db import get_db
from global_logger import get_logger, log_event
import logging
sy = Blueprint("symbol", __name__, url_prefix="/symbol")
logger = get_logger('symbol')  # Create logger instance

@sy.route('/admin_holdings', methods=['GET', 'POST'])
def admin_holdings():
    log_event(logger, 'Accessing admin holdings', logging.INFO)
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
    else:
        start_date = None
        end_date = None

    cursor = get_db().cursor()

    if start_date and end_date:
        cursor.execute("""
        SELECT ua.user_id, ua.symbol, ao.name, ua.shares, a.adjusted_close
        FROM users_assets ua
        JOIN (
        SELECT symbol, MAX(date) AS max_date, adjusted_close
            FROM assets
            WHERE date BETWEEN ? AND ?
            GROUP BY symbol
        ) a ON ua.symbol = a.symbol
        LEFT JOIN assets_overview ao ON ua.symbol = ao.symbol
        """, (start_date, end_date))
    else:
        cursor.execute("""
        SELECT ua.user_id, ua.symbol, ao.name, ua.shares, a.adjusted_close
        FROM users_assets ua
        JOIN (
        SELECT symbol, MAX(date) AS max_date, adjusted_close
            FROM assets
            GROUP BY symbol
        ) a ON ua.symbol = a.symbol
        LEFT JOIN assets_overview ao ON ua.symbol = ao.symbol
        """)

    holdings = cursor.fetchall()

    return render_template('symbol/admin_holdings.html', holdings=holdings)


# @sy.route('/admin_orders')
# def admin_orders():
#     cursor = get_db().cursor()
#     cursor.execute("""
#     SELECT  t.symbol, ao.name, SUM(CASE WHEN type = 'buy' THEN t.shares ELSE 0 END) as total_bought, SUM(CASE WHEN type = 'sell' THEN t.shares ELSE 0 END) as total_sold
#     FROM transactions t
#     LEFT JOIN assets_overview ao
#     ON t.symbol = ao.symbol
#     WHERE DATE(t.timestmp) = ?
#     GROUP BY t.symbol
#     """,(datetime.now().date(),))
#     orders = cursor.fetchall()
#     return render_template('symbol/admin_orders.html', orders=orders)
@sy.route('/admin_orders', methods=['GET', 'POST'])
def admin_orders():
    cursor = get_db().cursor()
    log_event(logger, 'Accessing admin orders', logging.INFO)

    if request.method == 'POST':

        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor.execute("""
        SELECT  t.symbol, ao.name, SUM(CASE WHEN type = 'buy' THEN t.shares ELSE 0 END) as total_bought, SUM(CASE WHEN type = 'sell' THEN t.shares ELSE 0 END) as total_sold
        FROM transactions t
        LEFT JOIN assets_overview ao
        ON t.symbol = ao.symbol
        WHERE DATE(t.timestmp) BETWEEN ? AND ?
        GROUP BY t.symbol
        """, (start_date, end_date,))

    else:  # When request.method == 'GET'
        cursor.execute("""
        SELECT  t.symbol, ao.name, SUM(CASE WHEN type = 'buy' THEN t.shares ELSE 0 END) as total_bought, SUM(CASE WHEN type = 'sell' THEN t.shares ELSE 0 END) as total_sold
        FROM transactions t
        LEFT JOIN assets_overview ao
        ON t.symbol = ao.symbol
        GROUP BY t.symbol
        """)

    orders = cursor.fetchall()
    return render_template('symbol/admin_orders.html', orders=orders)


@sy.route('/overall_profile', methods=['GET'])
def admin_form():
    log_event(logger, 'Accessing admin profile form', logging.INFO)
    return render_template('symbol/admin_profile.html')

@sy.route('/overall_profile', methods=['POST'])
def admin_profile():
    log_event(logger, 'Accessing admin profile form', logging.INFO)
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    assets, weight_list = get_all_stock(start_date, end_date)
    if assets == weight_list:
        return render_template('symbol/admin_profile.html', error="No results found")
    weights = np.array(weight_list)
    port = Portfolio(assets)
    free_risk = 0.0339
    port.build_portfolio(weights, free_risk)
    asset_list = [t[0] for t in port.assets]
    port_p = port.port_pie.to_html(full_html=False)
    opti_p = port.opti_pie.to_html(full_html=False)
    chart = port.chart.to_html(full_html=False)
    return render_template('symbol/admin_profile.html', portfolio=port, assets=asset_list, chart=chart, port_pie=port_p, opti_pie=opti_p)
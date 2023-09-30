import functools
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from scipy import stats
from flask import Blueprint,flash,g,redirect, render_template, request,url_for, jsonify
from flask_login import current_user,login_manager
from bigbucks.auth import login_required
from bigbucks.db import get_db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from global_logger import get_logger, log_event  # Import logging utilities
import  logging

logger = get_logger('charting')  # Create logger instance
bp = Blueprint('charting', __name__)
@bp.route('/charting',methods=['GET', 'POST'])
@login_required
def charting():
    if request.method == 'POST':
        log_event(logger, 'Generating a chart', logging.INFO)
        stock_symbol = request.form['stock_symbol']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        plot_type = request.form['plot_type']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT date, adjusted_close FROM assets WHERE symbol = ? AND date >= ? AND date <= ?", (stock_symbol, start_date, end_date))
        rows = cur.fetchall()
        data = pd.DataFrame(rows, columns=['date', 'adjusted_close'])
        cur.execute("SELECT date, adjusted_close FROM assets WHERE symbol = 'SPY' AND date >= ? AND date <= ?", (start_date, end_date))
        rows_index = cur.fetchall()
        index_data = pd.DataFrame(rows_index, columns=['date', 'adjusted_close'])

        if plot_type == 'adjusted_closing_price':
            fig = px.line(data, x='date', y='adjusted_close', title=f'Adjusted Closing Price of {stock_symbol.upper()} from {start_date_str} to {end_date_str}')
        
        elif plot_type == 'area_graph':
            fig = px.area(data, x='date', y='adjusted_close', title=f'Area Graph of {stock_symbol.upper()} from {start_date_str} to {end_date_str}')

        elif plot_type == 'daily_return':
            data['simple_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            fig = px.scatter(data, x='date', y='simple_return', title=f'Simple Return of {stock_symbol.upper()} from {start_date_str} to {end_date_str}')
        
        elif plot_type == 'log_return':
            data['log_return'] = np.log(data['adjusted_close'] / data['adjusted_close'].shift(1))
            data.dropna(inplace=True)
            fig = px.scatter(data, x='date', y='log_return', title=f'Log Return of {stock_symbol.upper()} from {start_date_str} to {end_date_str}')
        
        elif plot_type == 'today_vs_yesterday_returns':
            data['simple_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            yesterday_return = data['simple_return'][:-1]
            today_return = data['simple_return'][1:]
            fig = px.scatter(x=yesterday_return, y=today_return, title=f"Today's Returns vs. Yesterday's Returns of {stock_symbol.upper()} from {start_date_str} to {end_date_str}")
            fig.update_layout(xaxis_title="Yesterday's Returns (%)", yaxis_title="Today's Returns (%)")
        
        elif plot_type == 'stock_vs_index_adjusted_close_price':
            fig = px.line()
            fig.add_trace(go.Scatter(x=data['date'], y=data['adjusted_close'], mode='lines', name=f'{stock_symbol.upper()} adjusted closing price'))
            fig.add_trace(go.Scatter(x=index_data['date'], y=index_data['adjusted_close'], mode='lines', name='SPY adjusted closing price'))
            fig.update_layout(title=f"{stock_symbol.upper()} vs. SPY adjusted closing price from {start_date_str} to {end_date_str}")
            fig.update_layout(xaxis_title='Date', yaxis_title='Adjusted Closing Price')

        elif plot_type == 'simple_return':
            data['simple_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            fig = px.histogram(data, x='simple_return', nbins=50, range_x=[-0.1, 0.1], title=f'Simple Return of {stock_symbol.upper()} from {start_date_str} to {end_date_str}')
        
        elif plot_type == 'stock_vs_index_time_series_return':
            data['simple_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            index_data['simple_return']=index_data['adjusted_close'].pct_change()
            index_data.dropna(inplace=True)
            fig = px.line()
            fig.add_trace(go.Scatter(x=data['date'], y=data['simple_return'], mode='lines', name=f'{stock_symbol.upper()} return'))
            fig.add_trace(go.Scatter(x=index_data['date'], y=index_data['simple_return'], mode='lines', name='SPY return'))
            fig.update_layout(title=f"{stock_symbol.upper()} vs. SPY return from {start_date_str} to {end_date_str}")
            fig.update_layout(xaxis_title='Date', yaxis_title='Daily Returns')
        
        elif plot_type == "stock_return_vs_index_return":
            data['simple_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            index_data['simple_return']=index_data['adjusted_close'].pct_change()
            index_data.dropna(inplace=True)
            fig = px.scatter(x=index_data['simple_return'], y=data['simple_return'], title=f"Daily Returns of {stock_symbol.upper()} vs. SPY")
            slope, intercept, r_value, p_value, std_err = stats.linregress(index_data['simple_return'], data['simple_return'])
            line_x = np.linspace(index_data['simple_return'].min(), index_data['simple_return'].max(), 10)
            line_y = slope * line_x + intercept
            fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines', name='Linear Regression'))
            fig.update_layout(xaxis_title='SPY Daily Return', yaxis_title=f"{stock_symbol.upper()} Daily Return")
        elif plot_type == "daily_price_movement":
            start_mask = data["date"] == start_date
            if not start_mask.any():
                flash(f"No data found for {stock_symbol.upper()} on {start_date}.", "warning")
                return redirect(url_for('charting.charting'))
            data['daily_return'] = data['adjusted_close'].pct_change()
            data.dropna(inplace=True)
            index_data['daily_return']=index_data['adjusted_close'].pct_change()
            index_data.dropna(inplace=True)
            data['cumulative_return'] = (1 + data['daily_return']).cumprod()
            index_data['cumulative_return'] = (1 + index_data['daily_return']).cumprod()
            initial_price=1
            data['adj_relative_price'] = data['cumulative_return'] * initial_price
            index_data['adj_relative_price'] = index_data['cumulative_return'] * initial_price
            data['relative_price'] = data['adj_relative_price'] / initial_price
            index_data['relative_price'] = index_data['adj_relative_price'] / initial_price
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['date'], y=data['relative_price'], mode='lines', name=f'{stock_symbol.upper()}'))
            fig.add_trace(go.Scatter(x=index_data['date'], y=index_data['relative_price'], mode='lines', name='SPY'))
            fig.update_layout(title=f"{stock_symbol.upper()} vs. SPY Adjusted Price Movement from {start_date_str} to {end_date_str}")
            fig.update_layout(xaxis_title='Date', yaxis_title='Relative Price')

        plot_html = fig.to_html(full_html=False)
        log_event(logger,
                  f"Generated a {plot_type} chart for {stock_symbol.upper()} from {start_date_str} to {end_date_str}",
                  logging.INFO)
        return render_template('charting.html', plot_html=plot_html)

    return render_template('charting.html')
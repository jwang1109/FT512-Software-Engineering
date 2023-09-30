'''
Protfolio Builder & Efficent Frontier
a legally assets input should be like this:
[(symbol1, rtn, sd), (symbol2, rtn, sd), ...]
a legally weights input should be like this:
weights = np.array([])
'''
import os
import sys
import numpy as np
import itertools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Blueprint,render_template, Flask, request, redirect, url_for
from scipy.optimize import minimize
import plotly.offline as pyo
import plotly.colors as pc
import plotly.graph_objs as go
import plotly.offline as pyo
from portfolio_tools import get_stock_info


bp = Blueprint('portfolio_builder', __name__)

error_msg = "No results found"

class Portfolio:
    def __init__(self, assets, weights=[], cov_matrix=None, port_rtn=None, 
                 port_sdv=None, port_shp=None, port_pie=None, opti_rtn=None, opti_sdv=None, 
                 opti_wgt=None, opti_shp=None, opti_pie=None, chart=None):
        self.assets = assets # 投资组合 [(symbol1, rtn, sd), (symbol2, rtn, sd), ...]
        self.weights = weights # 用户指定投资比重 np.array([0.3, 0.5, 0.2, ...])
        self.cov_matrix = cov_matrix # 该比例下Cov-Matrix np.outer
        self.port_rtn = port_rtn # 该比例下回报率
        self.port_sdv = port_sdv # 该比例下标准差
        self.port_shp = port_shp # 该比例下夏普比
        self.port_pie = port_pie # 该比重饼图
        self.opti_rtn = opti_rtn # 最优比例下回报率
        self.opti_sdv = opti_sdv # 最优比例下标准差
        self.opti_wgt = opti_wgt # 最优比例下资产比重
        self.opti_shp = opti_shp # 最优比例下夏普比
        self.opti_pie = opti_pie # 最优比重饼图
        self.chart = chart # 图表
    
    def drew_chart(self):
        self.chart.show()
    
    def __str__(self):
        return f"Portfolio: \nAssets: {self.assets} \nWeights: {self.weights} \nCovariance Matrix: \n{self.cov_matrix} \nPortfolio Return: {self.port_rtn} \nPortfolio Standard Deviation: {self.port_sdv} \nPortfolio Sharpe Ratio: {self.port_shp} \nOptimal Return: {self.opti_rtn} \nOptimal Standard Deviation: {self.opti_sdv} \nOptimal Weights: {self.opti_wgt} \nOptimal Sharpe Ratio: {self.opti_shp}"
    
    def cal_port_rtn(self, weights, opti=False):
        port_rtn = np.dot(np.array([asset[1] for asset in self.assets]), weights)
        if opti: self.opti_rtn = port_rtn
        else: self.port_rtn = port_rtn

    def cal_port_sdv(self, weights, opti=False):
        port_std_dev = np.sqrt(np.dot(weights, np.dot(self.cov_matrix, weights)))
        if opti: self.opti_sdv = port_std_dev
        else: self.port_sdv = port_std_dev

    def find_covar(self):
        # Extract standard deviations
        std_devs = np.array([asset[2] for asset in self.assets])
        # Calculate covariance matrix
        self.cov_matrix = np.diag(np.power(std_devs, 2))

    def find_opti_wgt(self, risk_free, tol=1e-5):
        assets = self.assets
        # Extract expected returns
        returns = np.array([asset[1] for asset in assets])
        # Define objective function to maximize Sharpe ratio
        def objective(weights):
            port_return = np.dot(returns, weights)
            port_std_dev = np.sqrt(np.dot(weights, np.dot(self.cov_matrix, weights)))
            sharpe_ratio = (port_return-risk_free) / port_std_dev
            return -sharpe_ratio
        # Define constraints: weights must sum to 1
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        # Define bounds: weights must be between 0 and 1
        bounds = [(0, 1) for _ in range(len(assets))]
        # Initialize weights to equal weights
        init_weights = np.array([1 / len(assets) for _ in range(len(assets))])
        # Minimize negative Sharpe ratio
        res = minimize(objective, init_weights, method='SLSQP', bounds=bounds, constraints=constraints, tol=tol)
        # Return optimal weights
        wgt_list = [round(num, 2) for num in res.x.tolist()]
        self.opti_wgt = wgt_list

    def cal_shp(self, risk_free, opti=False):
        if opti: 
            # find the weights first
            Portfolio.find_opti_wgt(self, risk_free)
            # find the assets rtn and sd
            Portfolio.cal_port_rtn(self, self.opti_wgt, opti) # opti = True
            Portfolio.cal_port_sdv(self, self.opti_wgt, opti)
            sharpe_ratio = (self.opti_rtn-risk_free) / self.opti_sdv
            self.opti_shp = sharpe_ratio
        else:
            Portfolio.cal_port_rtn(self, self.weights, opti) # opti = False
            Portfolio.cal_port_sdv(self, self.weights, opti)
            sharpe_ratio = (self.port_rtn-risk_free) / self.port_sdv
            self.port_shp = sharpe_ratio

    def cal_efficient_frontier(self):
        assets = self.assets
        n_assets = len(assets)
        if n_assets<=4:
            weights_range = np.linspace(0, 1, 24)
        elif n_assets<=6:
            weights_range = np.linspace(0, 1, 15)
        elif n_assets<=8:
            weights_range = np.linspace(0, 1, 7)
        else:
            weights_range = np.linspace(0, 1, 4)
        # find all the possible weights combinations
        weight_combinations = itertools.product(weights_range, repeat=n_assets)
        valid_combinations = [weights for weights in weight_combinations if sum(weights) == 1]
        # run over all the weights
        weights_array = np.array(valid_combinations)
        portfolio_return = np.dot(weights_array, [asset[1] for asset in assets])
        cov_matrix = self.cov_matrix
        portfolio_sd = np.sqrt(np.diagonal(weights_array @ cov_matrix @ weights_array.T))
        return portfolio_return, portfolio_sd
    
    def build_port_pie(self):
        self.weights = self.weights.tolist()
        colors = pc.qualitative.Pastel
        data = go.Pie(labels=['Asset {}'.format(i+1) for i in range(len(self.weights))], 
              values=self.weights, 
              hole=.5, 
              marker=dict(colors=colors))
        layout = go.Layout(title='Portfolio Weights')
        fig = go.Figure(data=[data], layout=layout)
        pyo.plot(fig, filename='instance/portfolio_port_pie.html', auto_open=False)
        self.port_pie = fig

    def build_opti_pie(self):
        colors = pc.qualitative.Pastel
        data = go.Pie(labels=['Asset {}'.format(i+1) for i in range(len(self.opti_wgt))], 
              values=self.opti_wgt, 
              hole=.5, 
              marker=dict(colors=colors))
        layout = go.Layout(title='Optimal Weights')
        fig = go.Figure(data=[data], layout=layout)
        pyo.plot(fig, filename='instance/portfolio_opti_pie.html', auto_open=False)
        self.opti_pie = fig

    def build_chart(self):
        portfolio_returns, portfolio_sdvs =self.cal_efficient_frontier()
        # create data traces
        portfolio_trace = go.Scatter(
            x=portfolio_sdvs,
            y=portfolio_returns,
            mode='markers',
            name='Efficient Frontier',
            marker=dict(size=10)
        )
        user_trace = go.Scatter(
            x=[self.port_sdv],
            y=[self.port_rtn],
            mode='markers',
            name='Current Portfolio',
            marker=dict(color='red', size=12, symbol='circle')
        )
        opti_trace = go.Scatter(
            x=[self.opti_sdv],
            y=[self.opti_rtn],
            mode='markers',
            name='Optimal Portfolio',
            marker=dict(color='gold', size=12, symbol='circle')
        )
        user_trace.text = ['Current Portfolio']
        # create layout
        layout = go.Layout(
            xaxis=dict(title='Standard deviation'),
            yaxis=dict(title='Expected return'),
            title='Risk/Return graph for portfolio'
        )
        # create figure
        fig = go.Figure(data=[portfolio_trace, user_trace, opti_trace], layout=layout)
        # plot figure
        pyo.plot(fig, filename='instance/portfolio_chart.html', auto_open=False)
        # set chart
        self.chart = fig

    def build_portfolio(self, weights, risk_free):
        # self.assets is already there
        self.weights = weights # self.weights
        Portfolio.find_covar(self) # cov_matrix
        Portfolio.cal_shp(self, risk_free, False) # port_rtn, port_sdv, port_shp
        Portfolio.cal_shp(self, risk_free, True) # opti_wgt, opti_rtn, opti_sdv, opti_shp
        Portfolio.build_port_pie(self) # port_pie
        Portfolio.build_opti_pie(self) # opti_pie
        Portfolio.build_chart(self) # chart
        self.weights = weights.tolist()

@bp.route('/portfolio', methods=['GET'])
def portfolio_form():
    return render_template('portfolio/portfolio_builder.html')

@bp.route('/portfolio', methods=['POST'])
def builder():
    # Retrieve the form data
    num_assets = int(request.form['num_assets'])
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    assets = []
    weights = np.array([])
    for i in range(num_assets):
        symbol = request.form['symbol_{}'.format(i)].upper()
        weight = float(request.form['weight_{}'.format(i)]) / 100.0
        gmean, sd = get_stock_info(symbol, start_date, end_date)
        if (error_msg == gmean) or (error_msg == sd):
            return render_template('portfolio/portfolio_builder.html', error="No results found")
        assets.append([symbol, gmean, sd])
        weights = np.append(weights, weight)
    free_risk = 0.0339
    # Calculate the portfolio
    port = Portfolio(assets)
    port.build_portfolio(weights, free_risk)
    asset_list = [t[0] for t in port.assets]
    # Convert chart to HTML
    port_p = port.port_pie.to_html(full_html=False)
    opti_p = port.opti_pie.to_html(full_html=False)
    chart = port.chart.to_html(full_html=False)
    # Render the portfolio result template with the portfolio information and chart
    return render_template('portfolio/portfolio_builder.html', portfolio=port, assets=asset_list, chart=chart, port_pie=port_p, opti_pie=opti_p)
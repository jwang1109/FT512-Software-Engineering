import math
from flask import(
    request, Blueprint,render_template
)
from flaskr.db import get_db
import plotly.graph_objs as go
import plotly.offline as opy

bp = Blueprint('examples', __name__, url_prefix='/examples', static_url_path='/static')



@bp.route('/statement')
def statement():
    total_amount = 0
    volume_credits = 0
    invoice ={
        "customer": "BigCo",
        "performances": [
            {
                "playID": "hamlet",
                "audience": 55
            },
            {
                "playID": "as-like",
                "audience": 35
            },
            {
                "playID": "othello",
                "audience": 40
            }
        ]
    }
    plays = {
        "hamlet": {"name": "Hamlet", "type": "tragedy"},
        "as-like": {"name": "As You Like It", "type": "comedy"},
        "othello": {"name": "Othello", "type": "tragedy"}
    }
    result = f'Statement for {invoice["customer"]}\n'

    def format_as_dollars(amount):
        return f"${amount:0,.2f}"

    for perf in invoice['performances']:
        play = plays[perf['playID']]
        if play['type'] == "tragedy":
            this_amount = 40000
            if perf['audience'] > 30:
                this_amount += 1000 * (perf['audience'] - 30)
        elif play['type'] == "comedy":
            this_amount = 30000
            if perf['audience'] > 20:
                this_amount += 10000 + 500 * (perf['audience'] - 20)

            this_amount += 300 * perf['audience']

        else:
            raise ValueError(f'unknown type: {play["type"]}')

        # add volume credits
        volume_credits += max(perf['audience'] - 30, 0)
        # add extra credit for every ten comedy attendees
        if "comedy" == play["type"]:
            volume_credits += math.floor(perf['audience'] / 5)
        # print line for this order
        result += f' {play["name"]}: {format_as_dollars(this_amount/100)} ({perf["audience"]} seats)\n'
        total_amount += this_amount

    result += f'Amount owed is {format_as_dollars(total_amount/100)}\n'
    result += f'You earned {volume_credits} credits\n'
    return render_template('examples/statement.html',result = result)


@bp.route('/stockchart',methods =["GET","POST"])
def stockchart():
    result = []
    if request.method =='POST':
        stock_symbol = request.form['stocks']
        db = get_db()
        #aapl_chart1 code
        data = db.execute('SELECT closing_date, close_price FROM stock_data WHERE stock_symbol =?',[stock_symbol]).fetchall()
        #aapl_chart2 code
        #data = db.execute("SELECT closing_date, close_price FROM stock_data WHERE closing_date BETWEEN '2023-02-20' AND '2023-02-24' AND stock_symbol='AAPL';").fetchall()
        fig = go.Figure([go.Scatter(x=[row['closing_date'] for row in data], y=[row['close_price'] for row in data])])
        fig.update_layout(title={'text':stock_symbol
                                 ,'font':{'size':30}
                                 ,'x':0.5
                                 ,'y':0.9
                                 ,'xanchor':'center'
                                 ,'yanchor':'top'})
        fig_html = fig.to_html(default_height=500, default_width=700)
        result = fig_html

    
        
    return render_template('examples/stock.html',chart = result)

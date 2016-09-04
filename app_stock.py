import simplejson as json
from flask import Flask, render_template, request
import requests
from dateutil.relativedelta import *
import datetime
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components

app_stock = Flask(__name__)

@app_stock.route('/', methods=['GET','POST'])
def main():
	if request.method == 'GET':
		return render_template('ticker_input.html')
	else:
		#request was a POST
		return redirect ('/stock_trend')

@app_stock.route('/stock_trend', methods=['GET','POST'])
def stock_trend():
	#build url
	ticker = request.form['tickersym']
	ticker = ticker.upper()
	url = "https://www.quandl.com/api/v3/datasets/WIKI/"
	api_url = url + ticker + '.json?'

	#for last month
	end_date = datetime.date.today()
	start_date = end_date - relativedelta(months=1)
	start_date = start_date.strftime('%Y/%m/%d')
	end_date = end_date.strftime('%Y/%m/%d')

	#url params
	url_values = {'start_date':start_date, 'end_date':end_date,'api_key':'wPH_MckAwwBJH1EJp_TD'}

    #'column_names and indices': [Date:0 , Open:1, Close:4, adj open:8, adj close:11]
	#process data
	resp = requests.get(api_url, params=url_values)
	json_data = resp.json()
	dataframe = pd.DataFrame(json_data).reset_index()
	df = dataframe['dataset']
	df = df.iloc[3]
	data_array = np.array(df)
	data = pd.DataFrame({'date':data_array[:,0],'Open':data_array[:,1], 'Close':data_array[:,4],'Adj_Open':data_array[:,8], 'Adj_Close':data_array[:,11]})

	#get input data
	open_val = "openingprice" in request.form
	close_val = "closingprice" in request.form
	adj_close_val = "adjclosingprice" in request.form
	adj_open_val = "adjopeningprice" in request.form

	#plot
	x = data['date'].astype('datetime64')
	closeprice = data['Close'].astype('float')
	openprice = data['Open'].astype('float')
	adjopen = data['Adj_Open'].astype('float')
	adjclose = data['Adj_Close'].astype('float')

 	p = figure(title="Stock value for "+ '' + ticker, x_axis_label='Date', y_axis_label='Stock Price', x_axis_type="datetime")
	p.line(x, openprice, legend="Opening Price", line_width=2, color='lightcoral')
	if open_val:
		p.line(x, openprice, legend="Opening Price", line_width=2, color='lightcoral')

	if close_val:
		p.line(x, closeprice, legend="Closing Price", line_width=2, color='lightseagreen')

	if adj_close_val:
		p.line(x, adjclose, legend="Adj. Closing Price", line_width=2, color='gold')

	if adj_open_val:
		p.line(x, adjopen, legend="Adj. Opening Price", line_width=2, color='olivedrab')

	title = "Stock price for " + ticker
	script, div = components(p)
	return render_template('stock_trend.html', script=script, div=div, ttl=title)

if __name__ == "__main__":
	app_stock.run(port=33507)

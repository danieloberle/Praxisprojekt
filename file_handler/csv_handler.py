import csv
from datetime import date
import os
import shutil

import pandas as pd


def create_stocks_and_etf_list():
    stocks_and_etf_list = []

    with open('securities/stocks_list.csv', newline='') as stocks_list_file:
        stocks_list_csv = csv.DictReader(stocks_list_file, delimiter=',')
        for stock in stocks_list_csv:
            stocks_and_etf_list.append(stock['Company Name'] + '   (' + stock['Symbol'] + ')')

    with open('securities/etfs_list.csv', newline='') as etf_list_file:
        etf_list_csv = csv.DictReader(etf_list_file, delimiter=',')
        for etf in etf_list_csv:
            stocks_and_etf_list.append(etf['Fund Name'] + '   (' + etf['Symbol'] + ')')

    return stocks_and_etf_list


def remove_chart_data(symbol):
    directory = os.path.join('securities', symbol)
    shutil.rmtree(directory)


def write_chart_data(symbol, ticker, interval):
    directory = os.path.join('securities', symbol)
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f'{symbol}_{interval}.csv')
    historical_data = ticker.history(period='max', interval=interval)
    historical_data.to_csv(filename, date_format='%m/%d/%Y')


def load_chart_data(symbol, interval, start_date):
    directory = os.path.join('securities', symbol)
    filename = os.path.join(directory, f'{symbol}_{interval}.csv')
    chart_data = pd.read_csv(filename, index_col=0, parse_dates=True)
    return chart_data.loc[start_date: date.today(), :]


def get_current_price(symbol, interval):
    if symbol == '':
        return 0.00

    directory = os.path.join('securities', symbol)
    filename = os.path.join(directory, f'{symbol}_{interval}.csv')
    chart_data = pd.read_csv(filename, index_col=0, parse_dates=True)
    current_price = chart_data['Close'].iloc[-1]
    return current_price

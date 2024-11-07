import json
import os

from file_handler import txt_handler


def remove_chart_settings(symbol, datetime):
    directory = os.path.join('securities', symbol)
    filename = os.path.join(directory, f'{symbol}_{datetime}.json')
    os.remove(filename)


def load_chart_settings(symbol, datetime):
    directory = os.path.join('securities', symbol)
    filename = os.path.join(directory, f'{symbol}_{datetime}.json')
    with open(filename, 'r') as filehandler:
        return json.load(filehandler)


def load_security_portfolio():
    filename = 'securities/security_portfolio.json'
    with open(filename, 'r') as filehandler:
        return json.load(filehandler)


def add_security_to_security_portfolio(symbol):
    security_portfolio = load_security_portfolio()

    for security in security_portfolio:
        if security['symbol'] == symbol:
            return

    new_security = {"symbol": symbol, "pieces_owned": 0, "total_purchase_price": 0}
    security_portfolio.append(new_security)

    save_security_portfolio(security_portfolio)


def save_chart_settings(chart_settings, datetime):
    if chart_settings['symbol'] == '':
        return

    if not txt_handler.is_security_in_security_list(chart_settings['symbol']):
        return

    symbol = chart_settings['symbol']
    directory = os.path.join('securities', symbol)
    filename = os.path.join(directory, f'{symbol}_{datetime}.json')
    with open(filename, 'w') as filehandler:
        json.dump(chart_settings, filehandler)


def save_security_portfolio(security_portfolio):
    filename = 'securities/security_portfolio.json'
    with open(filename, 'w') as filehandler:
        json.dump(security_portfolio, filehandler)


def remove_security_from_security_portfolio(symbol):
    security_portfolio = load_security_portfolio()
    security_portfolio = [security for security in security_portfolio if security['symbol'] != symbol]
    save_security_portfolio(security_portfolio)

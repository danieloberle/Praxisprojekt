from datetime import datetime
import re
import tkinter as tk

import yfinance as yf

from file_handler import csv_handler, json_handler, txt_handler
from ui import (Chart,
                ChartDisplaySettings,
                SecurityFinder,
                SecurityPortfolioManager,
                TechnicalIndicatorsSettingsLeft,
                TechnicalIndicatorsSettingsRight)


def load_default_chart_settings():
    return {
        "symbol": "",
        "interval": "1d",
        "show_volume": False,
        "chart_type": "line",
        "show_nontrading": False,
        "show_mav1": False,
        "show_mav2": False,
        "show_mav3": False,
        "mav1": 2,
        "mav2": 4,
        "mav3": 6,
        "show_best_peaks_and_lows": False,
        "best_peaks_significance": 20,
        "best_lows_significance": 20,
        "show_percentage_bands": False,
        "mav_for_percentage_bands": 21,
        "percentage_for_percentage_bands": 3,
        "show_bollinger_bands": False,
        "mav_for_bollinger_bands": 20,
        "show_candlestick_patterns": False,
        "show_on_balance_volume": False,
        "time_period": "1 year",
        "show_logarithmic_scale": False,
        "box_size": 3.00
    }


def find_entry_in_stocks_and_etf_list(entry):
    for stock_or_etf in csv_handler.create_stocks_and_etf_list():
        if entry == stock_or_etf:
            split_string = re.split('[()]', entry)
            symbol = split_string[len(split_string) - 2]
            return symbol
    return entry


def create_security_files(symbol, ticker):
    txt_handler.add_security_to_security_list(symbol)
    for interval in ['1d', '1wk', '1mo']:
        csv_handler.write_chart_data(symbol, ticker, interval)
    txt_handler.create_chart_settings_list(symbol)
    json_handler.add_security_to_security_portfolio(symbol)


class Main(tk.Tk):
    def __init__(self, title):
        super().__init__()
        self.title(title)
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')
        self.iconphoto(False, tk.PhotoImage(file='images/stockimage.png'))

        self.interval = tk.StringVar()
        self.default_chart_settings = load_default_chart_settings()
        self.chart_settings = self.default_chart_settings.copy()
        self.security_portfolio = json_handler.load_security_portfolio()

        self.chart_ui = None
        self.chart_frame = None
        self.security_finder_ui = None
        self.security_finder_frame = None
        self.chart_display_settings_ui = None
        self.chart_display_settings_frame = None
        self.technical_indicators_settings_right_ui = None
        self.technical_indicators_settings_right_frame = None
        self.technical_indicators_settings_left_ui = None
        self.technical_indicators_settings_left_frame = None
        self.security_portfolio_manager_ui = None
        self.security_portfolio_manager_frame = None

        self.create_widgets()
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.mainloop()

    def create_widgets(self):
        self.create_security_finder_frame()
        self.create_chart_frame()
        self.create_chart_display_settings_frame()
        self.create_technical_indicators_settings_left_frame()
        self.create_technical_indicators_settings_right_frame()
        self.create_security_portfolio_manager_frame()

    def update_ui(self):
        self.create_widgets()

    def update_security_finder_frame(self):
        self.create_security_finder_frame()

    def update_chart_frame(self):
        self.create_chart_frame()

    def update_chart_display_settings_frame(self):
        self.create_chart_display_settings_frame()

    def update_technical_indicators_settings_left_frame(self):
        self.create_technical_indicators_settings_left_frame()

    def update_technical_indicators_settings_right_frame(self):
        self.create_technical_indicators_settings_right_frame()

    def update_security_portfolio_manager_frame(self):
        self.create_security_portfolio_manager_frame()

    def request_historical_market_information(self, entry):
        symbol = find_entry_in_stocks_and_etf_list(entry)
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="max")

            if history.empty:
                self.security_finder_ui.update_entry('Not Found!')
            else:
                create_security_files(symbol, ticker)
                self.security_portfolio = json_handler.load_security_portfolio()
                self.update_ui()

        except Exception as e:
            self.security_finder_ui.update_entry(f'Error: {str(e)}')

    def remove_security(self, symbol):
        txt_handler.remove_security_from_security_list(symbol)
        csv_handler.remove_chart_data(symbol)

        if len(txt_handler.get_security_list()) == 0 or self.chart_settings['symbol'] == symbol:
            self.chart_settings = self.default_chart_settings.copy()

        json_handler.remove_security_from_security_portfolio(symbol)
        self.security_portfolio = json_handler.load_security_portfolio()

        self.update_ui()

    def plot_fullscreen(self):
        self.chart_ui.plot_fullscreen(self.chart_settings)

    def validate_variables(self, buy_sell_pieces, buy_sell_price):
        try:
            float(buy_sell_price)
            int(buy_sell_pieces)
        except ValueError:
            self.security_portfolio_manager_ui.update_buy_sell_price_entry('Invalid input!')
            return False

        if self.chart_settings['symbol'] == '' or int(buy_sell_pieces) < 1 or float(buy_sell_price) <= 0:
            return False

        return True

    def buy_security(self, buy_sell_pieces, buy_sell_price):
        if not self.validate_variables(buy_sell_pieces, buy_sell_price):
            return

        security = self.find_security(self.chart_settings['symbol'])
        if security is None:
            return

        pieces_owned = security['pieces_owned']
        total_purchase_price = security['total_purchase_price']

        new_pieces_owned = pieces_owned + int(buy_sell_pieces)
        if new_pieces_owned > 100000:
            return

        security['pieces_owned'] = new_pieces_owned
        security['total_purchase_price'] = total_purchase_price + (int(buy_sell_pieces) * float(buy_sell_price))

        self.security_portfolio_changed()

    def sell_security(self, buy_sell_pieces, buy_sell_price):
        if not self.validate_variables(buy_sell_pieces, buy_sell_price):
            return

        security = self.find_security(self.chart_settings['symbol'])
        if security is None:
            return

        buy_sell_pieces = int(buy_sell_pieces)
        buy_sell_price = float(buy_sell_price)
        pieces_owned = security['pieces_owned']

        if buy_sell_pieces > pieces_owned:
            buy_sell_pieces = pieces_owned

        new_pieces_owned = pieces_owned - buy_sell_pieces
        new_total_purchase_price = security['total_purchase_price'] - (buy_sell_pieces * buy_sell_price)

        if new_pieces_owned == 0:
            new_total_purchase_price = 0

        security['pieces_owned'] = new_pieces_owned
        security['total_purchase_price'] = new_total_purchase_price

        self.security_portfolio_changed()

    def find_security(self, symbol):
        for sec in self.security_portfolio:
            if sec['symbol'] == symbol:
                return sec
        return None

    def create_chart_frame(self):
        if self.chart_frame is not None:
            self.chart_frame.destroy()

        self.chart_frame = tk.LabelFrame(self)
        self.chart_frame.place(relwidth=4 / 5, relheight=2 / 3, relx=1 / 5)
        self.chart_ui = Chart(self.chart_frame)
        self.chart_ui.plot_chart(self.chart_settings)

    def create_chart_display_settings_frame(self):
        if self.chart_display_settings_frame is not None:
            self.chart_display_settings_frame.destroy()

        self.chart_display_settings_frame = tk.LabelFrame(self)
        self.chart_display_settings_frame.place(relwidth=1 / 5, relheight=1 / 3, rely=2 / 3)
        self.chart_display_settings_ui = ChartDisplaySettings(self.chart_display_settings_frame, self.chart_settings, self.chart_settings_changed, self.plot_fullscreen, self.save_chart_settings)

    def create_security_finder_frame(self):
        if self.security_finder_frame is not None:
            self.security_finder_frame.destroy()

        self.security_finder_frame = tk.LabelFrame(self)
        self.security_finder_frame.place(relwidth=1 / 5, relheight=2 / 3)
        self.security_finder_ui = SecurityFinder(self.security_finder_frame, self.entry_confirmed, self.plot_chart, self.request_historical_market_information, self.remove_security, self.security_portfolio, self.remove_chart_settings, self.load_chart_settings)

    def create_security_portfolio_manager_frame(self):
        if self.security_portfolio_manager_frame is not None:
            self.security_portfolio_manager_frame.destroy()

        self.security_portfolio_manager_frame = tk.LabelFrame(self)
        self.security_portfolio_manager_frame.place(relwidth=4 / 15, relheight=1 / 3, relx=11 / 15, rely=2 / 3)
        self.security_portfolio_manager_ui = SecurityPortfolioManager(self.security_portfolio_manager_frame, self.chart_settings, self.buy_security, self.sell_security)

    def create_technical_indicators_settings_left_frame(self):
        if self.technical_indicators_settings_left_frame is not None:
            self.technical_indicators_settings_left_frame.destroy()

        self.technical_indicators_settings_left_frame = tk.LabelFrame(self)
        self.technical_indicators_settings_left_frame.place(relwidth=4 / 15, relheight=1 / 3, relx=1 / 5, rely=2 / 3)
        self.technical_indicators_settings_left_ui = TechnicalIndicatorsSettingsLeft(self.technical_indicators_settings_left_frame, self.chart_settings, self.chart_settings_changed)

    def create_technical_indicators_settings_right_frame(self):
        if self.technical_indicators_settings_right_frame is not None:
            self.technical_indicators_settings_right_frame.destroy()

        self.technical_indicators_settings_right_frame = tk.LabelFrame(self)
        self.technical_indicators_settings_right_frame.place(relwidth=4 / 15, relheight=1 / 3, relx=7 / 15, rely=2 / 3)
        self.technical_indicators_settings_right_ui = TechnicalIndicatorsSettingsRight(self.technical_indicators_settings_right_frame, self.chart_settings, self.chart_settings_changed)

    def entry_confirmed(self, entry):
        self.request_historical_market_information(entry)

    def load_chart_settings(self, symbol, save):
        self.chart_settings = json_handler.load_chart_settings(symbol, save)
        self.update_ui()

    def save_chart_settings(self):
        if self.chart_settings['symbol'] == '':
            return

        current_datetime = datetime.now()
        formatted_current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        json_handler.save_chart_settings(self.chart_settings, formatted_current_datetime)
        txt_handler.add_datetime_to_chart_settings_list(self.chart_settings['symbol'], formatted_current_datetime)

        self.update_ui()

    def remove_chart_settings(self, symbol, formatted_current_datetime):
        json_handler.remove_chart_settings(symbol, formatted_current_datetime)
        txt_handler.remove_settings_from_chart_settings_list(symbol, formatted_current_datetime)

        self.update_ui()

    def plot_chart(self, symbol):
        self.chart_settings = self.default_chart_settings.copy()
        self.chart_settings['symbol'] = symbol
        self.update_ui()

    def chart_settings_changed(self):
        self.update_ui()

    def security_portfolio_changed(self):
        json_handler.save_security_portfolio(self.security_portfolio)
        self.update_ui()


Main('Praxisprojekt')

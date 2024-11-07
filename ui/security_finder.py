from PIL import Image

import customtkinter as ctk
import tkinter as tk

from file_handler import csv_handler, txt_handler


def create_button(parent, text, command):
    tk.Button(parent, text=text, command=command).pack(side='left')


class SecurityFinder:
    def __init__(self, parent, entry_confirmed, plot_chart, request_historical_market_information, remove_security, security_portfolio, remove_chart_settings, load_chart_settings):
        self.parent = parent
        self.entry_confirmed = entry_confirmed
        self.plot_chart = plot_chart
        self.request_historical_market_information = request_historical_market_information
        self.remove_security = remove_security
        self.security_portfolio = security_portfolio
        self.remove_chart_settings = remove_chart_settings
        self.load_chart_settings = load_chart_settings

        self.stocks_and_etf_list = csv_handler.create_stocks_and_etf_list()
        self.edited_stocks_and_etf_list = []
        self.list_box_height = tk.IntVar(value=30)

        self.security_list_frame = None
        self.list_box = None
        self.list_box_frame = None
        self.entry = None
        self.magnifying_glass_image = None
        self.entry_frame = None

        self.destroy_widgets()
        self.create_widgets()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def create_widgets(self):
        self.create_entry_frame()
        self.create_list_box_frame()
        self.create_security_list_frame()

    def create_entry_frame(self):
        self.entry_frame = tk.LabelFrame(self.parent)
        self.entry_frame.pack(fill=tk.X)

        self.magnifying_glass_image = ctk.CTkImage(
            light_image=Image.open('images/magnifying_glass_dark.png'),
            dark_image=Image.open('images/magnifying_glass_light.png'))
        ctk.CTkLabel(self.entry_frame, text='', image=self.magnifying_glass_image).pack(side='left')

        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(side='left')
        self.entry.bind('<KeyRelease>', self.update_edited_stocks_and_etf_list)
        self.entry.bind('<KeyRelease>', self.update_list_box, add="+")
        self.entry.bind('<KeyRelease>', self.place_or_forget_list_box, add="+")
        self.entry.bind('<Return>', self.confirm_entry)

        create_button(self.entry_frame, 'X', self.delete_button_commands)
        create_button(self.entry_frame, 'Search', self.confirm_entry)

    def create_list_box_frame(self):
        self.list_box_frame = tk.LabelFrame(self.parent)
        self.list_box_frame.pack(fill=tk.X)

        self.list_box = tk.Listbox(self.list_box_frame, width=20, height=self.list_box_height.get())
        self.list_box.bind('<<ListboxSelect>>', self.fillout_entry)
        self.list_box.bind('<<ListboxSelect>>', self.forget_list_box, add="+")

    def create_security_list_frame(self):
        self.security_list_frame = tk.LabelFrame(self.parent)
        self.security_list_frame.pack(fill=tk.X)
        self.update_security_list()

    def delete_button_commands(self):
        self.forget_list_box()
        self.empty_entry()

    def confirm_entry(self, *args):
        self.entry_confirmed(self.entry.get())

    def empty_entry(self, *args):
        self.entry.delete(0, tk.END)

    def fillout_entry(self, *args):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.list_box.get(tk.ANCHOR))

    def update_entry(self, message):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, message)

    def update_edited_stocks_and_etf_list(self, *args):
        self.edited_stocks_and_etf_list = []
        typed = self.entry.get()

        if typed:
            self.edited_stocks_and_etf_list = [stock_or_etf for stock_or_etf in self.stocks_and_etf_list if typed.lower() in stock_or_etf.lower()]

    def update_list_box(self, *args):
        self.list_box.delete(0, tk.END)
        for stock_or_etf in self.edited_stocks_and_etf_list:
            self.list_box.insert(tk.END, stock_or_etf)
        self.list_box_height.set(len(self.edited_stocks_and_etf_list))
        self.list_box.config(height=self.list_box_height.get())

    def forget_list_box(self, *args):
        self.list_box.forget()
        self.list_box_frame.forget()

    def place_or_forget_list_box(self, *args):
        if not self.edited_stocks_and_etf_list or self.entry.get() == '':
            self.forget_list_box()
        else:
            self.list_box_frame.pack(fill=tk.X)
            self.list_box.pack(fill=tk.BOTH)
            self.security_list_frame.forget()
            self.security_list_frame.pack(fill=tk.X)

    def update_security_list(self):
        security_list = txt_handler.get_security_list()
        if len(security_list) == 0:
            self.security_list_frame.forget()
        else:
            self.security_list_frame.pack(fill=tk.X)
            for symbol in security_list:
                self.create_security_frame(symbol)
                self.create_saved_settings_frame(symbol)

    def create_portfolio_label(self, parent, symbol):
        pieces_owned = sum(security['pieces_owned'] for security in self.security_portfolio if security['symbol'] == symbol)
        label_text = 'Portfolio' if pieces_owned > 0 else 'Watchlist'
        ctk.CTkLabel(parent, text=label_text).pack(side='left')

    def create_saved_settings_frame(self, symbol):
        saved_settings = txt_handler.get_chart_settings_list(symbol)
        for setting in saved_settings:
            saved_settings_frame = tk.Frame(self.security_list_frame)
            saved_settings_frame.pack(fill=tk.X)
            create_button(saved_settings_frame, setting, lambda symbol=symbol, setting=setting: self.load_chart_settings(symbol, setting))
            create_button(saved_settings_frame, 'X', lambda symbol=symbol, setting=setting: self.remove_chart_settings(symbol, setting))

    def create_security_frame(self, symbol):
        security_frame = tk.Frame(self.security_list_frame, borderwidth=1, relief=tk.GROOVE)
        security_frame.pack(fill=tk.X)

        tk.Button(security_frame, text=symbol, command=lambda symbol=symbol: self.plot_chart(symbol)).pack(side='left', expand=True, fill=tk.X)

        self.create_portfolio_label(security_frame, symbol)

        unicode_character = '\u21BB'
        create_button(security_frame, unicode_character, lambda symbol=symbol: [self.request_historical_market_information(symbol), self.plot_chart(symbol)])
        create_button(security_frame, 'X', lambda symbol=symbol: self.remove_security(symbol))

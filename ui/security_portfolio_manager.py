import customtkinter as ctk
import tkinter as tk

from file_handler import csv_handler, json_handler


def create_label(parent, text, row, column):
    ctk.CTkLabel(parent, text=text).grid(row=row, column=column)


def validate_spinbox_value(value):
    if value == '':
        return True
    try:
        if int(value) < 0:
            return False
        return True
    except ValueError:
        return False


def enforce_spinbox_limit(spinbox):
    if spinbox.get() == '':
        spinbox.delete(0, tk.END)
        spinbox.insert(0, '1')
        return
    value = int(spinbox.get())
    if value < 1:
        spinbox.delete(0, tk.END)
        spinbox.insert(0, '1')
        return
    if value > 10000:
        spinbox.delete(0, tk.END)
        spinbox.insert(0, '10000')
        return


def create_spinbox(parent, variable, row, column):
    validate_input = parent.register(validate_spinbox_value)

    spinbox = tk.Spinbox(parent, from_=1, to=10000, textvariable=variable, width=5, validate='key', validatecommand=(validate_input, '%P'))
    spinbox.grid(row=row, column=column)
    spinbox.bind('<FocusOut>', lambda event: enforce_spinbox_limit(spinbox))
    spinbox.bind('<Return>', lambda event: enforce_spinbox_limit(spinbox))


def create_button(parent, text, command, row, column):
    tk.Button(parent, text=text, height=2, width=10, command=command).grid(row=row, column=column)


def validate_entry_value(value):
    if value == '':
        return True
    try:
        if float(value) < 0:
            return False
        return True
    except ValueError:
        return False


class SecurityPortfolioManager:
    def __init__(self, parent, chart_settings, buy_security, sell_security):
        self.parent = parent
        self.chart_settings = chart_settings
        self.buy_security = buy_security
        self.sell_security = sell_security

        self.symbol = self.chart_settings['symbol']
        self.interval = self.chart_settings['interval']

        self.current_price = csv_handler.get_current_price(self.symbol, self.interval)
        self.pieces_owned, self.total_purchase_price = self.get_current_ownership_info()
        self.current_total = tk.DoubleVar(value=self.current_price * self.pieces_owned)
        self.purchase_price_difference = self.current_total.get() - self.total_purchase_price
        self.purchase_price_difference_in_percent = self.get_purchase_price_difference_in_percent()
        self.buy_sell_pieces = tk.IntVar()
        self.buy_sell_price = tk.DoubleVar()
        self.buy_sell_price.set(float(f'{self.current_price:.2f}'))

        self.buy_sell_price_entry = None

        self.destroy_widgets()
        self.create_widgets()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def get_current_ownership_info(self):
        pieces_owned = 0
        total_purchase_price = 0
        security_portfolio = json_handler.load_security_portfolio()

        for security in security_portfolio:
            if security['symbol'] == self.chart_settings['symbol']:
                pieces_owned = security['pieces_owned']
                total_purchase_price = security['total_purchase_price']
                break

        return pieces_owned, total_purchase_price

    def get_purchase_price_difference_in_percent(self):
        if self.total_purchase_price != 0:
            return self.purchase_price_difference / self.total_purchase_price * 100
        return 0

    def buy_security_pressed(self):
        self.buy_security(self.buy_sell_pieces.get(), self.buy_sell_price.get())

    def sell_security_pressed(self):
        self.sell_security(self.buy_sell_pieces.get(), self.buy_sell_price.get())

    def create_widgets(self):
        ctk.CTkLabel(self.parent, text='Current Ownership', font=('TkDefaultFont', 18)).grid(row=1, column=0)

        create_label(self.parent, 'Current Price: ', 2, 0)
        create_label(self.parent, f'{self.current_price:.2f}', 2, 1)

        create_label(self.parent, 'Pieces: ', 3, 0)
        create_label(self.parent, self.pieces_owned, 3, 1)

        create_label(self.parent, 'Total: ', 4, 0)
        create_label(self.parent, f'{self.current_total.get():.2f}', 4, 1)
        create_label(self.parent, f'({self.purchase_price_difference:+.2f}, {self.purchase_price_difference_in_percent:+.2f}%)', 4, 2)

        ctk.CTkLabel(self.parent, text='').grid(row=5, column=0)

        ctk.CTkLabel(self.parent, text='Buy / Sell', font=('TkDefaultFont', 18)).grid(row=6, column=0)

        create_label(self.parent, 'Price: ', 7, 0)
        validate_entry = self.parent.register(validate_entry_value)
        self.buy_sell_price_entry = tk.Entry(self.parent, width=10, textvariable=self.buy_sell_price, validate='key', validatecommand=(validate_entry, '%P'))
        self.buy_sell_price_entry.grid(row=7, column=1)

        create_label(self.parent, 'Pieces: ', 8, 0)
        create_spinbox(self.parent, self.buy_sell_pieces, 8, 1)

        create_button(self.parent, 'Buy', self.buy_security_pressed, 9, 0)
        create_button(self.parent, 'Sell', self.sell_security_pressed, 9, 1)

    def update_buy_sell_price_entry(self, message):
        self.buy_sell_price_entry.delete(0, tk.END)
        self.buy_sell_price_entry.insert(0, message)

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk


def create_button(parent, text, command):
    tk.Button(parent, text=text, height=2, width=15, command=command).pack()


def create_checkbutton(parent, text, variable, command):
    checkbutton = tk.Checkbutton(parent,
                                 text=text,
                                 variable=variable,
                                 onvalue=True,
                                 offvalue=False,
                                 height=1,
                                 width=15,
                                 command=command)
    checkbutton.pack()


def create_label(parent, text, row, column):
    ctk.CTkLabel(parent, text=text).grid(row=row, column=column)


def create_option_menu(parent, variable, values, command, row, column):
    ttk.OptionMenu(parent, variable, variable.get(), *values, command=command).grid(row=row, column=column)


def get_time_periods(interval):
    time_periods_map = {
        '1d': ['1 week', '1 month', '6 months', '1 year', '5 years', '10 years', '20 years'],
        '1wk': ['1 month', '6 months', '1 year', '5 years', '10 years', '20 years'],
        '1mo': ['6 months', '1 year', '5 years', '10 years', '20 years']
    }
    return time_periods_map.get(interval)


def validate_spinbox_value(value):
    if value == "":
        return True
    try:
        if float(value) < 0:
            return False
        return True
    except ValueError:
        return False


class ChartDisplaySettings:
    INTERVALS = {
        'daily': '1d',
        'weekly': '1wk',
        'monthly': '1mo'
    }
    CHART_TYPES = {
        'line chart': 'line',
        'candlestick chart': 'candle',
        'ohlc chart': 'ohlc',
        'point & figure chart': 'pnf'
    }

    def __init__(self, parent, chart_settings, chart_settings_changed, plot_fullscreen, save_chart_settings):
        self.parent = parent
        self.chart_settings = chart_settings
        self.chart_settings_changed = chart_settings_changed
        self.plot_fullscreen = plot_fullscreen
        self.save_chart_settings = save_chart_settings

        self.presented_interval = tk.StringVar(value=self.get_presented_interval(self.chart_settings['interval']))
        self.presented_chart_type = tk.StringVar(value=self.get_presented_chart_type(self.chart_settings['chart_type']))
        self.time_period = tk.StringVar(value=self.chart_settings['time_period'])
        self.show_volume = tk.BooleanVar(value=self.chart_settings['show_volume'])
        self.show_nontrading = tk.BooleanVar(value=self.chart_settings['show_nontrading'])
        self.show_logarithmic_scale = tk.BooleanVar(value=self.chart_settings['show_logarithmic_scale'])
        self.box_size = tk.DoubleVar(value=self.chart_settings['box_size'])

        self.time_periods = get_time_periods(self.chart_settings['interval'])

        self.option_menu_frame = None
        self.checkbutton_frame = None
        self.button_frame = None
        self.box_size_spinbox = None
        self.box_size_label = None

        self.destroy_widgets()
        self.create_widgets()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def get_presented_interval(self, interval):
        for presented, actual in self.INTERVALS.items():
            if actual == interval:
                return presented

    def get_presented_chart_type(self, chart_type):
        for presented, actual in self.CHART_TYPES.items():
            if actual == chart_type:
                return presented

    def validate_spinbox_input(self):
        try:
            float(self.box_size_spinbox.get())
            return True
        except ValueError:
            self.box_size.set(self.chart_settings['box_size'])
            return False

    def update_chart_settings(self, *args):
        if not self.validate_spinbox_input():
            return

        self.chart_settings.update({
            'time_period': self.time_period.get(),
            'show_volume': self.show_volume.get(),
            'show_nontrading': self.show_nontrading.get(),
            'show_logarithmic_scale': self.show_logarithmic_scale.get(),
            'box_size': self.box_size.get()
        })
        self.chart_settings_changed()

    def interval_changed(self, *args):
        self.chart_settings['interval'] = self.INTERVALS[self.presented_interval.get()]
        self.adjust_time_period()
        self.chart_settings_changed()

    def adjust_time_period(self):
        if self.chart_settings['interval'] == '1wk' and self.chart_settings['time_period'] == '1 week':
            self.chart_settings['time_period'] = '1 month'
        if self.chart_settings['interval'] == '1mo' and (self.chart_settings['time_period'] == '1 week' or self.chart_settings['time_period'] == '1 month'):
            self.chart_settings['time_period'] = '6 months'

    def chart_type_changed(self, *args):
        self.chart_settings['chart_type'] = self.CHART_TYPES[self.presented_chart_type.get()]
        self.update_chart_settings()

    def create_widgets(self):
        self.create_option_menu_frame()
        self.create_box_size_spinbox()
        self.create_checkbutton_frame()
        self.create_button_frame()

    def create_option_menu_frame(self):
        self.option_menu_frame = tk.Frame(self.parent)
        self.option_menu_frame.pack(pady=8)

        create_label(self.option_menu_frame, 'Interval', 1, 0)
        create_option_menu(self.option_menu_frame, self.presented_interval, list(self.INTERVALS.keys()), self.interval_changed, 1, 1)

        create_label(self.option_menu_frame, 'Time Period', 2, 0)
        create_option_menu(self.option_menu_frame, self.time_period, self.time_periods, self.update_chart_settings, 2, 1)

        create_label(self.option_menu_frame, 'Chart Type', 3, 0)
        create_option_menu(self.option_menu_frame, self.presented_chart_type, list(self.CHART_TYPES.keys()), self.chart_type_changed, 3, 1)

    def create_box_size_spinbox(self):
        self.box_size_label = ctk.CTkLabel(self.option_menu_frame, text='Box Size')

        validate_input = self.option_menu_frame.register(validate_spinbox_value)

        self.box_size_spinbox = tk.Spinbox(self.option_menu_frame,
                                           from_=0.01,
                                           to=200,
                                           format='%.2f',
                                           textvariable=self.box_size,
                                           increment=0.1,
                                           width=5,
                                           validate='key',
                                           validatecommand=(validate_input, '%P'),
                                           command=self.update_chart_settings)
        self.box_size_spinbox.bind('<FocusOut>', self.update_chart_settings)
        self.box_size_spinbox.bind('<Return>', self.update_chart_settings)
        if self.chart_settings['chart_type'] == 'pnf':
            self.box_size_label.grid(row=5, column=0)
            self.box_size_spinbox.grid(row=5, column=1)

    def create_checkbutton_frame(self):
        self.checkbutton_frame = tk.Frame(self.parent)
        self.checkbutton_frame.pack(pady=8)

        create_checkbutton(self.checkbutton_frame, 'Volume', self.show_volume, self.update_chart_settings)
        create_checkbutton(self.checkbutton_frame, 'non-Trading days', self.show_nontrading, self.update_chart_settings)
        create_checkbutton(self.checkbutton_frame, 'logarithmic scale', self.show_logarithmic_scale, self.update_chart_settings)

    def create_button_frame(self):
        self.button_frame = tk.Frame(self.parent)
        self.button_frame.pack(pady=8)

        create_button(self.button_frame, 'Fullscreen', self.plot_fullscreen)
        create_button(self.button_frame, 'Save', self.save_chart_settings)

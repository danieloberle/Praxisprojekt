import math
import matplotlib.pyplot as plt
import mplfinance as mpf
import tkinter as tk

from datetime import date, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import ScalarFormatter

from technical_indicators import (bollinger_bands,
                                  candlestick_patterns,
                                  mav,
                                  on_balance_volume,
                                  peaks_and_lows,
                                  percentage_bands)
from file_handler import csv_handler, txt_handler


TIME_PERIODS = {
    '1 week': timedelta(weeks=1),
    '1 month': timedelta(days=30),
    '6 months': timedelta(days=182),
    '1 year': timedelta(days=365),
    '5 years': timedelta(days=1826),
    '10 years': timedelta(days=3650),
    '20 years': timedelta(days=7300)
}


def configure_legend(ax, chart_settings):
    if chart_settings['show_logarithmic_scale']:
        ax[0].set_yscale('log')
        ax[0].yaxis.set_major_formatter(ScalarFormatter())
        ax[0].yaxis.set_minor_formatter(ScalarFormatter())

    if ax[0].get_legend() is not None:
        ax[0].legend(loc='upper left')

    if ax[1].get_legend() is not None:
        ax[1].legend(loc='lower left')


def get_start_date(chart_settings):
    time_period = chart_settings['time_period']
    delta = TIME_PERIODS.get(time_period)

    return date.today() - delta


def add_plots(chart_data, chart_settings):
    add_plot = []

    peaks = peaks_and_lows.find_all_peaks(chart_data)
    best_peaks = peaks_and_lows.find_best_peaks(peaks, chart_settings)
    lows = peaks_and_lows.find_all_lows(chart_data)
    best_lows = peaks_and_lows.find_best_lows(lows, chart_settings)

    add_plot.extend(bollinger_bands.add_bollinger_bands(chart_data, chart_settings))
    add_plot.extend(candlestick_patterns.add_candlestick_patterns(chart_data, chart_settings))
    add_plot.extend(mav.add_mav(chart_data, chart_settings))
    add_plot.extend(on_balance_volume.add_on_balance_volume(chart_data, chart_settings))
    add_plot.extend(peaks_and_lows.add_best_peaks_and_lows(chart_data, chart_settings))
    add_plot.extend(peaks_and_lows.add_trendline(best_peaks, best_lows, chart_data, chart_settings))
    add_plot.extend(percentage_bands.add_percentage_bands(chart_data, chart_settings))

    return add_plot


def create_chart(chart_data, chart_settings):
    plt.close()

    if chart_settings['chart_type'] == 'pnf':
        min_price = chart_data['Close'].min()
        max_price = chart_data['Close'].max()
        price_range = max_price - min_price
        max_box_size = price_range / 2
        average_true_value = chart_data['Close'].mean()
        min_box_size = 0.01 * average_true_value

        if chart_settings['box_size'] > max_box_size:
            chart_settings['box_size'] = math.floor((price_range / 2) * 100) / 100

        elif chart_settings['box_size'] < min_box_size:
            chart_settings['box_size'] = math.ceil(min_box_size * 100) / 100

        fig, ax = mpf.plot(chart_data,
                           type=chart_settings['chart_type'],
                           pnf_params=dict(box_size=chart_settings['box_size']),
                           volume=chart_settings['show_volume'],
                           show_nontrading=chart_settings['show_nontrading'],
                           returnfig=True,
                           title=chart_settings['symbol'],
                           style='yahoo')

    else:
        fig, ax = mpf.plot(chart_data,
                           type=chart_settings['chart_type'],
                           volume=chart_settings['show_volume'],
                           show_nontrading=chart_settings['show_nontrading'],
                           returnfig=True,
                           title=chart_settings['symbol'],
                           style='yahoo',
                           figscale=3,
                           addplot=add_plots(chart_data, chart_settings),
                           hlines=peaks_and_lows.add_horizontal_lines(chart_data, chart_settings))

    return fig, ax


class Chart:
    def __init__(self, parent):
        self.parent = parent

        self.destroy_widgets()

        self.chart_frame = tk.LabelFrame(self.parent)
        self.chart_frame.pack()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def clear_chart_frame(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def plot_chart(self, chart_settings):
        self.clear_chart_frame()

        if chart_settings['symbol'] == '':
            return

        chart_data = csv_handler.load_chart_data(chart_settings['symbol'],
                                            chart_settings['interval'],
                                            get_start_date(chart_settings))

        if len(chart_data) == 0:
            return

        fig, ax = create_chart(chart_data, chart_settings)
        configure_legend(ax, chart_settings)

        chart_canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack()

    def plot_fullscreen(self, chart_settings):
        if txt_handler.is_security_in_security_list(chart_settings['symbol']):
            self.plot_chart(chart_settings)
            mpf.show()

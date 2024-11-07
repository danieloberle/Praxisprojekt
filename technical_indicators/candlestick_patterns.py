import talib

import mplfinance as mpf


def find_candlestick_pattern(chart_data, talib_function, bullish_label, bearish_label):
    bullish_candlestick = chart_data[talib_function(chart_data['Open'],
                                                    chart_data['High'],
                                                    chart_data['Low'],
                                                    chart_data['Close']) > 0]
    bearish_candlestick = chart_data[talib_function(chart_data['Open'],
                                                    chart_data['High'],
                                                    chart_data['Low'],
                                                    chart_data['Close']) < 0]

    bullish_candlestick_plot = None
    bearish_candlestick_plot = None

    if len(bullish_candlestick) > 0:
        aligned_bullish_candlestick = bullish_candlestick.reindex(chart_data.index)
        bullish_candlestick_plot = mpf.make_addplot(aligned_bullish_candlestick['Close'],
                                                    scatter=True,
                                                    label=bullish_label)

    if len(bearish_candlestick) > 0:
        aligned_bearish_candlestick = bearish_candlestick.reindex(chart_data.index)
        bearish_candlestick_plot = mpf.make_addplot(aligned_bearish_candlestick['Close'],
                                                    scatter=True,
                                                    label=bearish_label)

    return [plot for plot in [bullish_candlestick_plot, bearish_candlestick_plot] if plot is not None]


def add_candlestick_patterns(chart_data, chart_settings):
    candlestick_plots = []

    if chart_settings['show_candlestick_patterns']:
        candlestick_patterns = [(talib.CDLDOJI, 'Bullish Doji', 'Bearish Doji'),
                                (talib.CDLENGULFING, 'Bullish Engulfing', 'Bearish Engulfing'),
                                (talib.CDLEVENINGSTAR, 'Evening Star', 'Evening Star'),
                                (talib.CDLHAMMER, 'Bullish Hammer', 'Bearish Hammer'),
                                (talib.CDLHARAMI, 'Bullish Harami', 'Bearish Harami'),
                                (talib.CDLMORNINGSTAR, 'Morning Star', 'Morning Star'),
                                (talib.CDLSEPARATINGLINES, 'Bullish Separating Lines', 'Bearish Separating Lines'),
                                (talib.CDLSHOOTINGSTAR, 'Bullish Shooting Star', 'Bearish Shooting Star'),
                                (talib.CDLRISEFALL3METHODS, 'Rising Three Methods', 'Falling Three Methods')]

        for candlestick_pattern, bullish_label, bearish_label in candlestick_patterns:
            candlestick_plots.extend(find_candlestick_pattern(chart_data,
                                                              candlestick_pattern,
                                                              bullish_label,
                                                              bearish_label))

    return candlestick_plots

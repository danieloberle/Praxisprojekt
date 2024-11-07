import math
import mplfinance as mpf
import numpy as np
import pandas as pd


def find_all_peaks(chart_data):
    peaks = chart_data[(chart_data['Close'] > chart_data['Close'].shift(1)) &
                       (chart_data['Close'] > chart_data['Close'].shift(-1))]

    return peaks


def find_best_peaks(peaks, chart_settings):
    selected_peaks = []

    significance = chart_settings['best_peaks_significance']

    for i in range(len(peaks)):
        current_peak = peaks.iloc[i]
        current_date = current_peak.name
        current_price = current_peak['Close']

        start_date = max(current_date - pd.DateOffset(days=significance), peaks.index[0])
        end_date = min(current_date + pd.DateOffset(days=significance), peaks.index[-1])

        peaks_within_range = peaks.loc[start_date:end_date]

        if current_price == peaks_within_range['Close'].max():
            selected_peaks.append(current_peak)

    return pd.DataFrame(selected_peaks)


def find_all_lows(chart_data):
    lows = chart_data[(chart_data['Close'] < chart_data['Close'].shift(1)) &
                      (chart_data['Close'] < chart_data['Close'].shift(-1))]

    return lows


def find_best_lows(lows, chart_settings):
    selected_lows = []

    significance = chart_settings['best_lows_significance']

    for i in range(len(lows)):
        current_low = lows.iloc[i]
        current_date = current_low.name
        current_price = current_low['Close']

        start_date = max(current_date - pd.DateOffset(days=significance), lows.index[0])
        end_date = min(current_date + pd.DateOffset(days=significance), lows.index[-1])

        lows_within_range = lows.loc[start_date:end_date]

        if current_price == lows_within_range['Close'].min():
            selected_lows.append(current_low)

    return pd.DataFrame(selected_lows)


def add_best_peaks_and_lows(chart_data, chart_settings):
    best_peaks_and_lows_list = []

    if not chart_settings['show_best_peaks_and_lows']:
        return best_peaks_and_lows_list

    all_peaks = find_all_peaks(chart_data)
    best_peaks = find_best_peaks(all_peaks, chart_settings)

    all_lows = find_all_lows(chart_data)
    best_lows = find_best_lows(all_lows, chart_settings)

    if len(best_peaks) > 0:
        aligned_best_peaks = best_peaks.reindex(chart_data.index)
        best_peaks_plot = mpf.make_addplot(aligned_best_peaks['Close'],
                                           scatter=True,
                                           color='green',
                                           label='Peaks')
        best_peaks_and_lows_list.append(best_peaks_plot)

    if len(find_best_lows(find_all_lows(chart_data), chart_settings)) > 0:
        aligned_best_lows = best_lows.reindex(chart_data.index)
        best_lows_plot = mpf.make_addplot(aligned_best_lows['Close'],
                                          scatter=True,
                                          color='red',
                                          label='Lows')
        best_peaks_and_lows_list.append(best_lows_plot)

    return best_peaks_and_lows_list


def calculate_uptrend_line(best_peaks, best_lows):
    uptrend_lines = []

    for i in range(1, len(best_peaks)):
        peak1 = best_peaks.iloc[i-1]
        peak2 = best_peaks.iloc[i]

        for j in range(1, len(best_lows)):
            low1 = best_lows.iloc[j-1]
            low2 = best_lows.iloc[j]

            is_price_ascending = peak1['Close'] < peak2['Close'] and low1['Close'] < low2['Close']
            is_time_order_correct = low1.name < peak1.name < low2.name < peak2.name

            if is_price_ascending and is_time_order_correct:
                uptrend_lines.append([low1, peak1, low2, peak2])

    return uptrend_lines


def calculate_downtrend_line(best_peaks, best_lows):
    downtrend_lines = []

    for i in range(1, len(best_lows)):
        low1 = best_lows.iloc[i-1]
        low2 = best_lows.iloc[i]

        for j in range(len(best_peaks)):
            peak1 = best_peaks.iloc[j-1]
            peak2 = best_peaks.iloc[j]

            is_price_descending = low1['Close'] > low2['Close'] and peak1['Close'] > peak2['Close']
            is_time_order_correct = peak1.name < low1.name < peak2.name < low2.name

            if is_price_descending and is_time_order_correct:
                downtrend_lines.append([peak1, low1, peak2, low2])

    return downtrend_lines


def draw_line_between_two_points(point1, point2, line_color, trend, chart_data):
    date1 = point1.name
    date2 = point2.name
    close1 = point1['Close']
    close2 = point2['Close']
    dif_close = abs(close2-close1)
    dif_day = sum((date1 <= chart_data.iloc[day].name <= date2) for day in range(len(chart_data)))
    dif_close_per_day = dif_close / dif_day

    line_data = []
    price = close1

    for day in range(len(chart_data)):
        is_before_date1 = chart_data.iloc[day].name < date1
        is_maximum_exceeded = trend == 'Uptrend' and price > chart_data['Close'].max()
        is_minimum_exceeded = trend == 'Downtrend' and price < chart_data['Close'].min()

        if is_before_date1 or is_maximum_exceeded or is_minimum_exceeded:
            line_data.append(math.nan)
        else:
            line_data.append(price)
            if trend == 'Uptrend' and price <= chart_data['Close'].max():
                price = price + dif_close_per_day
            if trend == 'Downtrend' and price >= chart_data['Close'].min():
                price = price - dif_close_per_day

    trend_line_plot = mpf.make_addplot(line_data, color=line_color, label=trend)

    return trend_line_plot


def draw_logarithmic_line_between_two_points(point1, point2, line_color, trend, chart_data):
    date1 = point1.name
    date2 = point2.name
    close1 = point1['Close']
    close2 = point2['Close']
    log_close1 = np.log(close1)
    log_close2 = np.log(close2)
    dif_log_close = abs(log_close2-log_close1)
    dif_day = sum((date1 <= chart_data.iloc[day].name <= date2) for day in range(len(chart_data)))
    dif_log_close_per_day = dif_log_close / dif_day

    line_data = []
    log_price = log_close1

    for day in range(len(chart_data)):
        is_before_date1 = chart_data.iloc[day].name < date1
        is_maximum_exceeded = trend == 'Uptrend' and np.exp(log_price) > chart_data['Close'].max()
        is_minimum_exceeded = trend == 'Downtrend' and np.exp(log_price) < chart_data['Close'].min()

        if is_before_date1 or is_maximum_exceeded or is_minimum_exceeded:
            line_data.append(math.nan)
        else:
            line_data.append(np.exp(log_price))
            if trend == 'Uptrend' and np.exp(log_price) <= chart_data['Close'].max():
                log_price = log_price + dif_log_close_per_day
            if trend == 'Downtrend' and np.exp(log_price) >= chart_data['Close'].min():
                log_price = log_price - dif_log_close_per_day

    trend_line_plot = mpf.make_addplot(line_data, color=line_color, label=trend)

    return trend_line_plot


def add_trendline(best_peaks, best_lows, chart_data, chart_settings):
    uptrend_lines = calculate_uptrend_line(best_peaks, best_lows)
    downtrend_lines = calculate_downtrend_line(best_peaks, best_lows)
    trendlines = []

    if not chart_settings['show_best_peaks_and_lows']:
        return trendlines

    for i in uptrend_lines:
        if not chart_settings['show_logarithmic_scale']:
            trendlines.append(draw_line_between_two_points(i[0], i[2], 'green', 'Uptrend', chart_data))
        else:
            trendlines.append(draw_logarithmic_line_between_two_points(i[0], i[2], 'green', 'Uptrend', chart_data))

    for i in downtrend_lines:
        if not chart_settings['show_logarithmic_scale']:
            trendlines.append(draw_line_between_two_points(i[0], i[2], 'red', 'Downtrend', chart_data))
        else:
            trendlines.append(draw_logarithmic_line_between_two_points(i[0], i[2], 'red', 'Downtrend', chart_data))

    return trendlines


def add_horizontal_lines(chart_data, chart_settings):
    horizontal_lines = []

    if chart_settings['show_best_peaks_and_lows'] and not chart_settings['show_nontrading']:
        hlines = []
        colors = []

        best_lows = find_best_lows(find_all_lows(chart_data), chart_settings)
        if len(best_lows) != 0:
            hlines.append(best_lows['Close'].iloc[-1])
            colors.append('r')

        best_peaks = find_best_peaks(find_all_peaks(chart_data), chart_settings)
        if len(best_peaks) != 0:
            hlines.append(best_peaks['Close'].iloc[-1])
            colors.append('g')

        horizontal_lines = dict(hlines=hlines, colors=colors, linestyle='-.', linewidths=1)

    return horizontal_lines

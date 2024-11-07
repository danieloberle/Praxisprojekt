import mplfinance as mpf


def find_bollinger_bands(chart_data, chart_settings):
    mav_for_bollinger_bands = chart_settings['mav_for_bollinger_bands']

    mav = chart_data['Close'].rolling(window=mav_for_bollinger_bands).mean()

    upper_band = mav + 2 * chart_data['Close'].rolling(window=mav_for_bollinger_bands).std()
    lower_band = mav - 2 * chart_data['Close'].rolling(window=mav_for_bollinger_bands).std()

    return [upper_band, lower_band]


def add_bollinger_bands(chart_data, chart_settings):
    bollinger_bands_list = []

    if chart_settings['show_bollinger_bands']:
        if len(chart_data) > chart_settings['mav_for_bollinger_bands']:
            upper_bollinger_band_plot = mpf.make_addplot(find_bollinger_bands(chart_data, chart_settings)[0],
                                                         label='Upper Bollinger Band',
                                                         color='gold',
                                                         width=0.8)
            bollinger_bands_list.append(upper_bollinger_band_plot)
            lower_bollinger_band_plot = mpf.make_addplot(find_bollinger_bands(chart_data, chart_settings)[1],
                                                         label='Lower Bollinger Band',
                                                         color='lime',
                                                         width=0.8)
            bollinger_bands_list.append(lower_bollinger_band_plot)

    return bollinger_bands_list

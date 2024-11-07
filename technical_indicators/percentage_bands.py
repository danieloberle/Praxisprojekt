import mplfinance as mpf


def find_percentage_bands(chart_data, chart_settings):
    mav = chart_settings['mav_for_percentage_bands']
    percentage = chart_settings['percentage_for_percentage_bands']

    mav = chart_data['Close'].rolling(window=mav).mean()

    upper_band = mav * (1 + percentage / 100)
    lower_band = mav * (1 - percentage / 100)

    return upper_band, lower_band


def add_percentage_bands(chart_data, chart_settings):
    percentage_bands_list = []

    if chart_settings['show_percentage_bands']:
        if len(chart_data) > chart_settings['mav_for_percentage_bands']:
            upper_percentage_band_plot = mpf.make_addplot(find_percentage_bands(chart_data, chart_settings)[0],
                                                          label='Upper Percentage Band',
                                                          color='olive',
                                                          width=0.8)
            percentage_bands_list.append(upper_percentage_band_plot)

            lower_percentage_band_plot = mpf.make_addplot(find_percentage_bands(chart_data, chart_settings)[1],
                                                          label='Lower Percentage Band',
                                                          color='orange',
                                                          width=0.8)
            percentage_bands_list.append(lower_percentage_band_plot)

    return percentage_bands_list

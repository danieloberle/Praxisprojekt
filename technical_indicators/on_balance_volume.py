import mplfinance as mpf


def calculate_on_balance_volume(chart_data):
    obv = [0]

    for i in range(1, len(chart_data)):
        if chart_data['Close'].iloc[i] > chart_data['Close'].iloc[i - 1]:
            obv.append(obv[-1] + chart_data['Volume'].iloc[i])
        elif chart_data['Close'].iloc[i] < chart_data['Close'].iloc[i - 1]:
            obv.append(obv[-1] - chart_data['Volume'].iloc[i])
        else:
            obv.append(obv[-1])

    return obv


def add_on_balance_volume(chart_data, chart_settings):
    on_balance_volume_list = []

    if chart_settings['show_on_balance_volume']:
        on_balance_volume_plot = mpf.make_addplot(calculate_on_balance_volume(chart_data),
                                                  label='On Balance Volume',
                                                  ylabel='OBV',
                                                  secondary_y=True,
                                                  color='grey',
                                                  width=0.8)
        on_balance_volume_list.append(on_balance_volume_plot)

    return on_balance_volume_list

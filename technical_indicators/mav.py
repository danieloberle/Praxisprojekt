import mplfinance as mpf


def calculate_mav(chart_data, days):
    mav = chart_data['Close'].rolling(window=days).mean()
    return mav


def add_mav(chart_data, chart_settings):
    mav_list = []
    colors = ['cyan', 'magenta', 'purple']

    for i in range(1, 4):
        if chart_settings['show_mav' + str(i)]:
            if len(chart_data) > chart_settings['mav' + str(i)]:
                mav_plot = mpf.make_addplot(calculate_mav(chart_data, chart_settings['mav' + str(i)]),
                                            label=f'MAV {i}',
                                            color=colors[i-1],
                                            width=0.8)

                mav_list.append(mav_plot)

    return mav_list

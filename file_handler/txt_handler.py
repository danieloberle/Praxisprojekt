import os


def get_security_list():
    security_list = []

    with open('securities/security_list.txt', 'r') as filehandler:
        for line in filehandler:
            security = line[:-1]
            security_list.append(security)

    return security_list


def add_security_to_security_list(symbol):
    security_list = get_security_list()

    if symbol in security_list:
        return

    security_list.append(symbol)
    save_security_list(security_list)


def save_security_list(security_list):
    with open('securities/security_list.txt', 'w') as filehandler:
        for line in security_list:
            filehandler.write(line + '\n')


def remove_security_from_security_list(symbol):
    security_list = get_security_list()
    with open('securities/security_list.txt', 'w') as filehandler:
        for line in security_list:
            if line.strip('\n') != symbol:
                filehandler.write(line + '\n')


def is_security_in_security_list(symbol):
    security_list = get_security_list()

    if symbol in security_list:
        return True
    else:
        return False


def create_chart_settings_list(symbol):
    directory = os.path.join('securities', symbol, 'chart_settings_list.txt')
    if not os.path.exists(directory):
        with open(directory, 'w') as filehandler:
            filehandler.write('')


def get_chart_settings_list(symbol):
    chart_settings_list = []

    if not is_security_in_security_list(symbol):
        return chart_settings_list

    directory = os.path.join('securities', symbol, 'chart_settings_list.txt')
    with open(directory, 'r') as filehandler:
        for line in filehandler:
            chart_settings = line[:-1]
            chart_settings_list.append(chart_settings)
    return chart_settings_list


def add_datetime_to_chart_settings_list(symbol, datetime):
    if not is_security_in_security_list(symbol):
        return

    chart_settings_list = get_chart_settings_list(symbol)
    chart_settings_list.append(datetime)
    save_chart_settings_list(symbol, chart_settings_list)


def save_chart_settings_list(symbol, chart_settings_list):
    directory = os.path.join('securities', symbol, 'chart_settings_list.txt')
    with open(directory, 'w') as filehandler:
        for line in chart_settings_list:
            filehandler.write(line + '\n')


def remove_settings_from_chart_settings_list(symbol, datetime):
    chart_settings_list = get_chart_settings_list(symbol)
    directory = os.path.join('securities', symbol, 'chart_settings_list.txt')
    with open(directory, 'w') as filehandler:
        for line in chart_settings_list:
            if line.strip('\n') != datetime:
                filehandler.write(line + '\n')

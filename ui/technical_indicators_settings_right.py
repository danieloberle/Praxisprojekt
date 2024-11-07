import customtkinter as ctk
import tkinter as tk


def create_checkbutton(parent, text, variable, row, column, command):
    checkbutton = tk.Checkbutton(parent,
                                 text=text,
                                 variable=variable,
                                 onvalue=True,
                                 offvalue=False,
                                 height=2,
                                 width=18,
                                 command=command)
    checkbutton.grid(row=row, column=column)


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
        spinbox.insert(0, '2')
        return
    value = int(spinbox.get())
    if value < 2:
        spinbox.delete(0, tk.END)
        spinbox.insert(0, '2')
        return
    if value > 200:
        spinbox.delete(0, tk.END)
        spinbox.insert(0, '200')
        return


def create_spinbox(parent, label_text, variable, label_row, label_column, spinbox_row, spinbox_column, command):
    ctk.CTkLabel(parent, text=label_text).grid(row=label_row, column=label_column)

    validate_input = parent.register(validate_spinbox_value)

    spinbox = tk.Spinbox(parent, from_=2, to=200, textvariable=variable, width=5, validate='key', validatecommand=(validate_input, '%P'), command=command)
    spinbox.grid(row=spinbox_row, column=spinbox_column)
    spinbox.bind('<FocusOut>', lambda event: (enforce_spinbox_limit(spinbox), command()))
    spinbox.bind('<Return>', lambda event: (enforce_spinbox_limit(spinbox), command()))


def create_vertical_spacer(parent, row, column):
    ctk.CTkLabel(parent, text='').grid(row=row, column=column)


class TechnicalIndicatorsSettingsRight:
    def __init__(self, parent, chart_settings, chart_settings_changed):
        self.parent = parent
        self.chart_settings = chart_settings
        self.chart_settings_changed = chart_settings_changed

        self.show_percentage_bands = tk.BooleanVar(value=self.chart_settings['show_percentage_bands'])
        self.mav_for_percentage_bands = tk.IntVar(value=self.chart_settings['mav_for_percentage_bands'])
        self.percentage_for_percentage_bands = tk.IntVar(value=self.chart_settings['percentage_for_percentage_bands'])
        self.show_bollinger_bands = tk.BooleanVar(value=self.chart_settings['show_bollinger_bands'])
        self.mav_for_bollinger_bands = tk.IntVar(value=self.chart_settings['mav_for_bollinger_bands'])
        self.show_on_balance_volume = tk.BooleanVar(value=self.chart_settings['show_on_balance_volume'])
        self.show_candlestick_patterns = tk.BooleanVar(value=self.chart_settings['show_candlestick_patterns'])

        self.destroy_widgets()
        self.create_widgets()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def validate_spinbox_inputs(self):
        try:
            print(isinstance(self.mav_for_bollinger_bands.get(), int))
            mav_for_percentage_bands = int(self.mav_for_percentage_bands.get())
            percentage_for_percentage_bands = int(self.percentage_for_percentage_bands.get())
            mav_for_bollinger_bands = int(self.mav_for_bollinger_bands.get())
            if any(bands_value <= 0 for bands_value in [mav_for_percentage_bands, percentage_for_percentage_bands, mav_for_bollinger_bands]):
                raise ValueError
            return True
        except (ValueError, TypeError):
            self.reset_bands_value()
            return False

    def reset_bands_value(self):
        self.mav_for_percentage_bands.set(self.chart_settings['mav_for_percentage_bands'])
        self.percentage_for_percentage_bands.set(self.chart_settings['percentage_for_percentage_bands'])
        self.mav_for_bollinger_bands.set(self.chart_settings['mav_for_bollinger_bands'])

    def update_chart_settings(self, *args):
        self.chart_settings.update({
            'show_percentage_bands': self.show_percentage_bands.get(),
            'mav_for_percentage_bands': self.mav_for_percentage_bands.get(),
            'percentage_for_percentage_bands': self.percentage_for_percentage_bands.get(),
            'show_bollinger_bands': self.show_bollinger_bands.get(),
            'mav_for_bollinger_bands': self.mav_for_bollinger_bands.get(),
            'show_on_balance_volume': self.show_on_balance_volume.get(),
            'show_candlestick_patterns': self.show_candlestick_patterns.get()
        })
        self.chart_settings_changed()

    def create_widgets(self):
        create_checkbutton(self.parent, 'Percentage Bands', self.show_percentage_bands, 1, 0, self.update_chart_settings)
        create_spinbox(self.parent, 'Moving Average', self.mav_for_percentage_bands, 1, 1, 1, 2, self.update_chart_settings)
        create_spinbox(self.parent, 'Percentage', self.percentage_for_percentage_bands, 2, 1, 2, 2, self.update_chart_settings)

        create_vertical_spacer(self.parent, 3, 0)

        create_checkbutton(self.parent, 'Bollinger Bands', self.show_bollinger_bands, 4, 0, self.update_chart_settings)
        create_spinbox(self.parent, 'Moving Average', self.mav_for_bollinger_bands, 4, 1, 4, 2, self.update_chart_settings)

        create_vertical_spacer(self.parent, 5, 0)

        create_checkbutton(self.parent, 'On Balance Volume', self.show_on_balance_volume, 6, 0, self.update_chart_settings)
        create_checkbutton(self.parent, 'Candlestick Patterns', self.show_candlestick_patterns, 7, 0, self.update_chart_settings)

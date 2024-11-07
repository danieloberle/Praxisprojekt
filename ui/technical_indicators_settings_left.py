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


def create_spinbox(parent, variable, row, column, command):
    validate_input = parent.register(validate_spinbox_value)

    spinbox = tk.Spinbox(parent, from_=2, to=200, textvariable=variable, width=5, validate='key', validatecommand=(validate_input, '%P'), command=command)
    spinbox.grid(row=row, column=column)
    spinbox.bind('<FocusOut>', lambda event: (enforce_spinbox_limit(spinbox), command()))
    spinbox.bind('<Return>', lambda event: (enforce_spinbox_limit(spinbox), command()))


def create_slider(parent, label_text, variable, label_row, label_column, slider_row, slider_column, command):
    ctk.CTkLabel(parent, text=label_text).grid(row=label_row, column=label_column)
    ctk.CTkSlider(parent, from_=10, to=400, variable=variable, command=command).grid(row=slider_row, column=slider_column)


def create_label(parent, variable, row, column):
    ctk.CTkLabel(parent, textvariable=variable).grid(row=row, column=column)


class TechnicalIndicatorsSettingsLeft:
    def __init__(self, parent, chart_settings, chart_settings_changed):
        self.parent = parent
        self.chart_settings = chart_settings
        self.chart_settings_changed = chart_settings_changed

        self.show_mav1 = tk.BooleanVar(value=self.chart_settings['show_mav1'])
        self.mav1 = tk.IntVar(value=self.chart_settings['mav1'])
        self.show_mav2 = tk.BooleanVar(value=self.chart_settings['show_mav2'])
        self.mav2 = tk.IntVar(value=self.chart_settings['mav2'])
        self.show_mav3 = tk.BooleanVar(value=self.chart_settings['show_mav3'])
        self.mav3 = tk.IntVar(value=self.chart_settings['mav3'])
        self.show_best_peaks_and_lows = tk.BooleanVar(value=self.chart_settings['show_best_peaks_and_lows'])
        self.best_peaks_significance = tk.IntVar(value=self.chart_settings['best_peaks_significance'])
        self.best_lows_significance = tk.IntVar(value=self.chart_settings['best_lows_significance'])

        self.destroy_widgets()
        self.create_widgets()

    def destroy_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def validate_spinbox_inputs(self):
        try:
            mav1, mav2, mav3 = int(self.mav1.get()), int(self.mav2.get()), int(self.mav3.get())
            if any(mav <= 0 for mav in [mav1, mav2, mav3]):
                raise ValueError
            return True
        except ValueError:
            self.reset_spinbox_values()
            return False

    def reset_spinbox_values(self):
        self.mav1.set(self.chart_settings['mav1'])
        self.mav2.set(self.chart_settings['mav2'])
        self.mav3.set(self.chart_settings['mav3'])

    def update_chart_settings(self, *args):
        if not self.validate_spinbox_inputs():
            return

        self.chart_settings.update({
            'show_mav1': self.show_mav1.get(),
            'mav1': self.mav1.get(),
            'show_mav2': self.show_mav2.get(),
            'mav2': self.mav2.get(),
            'show_mav3': self.show_mav3.get(),
            'mav3': self.mav3.get(),
            'show_best_peaks_and_lows': self.show_best_peaks_and_lows.get(),
            'best_peaks_significance': self.best_peaks_significance.get(),
            'best_lows_significance': self.best_lows_significance.get()
        })
        self.chart_settings_changed()

    def create_widgets(self):
        create_checkbutton(self.parent, 'Moving Average 1', self.show_mav1, 1, 0, self.update_chart_settings)
        create_spinbox(self.parent, self.mav1, 1, 1, self.update_chart_settings)

        create_checkbutton(self.parent, 'Moving Average 2', self.show_mav2, 2, 0, self.update_chart_settings)
        create_spinbox(self.parent, self.mav2, 2, 1, self.update_chart_settings)

        create_checkbutton(self.parent, 'Moving Average 3', self.show_mav3, 3, 0, self.update_chart_settings)
        create_spinbox(self.parent, self.mav3, 3, 1, self.update_chart_settings)

        ctk.CTkLabel(self.parent, text='').grid(row=4, column=0)

        create_checkbutton(self.parent, 'Peaks and Lows', self.show_best_peaks_and_lows, 5, 0, self.update_chart_settings)

        create_slider(self.parent, 'Peak Significance', self.best_peaks_significance, 6, 0, 6, 1, self.update_chart_settings)
        create_label(self.parent, self.best_peaks_significance, 6, 2)

        create_slider(self.parent, 'Low Significance', self.best_lows_significance, 7, 0, 7, 1, self.update_chart_settings)

        create_label(self.parent, self.best_lows_significance, 7, 2)

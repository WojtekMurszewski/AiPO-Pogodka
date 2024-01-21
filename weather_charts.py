import tkinter as tk
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO

class WeatherCharts:
    def __init__(self, weather_data):
        self.weather_data = weather_data
        self.canvas = None
        self.chart_canvas = None

    def plot_temperature_chart(self, date):
        try:
            forecast_data = self.weather_data.get_forecast_weather_data()
            hours = list(forecast_data[date].keys())
            print(hours)

            hour_objects = [datetime.strptime(hour, '%H:%M') for hour in hours]

            temperatures = [data['temperature'] for data in forecast_data[datetime.now().strftime('%A')].values()]
            print(temperatures)

            fig, ax = plt.subplots(figsize=(6, 2))
            ax.plot(hour_objects, temperatures, marker=' ', linestyle='-', color='#201335')
            ax.set_title(f'Temperature Chart for {date}')

            y_min = min(temperatures) - 2
            y_max = max(temperatures) + 2
            ax.set_ylim(y_min, y_max)

            # Dodanie wypełnienia obszaru pod krzywą
            ax.fill_between(hour_objects, -100, temperatures, color='#201335', alpha=0.3)

            print(f"Hours:{hour_objects}")

            for i, txt in enumerate(temperatures):
                ax.annotate(txt, (hour_objects[i], temperatures[i]), textcoords="offset points", xytext=(0, 10),
                            ha='center')

            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=len(hour_objects)))
            ax.set_xticks(hour_objects)
            ax.set_xticklabels([hour.strftime('%H:%M') for hour in hour_objects], rotation=0, ha='center')

            # Zmiana koloru tła
            fig.set_facecolor('#7EA3CC')  # 7EA3CC
            ax.set_facecolor('#7EA3CC')

            ax.set_yticklabels([])

            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True, labeltop=False)
            ax.yaxis.set_visible(False)

            if self.canvas:
                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=8, column=0)

        except Exception as e:
            print(f"Błąd podczas rysowania wykresu: {e}")

    def display_temperature_chart_for_day(self, day):
        try:
            forecast_data = self.weather_data.get_forecast_weather_data()
            hours = list(forecast_data[day].keys())

            hour_objects = [datetime.strptime(hour, '%H:%M') for hour in hours]

            temperatures = [data['temperature'] for data in forecast_data[day].values()]

            if self.canvas:
                self.canvas.get_tk_widget().destroy()  # Usuń aktualny wykres

            fig, ax = plt.subplots(figsize=(6, 2))
            ax.plot(hour_objects, temperatures, marker=' ', linestyle='-', color='#201335')
            ax.set_title(f'Temperature Chart for {day}')

            y_min = min(temperatures) - 2
            y_max = max(temperatures) + 2
            ax.set_ylim(y_min, y_max)

            # Dodanie wypełnienia obszaru pod krzywą
            ax.fill_between(hour_objects, -100, temperatures, color='#201335', alpha=0.3)

            for i, txt in enumerate(temperatures):
                ax.annotate(txt, (hour_objects[i], temperatures[i]), textcoords="offset points", xytext=(0, 10),
                            ha='center')

            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=len(hour_objects)))
            ax.set_xticks(hour_objects)
            ax.set_xticklabels([hour.strftime('%H:%M') for hour in hour_objects], rotation=0, ha='center')

            # Zmiana koloru tła
            fig.set_facecolor('#7EA3CC')
            ax.set_facecolor('#7EA3CC')

            ax.set_yticklabels([])

            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True, labeltop=False)
            ax.yaxis.set_visible(False)

            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=8, column=0)

        except Exception as e:
            print(f"Błąd podczas rysowania wykresu: {e}")

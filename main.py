import os
import tkinter as tk
from tkinter import ttk
from weather_ui import WeatherAppUI
from weather_charts import WeatherCharts
from weather_data import WeatherData
import styles
from datetime import datetime

class WeatherApp:
    def __init__(self):
        # Klucz API OpenWeatherMap
        self.api_key = "b44ecf95a35963e3701437527cec0f2a"

        # Inicjalizacja głównego okna tkinter
        self.root = tk.Tk()
        self.root.title("Pogódka")

        # Dane pogodowe
        self.ui = WeatherAppUI(self.root, None, None)
        self.weather_charts = WeatherCharts(None)
        self.weather_data = WeatherData(self.api_key, self.ui)
        self.ui.weather_data = self.weather_data
        self.weather_charts.weather_data = self.weather_data
        self.ui.weather_charts = self.weather_charts

        # Sprawdzenie, czy istnieje plik z ostatnią lokalizacją
        if os.path.exists("last_location.txt"):
            # Jeśli tak, wczytaj ostatnią lokalizację i pobierz aktualną prognozę
            self.ui.load_last_location()
            self.weather_data.get_weather(self.ui.entry.get())
            self.weather_charts.plot_temperature_chart(datetime.now().strftime('%A'))

        # Inicjalizacja ikony
        self.icon_label = tk.Label(self.root)
        self.icon_image = None

        # Inicjalizacja stylu
        self.style = ttk.Style()

        # Inicjalizacja atrybutu canvas
        self.canvas = None
        self.chart_canvas = None

        # Dodajemy atrybut do przechowywania canvas
        self.canvas = None

        # Konfiguracja kolumn w głównym oknie
        self.root.columnconfigure(0, minsize=250, weight=0)  # Kolumna 0 (miejsce na polu wprowadzania danych)
        self.root.columnconfigure(1, minsize=220, weight=1)  # Kolumna 1 (miejsce na przycisk Search)
        self.root.columnconfigure(2, minsize=220, weight=1)  # Kolumna 2 (miejsce na ikonę)
        self.root.columnconfigure(3, minsize=220, weight=1)  # Kolumna 3 (miejsce na ramkę prognozy)
        self.root.columnconfigure(4, minsize=0, weight=0)

        # Styl okna
        self.root.configure(**styles.WINDOW_STYLE)
        self.style.configure('TEntry', **styles.ENTRY_STYLE)
        self.style.configure('TButton', **styles.BUTTON_STYLE)
        self.header_frame = tk.Label(self.root, **styles.HEADER_STYLE)
        self.header_frame.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.style.configure('TLabel', **styles.LABEL_STYLE)

        # Tworzenie ramek dla prognozy na pięć dni
        self.forecast_frames = []
        for i in range(5):
            forecast_frame = ttk.Frame(self.root, **styles.FRAME_STYLE)
            forecast_frame.grid(row=7, column=i, padx=10, pady=10, sticky="nsew")
            self.forecast_frames.append(forecast_frame)

        # Inicjalizacja ikony
        self.icon_label = tk.Label(self.root)
        self.icon_image = None

        # Tworzenie interfejsu użytkownika
        self.ui.create_widgets()

        # Wyświetlenie danych o bieżącej pogodzie i prognozie
        if os.path.exists("last_location.txt"):
            self.ui.display_current_weather()
            self.ui.display_5_day_forecast()

        # Debug - wyświetlenie danych pogodowych na konsoli
        self.weather_data.print_weather_data()

    def run(self):
        # Uruchomienie głównej pętli programu
        self.root.mainloop()

if __name__ == "__main__":
    # Uruchomienie aplikacji pogodowej
    app = WeatherApp()
    app.run()

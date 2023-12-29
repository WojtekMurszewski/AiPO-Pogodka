import requests
import os
import tkinter as tk
from tkinter import Label, StringVar, messagebox
from collections import Counter

class WeatherApp:
    def __init__(self):
        self.api_key = "b44ecf95a35963e3701437527cec0f2a"
        self.font_style = ("Arial", 12)

        self.root = tk.Tk()
        self.root.title("Pogódka")

        self.create_widgets()

        # Sprawdzenie czy istnieje ostatnio wprowadzana lokalizacja 
        if os.path.exists("last_location.txt"):
            self.load_last_location()
            self.get_weather()

    def get_weather(self):
        location = self.entry.get()

        # Zapisywanie ostatnio wprowadzonej lokalizacji do pliku
        with open("last_location.txt", "w") as file:
            file.write(location)

        # Pobranie aktualnej pogody
        current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&lang=pl&appid={self.api_key}'
        current_result = requests.get(current_weather_url).json()

        # Pobranie prognozy na kolejne dni
        forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&lang=pl&appid={self.api_key}'
        forecast_result = requests.get(forecast_url).json()

        if current_result.get('cod') == '404' or forecast_result.get('cod') == '404':
            print("Nieprawidłowa lokalizacja!")
            messagebox.showerror("Błąd", "Nieprawidłowa lokalizacja! Spróbuj ponownie.")
            return

        # Wyświetlanie aktualnej pogody
        self.display_current_weather(current_result)

        # Wyświetlanie prognozy na kolejne dni
        self.display_5_day_forecast(forecast_result)

    def display_current_weather(self, result):
        self.city_name_var.set(f"Miasto: {result['name']}")
        timestamp_label = tk.Label(self.root, text=self.convert_timestamp(result['dt']), font=self.font_style)
        self.timestamp_var.set(f"Czas pomiaru: {timestamp_label.cget('text')}")
        self.description_var.set(f"Opis: {result['weather'][0]['description']}")
        self.temperature_var.set(f"Temperatura: {round(result['main']['temp'])}°C")
        self.feels_like_var.set(f"Odczuwalna: {round(result['main']['feels_like'])}°C")
        self.high_var.set(f"Najwyższa: {round(result['main']['temp_max'])}°C")
        self.low_var.set(f"Najniższa: {round(result['main']['temp_min'])}°C")
        self.humidity_var.set(f"Wilgotność: {result['main']['humidity']}%")
        self.wind_speed_var.set(f"Wiatr: {result['wind']['speed']} m/s")
        self.cloudiness_var.set(f"Zachmurzenie: {result['clouds']['all']}%")
        rain = result.get('rain', {}).get('1h', 0) 
        self.rain_var.set(f"Opady deszczu (1h): {rain} mm")
        sunrise_label = tk.Label(self.root, text=self.convert_timestamp(result['sys']['sunrise']), font=self.font_style)
        self.sunrise_var.set(f"Wschód: {sunrise_label.cget('text')}")
        sunset_label = tk.Label(self.root, text=self.convert_timestamp(result['sys']['sunset']), font=self.font_style)
        self.sunset_var.set(f"Zachód: {sunset_label.cget('text')}")

    def display_5_day_forecast(self, result):
        forecast_list = result.get('list', [])
        daily_temps = {}  # Słownik do przechowywania uśrednionych temperatur dla każdego dnia
        daily_descriptions = {}  # Słownik do przechowywania opisów pogody dla każdego dnia

        for forecast in forecast_list:
            date = self.convert_timestamp(forecast['dt']).split()[1]  # Pobieranie tylko daty
            if date not in daily_temps:
                daily_temps[date] = {'day': [], 'night': []}
                daily_descriptions[date] = []

            if '06:00:00' <= self.convert_timestamp(forecast['dt']).split()[0] < '18:00:00':
                daily_temps[date]['day'].append(forecast['main']['temp'])
            else:
                daily_temps[date]['night'].append(forecast['main']['temp'])

            daily_descriptions[date].append(forecast['weather'][0]['description'])

        # Obliczanie uśrednionych temperatur dla każdego dnia
        averaged_temps_day = {date: sum(temps['day']) / len(temps['day']) for date, temps in daily_temps.items()}
        averaged_temps_night = {date: sum(temps['night']) / len(temps['night']) for date, temps in daily_temps.items()}

        # Wybieranie najczęściej występującego opisu pogody dla każdego dnia
        most_common_descriptions = {date: Counter(desc).most_common(1)[0][0] for date, desc in daily_descriptions.items()}

        # Wyświetlanie uśrednionych temperatur i opisów dla każdego dnia
        row_counter = len(daily_temps) + 14
        for date in sorted(daily_temps.keys()):
            day_label = tk.Label(self.root, text=f"{date}: "
                                                f"Temperatura w dzień: {round(averaged_temps_day[date])}°C, "
                                                f"Temperatura w nocy: {round(averaged_temps_night[date])}°C, "
                                                f"Opis: {most_common_descriptions[date]}", font=self.font_style)
            day_label.grid(row=row_counter, column=0, columnspan=3, pady=10)
            row_counter += 1

    def load_last_location(self):
        # Wczytywanie ostatnio wprowadzonej lokalizacji z pliku
        with open("last_location.txt", "r") as file:
            last_location = file.read()
            self.entry = tk.Entry(self.root)
            self.entry.insert(0, last_location)
            self.entry.grid(row=0, column=1, padx=10, pady=10)

            self.button = tk.Button(self.root, text="Ok", command=self.get_weather)
            self.button.grid(row=0, column=2, padx=10, pady=10)

    def create_widgets(self):
        # Tworzenie etykiet i pól tekstowych
        self.label = Label(self.root, text="Podaj lokalizację:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # Sprawdź, czy plik istnieje
        if os.path.exists("last_location.txt"):
            self.load_last_location()
        else:
            self.entry = tk.Entry(self.root)
            self.entry.grid(row=0, column=1, padx=10, pady=10)

            self.button = tk.Button(self.root, text="Ok", command=self.get_weather)
            self.button.grid(row=0, column=2, padx=10, pady=10)

        # Tworzenie zmiennych StringVar do przechowywania danych o pogodzie
        self.city_name_var = StringVar()
        self.timestamp_var = StringVar()
        self.description_var = StringVar()
        self.temperature_var = StringVar()
        self.feels_like_var = StringVar()
        self.high_var = StringVar()
        self.low_var = StringVar()
        self.humidity_var = StringVar()
        self.wind_speed_var = StringVar()
        self.cloudiness_var = StringVar()
        self.sunrise_var = StringVar()
        self.sunset_var = StringVar()
        self.rain_var = StringVar()

        # Tworzenie etykiet służących do wyświetlania informacji o pogodzie
        Label(self.root, textvariable=self.city_name_var, font=self.font_style).grid(row=1, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.timestamp_var, font=self.font_style).grid(row=2, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.description_var, font=self.font_style).grid(row=3, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.temperature_var, font=self.font_style).grid(row=4, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.feels_like_var, font=self.font_style).grid(row=5, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.high_var, font=self.font_style).grid(row=6, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.low_var, font=self.font_style).grid(row=7, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.humidity_var, font=self.font_style).grid(row=8, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.wind_speed_var, font=self.font_style).grid(row=9, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.cloudiness_var, font=self.font_style).grid(row=10, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.rain_var, font=self.font_style).grid(row=11, column=0, columnspan=3, pady=10) 
        Label(self.root, textvariable=self.sunrise_var, font=self.font_style).grid(row=12, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.sunset_var, font=self.font_style).grid(row=13, column=0, columnspan=3, pady=10)

    def convert_timestamp(self, timestamp):
        # Konwertowanie formatu czasowego na Godzina:Minuta Dzień-Miesiąc-Rok
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %d-%m-%Y')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WeatherApp()
    app.run()

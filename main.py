import requests
import os
import tkinter as tk
from tkinter import Label, StringVar, messagebox
from collections import Counter

class WeatherApp:
    def __init__(self):
        # Klucz API OpenWeatherMap
        self.api_key = "b44ecf95a35963e3701437527cec0f2a"
        # Styl czcionki dla interfejsu
        self.font_style = ("Arial", 12)

        # Inicjalizacja głównego okna tkinter
        self.root = tk.Tk()
        self.root.title("Pogódka")

        # Dane pogodowe
        self.current_weather_data = {}
        self.forecast_weather_data = {}

        # Tworzenie interfejsu użytkownika
        self.create_widgets()

        # Sprawdzenie, czy istnieje plik z ostatnią lokalizacją
        if os.path.exists("last_location.txt"):
            # Jeśli tak, wczytaj ostatnią lokalizację i pobierz aktualną prognozę
            self.load_last_location()
            self.get_weather()

    def get_weather(self):
        # Pobranie lokalizacji z pola wprowadzania danych
        location = self.entry.get()

        # Zapisanie lokalizacji do pliku
        with open("last_location.txt", "w") as file:
            file.write(location)

        # Pobranie danych o bieżącej pogodzie
        current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&lang=pl&appid={self.api_key}'
        current_result = requests.get(current_weather_url).json()

        # Pobranie prognozy pogody na 5 dni
        forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&lang=pl&appid={self.api_key}'
        forecast_result = requests.get(forecast_url).json()

        # Sprawdzenie, czy dane zostały pobrane poprawnie
        if current_result.get('cod') == '404' or forecast_result.get('cod') == '404':
            print("Nieprawidłowa lokalizacja!")
            messagebox.showerror("Błąd", "Nieprawidłowa lokalizacja! Spróbuj ponownie.")
            return

        # Przetworzenie danych o bieżącej pogodzie i prognozie
        self.current_weather_data = self.process_current_data(current_result)
        self.forecast_weather_data = self.process_forecast_data(forecast_result)

        # Wyświetlenie danych o bieżącej pogodzie i prognozie
        self.display_current_weather()
        self.display_5_day_forecast()

        # Wświetlenie danych w konsoli
        self.print_weather_data()

    def process_current_data(self, result):
        # Przetwarzanie danych o bieżącej pogodzie
        current_data = {}

        current_data['city_name'] = result['name']
        current_data['timestamp'] = self.convert_timestamp(result['dt'])
        current_data['description'] = result['weather'][0]['description']
        current_data['temperature'] = round(result['main']['temp'])
        current_data['feels_like'] = round(result['main']['feels_like'])
        current_data['high'] = round(result['main']['temp_max'])
        current_data['low'] = round(result['main']['temp_min'])
        current_data['humidity'] = result['main']['humidity']
        current_data['wind_speed'] = result['wind']['speed']
        current_data['cloudiness'] = result['clouds']['all']
        current_data['rain'] = result.get('rain', {}).get('1h', 0)
        current_data['sunrise'] = self.convert_timestamp(result['sys']['sunrise'])
        current_data['sunset'] = self.convert_timestamp(result['sys']['sunset'])
      
        return current_data

    def process_forecast_data(self, result):
        # Przetwarzanie danych o prognozie pogody na 5 dni
        forecast_list = result.get('list', {})
        forecast_data = {}

        for forecast in forecast_list:
            date = self.convert_timestamp(forecast['dt']).split()[1]
            time = self.convert_timestamp(forecast['dt']).split()[0]

            if date not in forecast_data:
                forecast_data[date] = {}

            if time not in forecast_data[date]:
                forecast_data[date][time] = {}

            forecast_data[date][time]['timestamp'] = self.convert_timestamp(forecast['dt'])
            forecast_data[date][time]['description'] = forecast['weather'][0]['description']
            forecast_data[date][time]['temperature'] = round(forecast['main']['temp'])
            forecast_data[date][time]['feels_like'] = round(forecast['main']['feels_like'])
            forecast_data[date][time]['high'] = round(forecast['main']['temp_max'])
            forecast_data[date][time]['low'] = round(forecast['main']['temp_min'])
            forecast_data[date][time]['humidity'] = forecast['main']['humidity']
            forecast_data[date][time]['wind_speed'] = forecast['wind']['speed']
            forecast_data[date][time]['cloudiness'] = forecast['clouds']['all']
            forecast_data[date][time]['rain'] = forecast.get('rain', {}).get('1h', 0)

        return forecast_data

    def display_current_weather(self):
        # Wyświetlanie danych o bieżącej pogodzie na interfejsie użytkownika
        self.city_name_var.set(f"Miasto: {self.current_weather_data['city_name']}")
        self.timestamp_var.set(f"Czas pomiaru: {self.current_weather_data['timestamp']}")
        self.description_var.set(f"Opis: {self.current_weather_data['description']}")
        self.temperature_var.set(f"Temperatura: {self.current_weather_data['temperature']}°C")
        self.feels_like_var.set(f"Odczuwalna: {self.current_weather_data['feels_like']}°C")
        self.high_var.set(f"Najwyższa: {self.current_weather_data['high']}°C")
        self.low_var.set(f"Najniższa: {self.current_weather_data['low']}°C")
        self.humidity_var.set(f"Wilgotność: {self.current_weather_data['humidity']}%")
        self.wind_speed_var.set(f"Wiatr: {self.current_weather_data['wind_speed']} m/s")
        self.cloudiness_var.set(f"Zachmurzenie: {self.current_weather_data['cloudiness']}%")
        self.rain_var.set(f"Opady deszczu (1h): {self.current_weather_data['rain']} mm")
        self.sunrise_var.set(f"Wschód: {self.current_weather_data['sunrise']}")
        self.sunset_var.set(f"Zachód: {self.current_weather_data['sunset']}")

    def display_5_day_forecast(self):
        # Wyświetlanie prognozy pogody na 5 dni na interfejsie użytkownika
        daily_temps = {}  # Słownik do przechowywania uśrednionych temperatur dla każdego dnia
        daily_descriptions = {}  # Słownik do przechowywania opisów pogody dla każdego dnia

        for date, hourly_data in self.forecast_weather_data.items():
            daily_temps[date] = {'day': [], 'night': []}
            daily_descriptions[date] = []

            for hour, data in hourly_data.items():
                if '06:00:00' <= hour < '18:00:00':
                    daily_temps[date]['day'].append(data['temperature'])
                else:
                    daily_temps[date]['night'].append(data['temperature'])

                daily_descriptions[date].append(data['description'])

        # Obliczanie uśrednionych temperatur dla każdego dnia
        averaged_temps_day = {date: sum(temps['day']) / len(temps['day']) if temps['day'] else 0 for date, temps in daily_temps.items()}
        averaged_temps_night = {date: sum(temps['night']) / len(temps['night']) if temps['night'] else 0 for date, temps in daily_temps.items()}

        # Wybieranie najczęściej występującego opisu pogody dla każdego dnia
        most_common_descriptions = {date: Counter(desc).most_common(1)[0][0] for date, desc in daily_descriptions.items()}

        # Wyświetlanie uśrednionych temperatur i opisów dla każdego dnia
        row_counter = len(daily_temps) + 14
        for date in sorted(daily_temps.keys(), reverse=True):  # Dodano reverse=True
            day_label = tk.Label(self.root, text=f"{date}: "
                                                f"Opis: {most_common_descriptions[date]}, "
                                                f"Średnia temperatura w dzień: {round(averaged_temps_day[date])}°C, "
                                                f"Średnia temperatura w nocy: {round(averaged_temps_night[date])}°C",
                                                font=self.font_style)
            day_label.grid(row=row_counter, column=0, columnspan=3, pady=10)
            row_counter += 1

    def load_last_location(self):
        # Wczytywanie ostatniej lokalizacji z pliku
        with open("last_location.txt", "r") as file:
            last_location = file.read()
            self.entry = tk.Entry(self.root)
            self.entry.insert(0, last_location)
            self.entry.grid(row=0, column=1, padx=10, pady=10)

            self.button = tk.Button(self.root, text="Ok", command=self.get_weather)
            self.button.grid(row=0, column=2, padx=10, pady=10)

    def create_widgets(self):
        # Tworzenie widżetów interfejsu użytkownika
        self.label = Label(self.root, text="Podaj lokalizację:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        if os.path.exists("last_location.txt"):
            self.load_last_location()
        else:
            self.entry = tk.Entry(self.root)
            self.entry.grid(row=0, column=1, padx=10, pady=10)

            self.button = tk.Button(self.root, text="Ok", command=self.get_weather)
            self.button.grid(row=0, column=2, padx=10, pady=10)

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
        # Konwersja znacznika czasu na czytelną datę i godzinę
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %d-%m-%Y')

    def run(self):
        # Uruchomienie głównej pętli aplikacji tkinter
        self.root.mainloop()

    def print_weather_data(self):
        # Wyświetlanie danych w konsoli
        print("-------- Bieżąca Pogoda --------")
        for key, value in self.current_weather_data.items():
            print(f"{key}: {value}")
        print("--------------------------------")

        print("-------- Prognoza Pogody --------")
        for day, hourly_data in self.forecast_weather_data.items():
            print(f"---- {day} ----")
            for hour, data in hourly_data.items():
                print(f"Godzina {hour}:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                print("-----------------------------")
            print("******************************")
        print("--------------------------------")

if __name__ == "__main__":
    # Uruchomienie aplikacji pogodowej
    app = WeatherApp()
    app.run()

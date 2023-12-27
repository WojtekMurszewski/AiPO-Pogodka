import requests
import googletrans
import tkinter as tk
from tkinter import Label, StringVar
from googletrans import Translator

class WeatherApp:
    def __init__(self):
        self.api_key = "b44ecf95a35963e3701437527cec0f2a"
        self.translator = Translator()
        self.font_style = ("Arial", 12)

        self.root = tk.Tk()
        self.root.title("Weather App")

        self.create_widgets()

    def get_weather(self):
        location = self.entry.get()
        result = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={self.api_key}').json()

        city_name_translation = self.translate_text(result['name'])
        description_translation = self.translate_text(result['weather'][0]['description'])


        self.city_name_var.set(f"Miasto: {city_name_translation}")
        timestamp_label = tk.Label(self.root, text=self.convert_timestamp(result['dt']), font=self.font_style)
        self.timestamp_var.set(f"Czas pomiaru: {timestamp_label.cget('text')}")
        self.description_var.set(f"Opis: {description_translation}")
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

    def create_widgets(self):
        # Tworzenie etykiet i pól tekstowych
        self.label = Label(self.root, text="Podaj lokalizację:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

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
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %d-%m-%Y')
    
    def translate_text(self, text):
        translated = self.translator.translate(text, dest='pl')
        return translated.text



    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WeatherApp()
    app.run()

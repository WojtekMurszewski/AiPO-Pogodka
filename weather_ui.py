import os
import tkinter as tk
from tkinter import Label, StringVar,  ttk, Toplevel
from datetime import datetime
from PIL import Image, ImageTk
import requests
from io import BytesIO
from weather_charts import WeatherCharts
import styles
from collections import Counter

class WeatherAppUI:
    def __init__(self, root, weather_data, weather_charts):
        self.root = root
        self.weather_data = weather_data
        self.weather_charts = weather_charts
        self.icon_label = tk.Label(self.root, bg="white")
        # Styl czcionki dla interfejsu
        self.font_style = ("Arial", 14)
   
    def create_widgets(self):
        # Tworzenie widżetów interfejsu użytkownika
        if os.path.exists("last_location.txt"):
            self.load_last_location()
        else:
            self.entry = ttk.Entry(self.root, font=('Helvetica', 14))
            self.entry.grid(row=0, column=0, sticky="w")

            self.button = ttk.Button(self.root, text="Szukaj", command=lambda: self.handle_search())
            self.button.grid(row=0, column=0, sticky="e")

            self.icon_label = tk.Label(self.root, bg="white")
            self.icon_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

            self.chart_canvas = tk.Frame(master=self.root)

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

        Label(self.root, textvariable=self.city_name_var, font=("Verdana", 24), bg="#7EA3CC", fg="black").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        Label(self.root, textvariable=self.timestamp_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        Label(self.root, textvariable=self.description_var, font=("Verdana", 20), bg="#7EA3CC", fg="black").grid(row=3, column=1, pady=10, padx=10, sticky="w")
        Label(self.root, textvariable=self.temperature_var, font=("Verdana", 40), bg="#7EA3CC", fg="black").grid(row=3, column=0, padx=(150, 10), pady=10, sticky="w")
        Label(self.root, textvariable=self.feels_like_var, font=("Verdana", 16), bg="#7EA3CC", fg="black").grid(row=3, column=1, pady=10, padx=10, sticky="sw")
        Label(self.root, textvariable=self.high_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=4, column=0)
        Label(self.root, textvariable=self.low_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=5, column=0)
        Label(self.root, textvariable=self.humidity_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=4, column=2)
        Label(self.root, textvariable=self.wind_speed_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=5, column=2)
        Label(self.root, textvariable=self.cloudiness_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=4, column=3)
        Label(self.root, textvariable=self.rain_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=5, column=3)
        Label(self.root, textvariable=self.sunrise_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=4, column=1)
        Label(self.root, textvariable=self.sunset_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=5, column=1)
        
        self.weather_charts = WeatherCharts(self.weather_data)
        self.weather_charts.plot_temperature_chart(datetime.now().strftime('%A'))

    

        timestamps = [timestamp for day, hourly_data in self.weather_data.get_forecast_weather_data().items()
                      for timestamp in hourly_data.keys()]

        date_combobox = ttk.Combobox(self.root, values=list(self.weather_data.get_forecast_weather_data().keys()))
        date_combobox.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        hour_combobox = ttk.Combobox(self.root, values=["01:00", "04:00", "07:00", "10:00", "13:00", "16:00", "19:00", "22:00"])
        hour_combobox.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        show_details_button = ttk.Button(self.root, text="Show Details", command=lambda: self.show_weather_details(date_combobox.get(), hour_combobox.get()))
        show_details_button.grid(row=0, column=4, padx=10, pady=10, sticky="w")


    def display_current_weather(self):
        current_data = self.weather_data.get_current_weather_data()

        # Wyświetlanie danych o bieżącej pogodzie na interfejsie użytkownika
        self.city_name_var.set(f"{current_data['city_name']}")
        self.timestamp_var.set(f"Current weather\n{current_data['timestamp']}")
        self.description_var.set(f"{current_data['description']}")
        self.temperature_var.set(f"{current_data['temperature']}°C")
        self.feels_like_var.set(f"Feels like {current_data['feels_like']}°C")
        self.high_var.set(f"Highest temp.\n{current_data['high']}°C")
        self.low_var.set(f"Lowest temp.\n{current_data['low']}°C")
        self.humidity_var.set(f"Humidity\n{current_data['humidity']}%")
        self.wind_speed_var.set(f"Wind speed\n{current_data['wind_speed']} m/s")
        self.cloudiness_var.set(f"Cloudiness\n{current_data['cloudiness']}%")
        self.rain_var.set(f"Rain (1h)\n{current_data['rain']} mm")
        sunrise_time = datetime.strptime(current_data['sunrise'], '%H:%M %A %d-%m-%Y').strftime('%H:%M')
        self.sunrise_var.set(f"Sunrise\n{sunrise_time}")
        sunset_time = datetime.strptime(current_data['sunset'], '%H:%M %A %d-%m-%Y').strftime('%H:%M')
        self.sunset_var.set(f"Sunset\n{sunset_time}")
        # Wyświetlania ikony
        self.update_icon(current_data['icon_url'])     

    def display_5_day_forecast(self):
        forecast_data = self.weather_data.get_forecast_weather_data()
        
        # Stworzenie ramki dla prognozy na pięć dni
        forecast_frame = ttk.Frame(self.root, **styles.FRAME_STYLE)
        forecast_frame.grid(row=7, column=0, columnspan=5, pady=10, sticky="nsew")

        daily_temps = {}  # Słownik do przechowywania uśrednionych temperatur dla każdego dnia
        daily_descriptions = {}  # Słownik do przechowywania opisów pogody dla każdego dnia

        for date, hourly_data in forecast_data.items():
            daily_temps[date] = {'day': [], 'night': []}
            daily_descriptions[date] = []

            for hour, data in hourly_data.items():
                if '06:00:00' <= hour < '18:00:00':
                    daily_temps[date]['day'].append(data['temperature'])
                else:
                    daily_temps[date]['night'].append(data['temperature'])

                daily_descriptions[date].append(data['description'])

        # Obliczanie uśrednionych temperatur dla każdego dnia
        averaged_temps_day = {date: sum(temps['day']) / len(temps['day']) if temps['day'] else 0 for date, temps in
                            daily_temps.items()}
        averaged_temps_night = {date: sum(temps['night']) / len(temps['night']) if temps['night'] else 0 for date, temps
                                in daily_temps.items()}

        # Wybieranie najczęściej występującego opisu pogody dla każdego dnia
        most_common_descriptions = {date: Counter(desc).most_common(1)[0][0] for date, desc in
                                    daily_descriptions.items()}

        # Wyświetlanie uśrednionych temperatur i opisów dla każdego dnia w ramce
        for i, date in enumerate(daily_temps.keys()):
            day_label = tk.Label(forecast_frame, text=f"{date}\n"
                                                    f"{most_common_descriptions[date]}\n"
                                                    f"Avg. temp. during day: {round(averaged_temps_day[date])}°C\n"
                                                    f"Avg. temp. during night: {round(averaged_temps_night[date])}°C",
                                                    font=self.font_style)
            day_label.grid(row=0, column=i, pady=10)

            button = ttk.Button(forecast_frame, text="Show chart", command=lambda d=date: self.weather_charts.display_temperature_chart_for_day(d))
            button.grid(row=1, column=i, pady=5)
        
    def update_icon(self, icon_url):
        try:
            response = requests.get(icon_url)
            if response.status_code == 200:
                # Pobierz obraz z odpowiedzi
                icon_data = BytesIO(response.content)
                icon_image = Image.open(icon_data)
                # Skonwertuj obraz do formatu PhotoImage
                image = ImageTk.PhotoImage(icon_image)
                # Aktualizacja ikony
                if image:
                    self.icon_image = image
                    self.icon_label.config(image=self.icon_image, bg = "#7EA3CC")
                    self.icon_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
            else:
                print(f"Błąd pobierania ikony: {response.status_code}")
        except Exception as e:
            print(f"Błąd podczas aktualizacji ikony: {e}")

    def load_last_location(self):
        # Wczytywanie ostatniej lokalizacji z pliku
        with open("last_location.txt", "r") as file:
            last_location = file.read()
            self.entry = ttk.Entry(self.root, font=self.font_style)
            self.entry.insert(0, last_location)
            self.entry.grid(row=0, column=0, sticky="w")

            self.button = ttk.Button(self.root, text="Search", command=lambda: self.handle_search())
            self.button.grid(row=0, column=0, sticky="e")

    def handle_search(self):
        # Metoda obsługująca przycisk "Search"
        location = self.entry.get()
        if location:
            self.weather_data.get_weather(location)
            self.display_current_weather()
            self.display_5_day_forecast()
            self.weather_charts.plot_temperature_chart(datetime.now().strftime('%A'))
    
    def show_weather_details(self, selected_date, selected_hour):
        # Metoda służaca do wyświetlania szczegółow wybranej prgnozy pogody
        forecast_data = self.weather_data.get_forecast_weather_data()
        current_data = self.weather_data.get_current_weather_data()
        selected_data = {}


        if selected_date in forecast_data:
            if selected_hour in forecast_data[selected_date]:
                selected_data = forecast_data[selected_date][selected_hour]

 
            weather_details_window = Toplevel()
            weather_details_window.title("Weather Details")

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
            self.rain_var = StringVar()

            self.city_name_var.set(f"{current_data['city_name']}")
            self.timestamp_var.set(f"{selected_data['timestamp']}")
            self.description_var.set(f"Weather details {selected_data['description']}")
            self.temperature_var.set(f"Temperature {selected_data['temperature']}°C")
            self.feels_like_var.set(f"Feels like {selected_data['feels_like']}°C")
            self.high_var.set(f"Highest temp. {selected_data['high']}°C")
            self.low_var.set(f"Lowest temp.{selected_data['low']}°C")
            self.humidity_var.set(f"Humidity {selected_data['humidity']}%")
            self.wind_speed_var.set(f"Wind speed {selected_data['wind_speed']} m/s")
            self.cloudiness_var.set(f"Cloudiness {selected_data['cloudiness']}%")
            self.rain_var.set(f"Rain (1h) {selected_data['rain']} mm")

            Label(weather_details_window, textvariable=self.city_name_var, font=self.font_style, bg="white", fg="black").grid(row=1, column=0)
            Label(weather_details_window, textvariable=self.timestamp_var, font=self.font_style, bg="white", fg="black").grid(row=2, column=0)
            Label(weather_details_window, textvariable=self.description_var, font=self.font_style, bg="white", fg="black").grid(row=3, column=0)
            Label(weather_details_window, textvariable=self.temperature_var, font=self.font_style, bg="white", fg="black").grid(row=4, column=0)
            Label(weather_details_window, textvariable=self.feels_like_var, font=self.font_style, bg="white", fg="black").grid(row=5, column=0)
            Label(weather_details_window, textvariable=self.high_var, font=self.font_style, bg="white", fg="black").grid(row=6, column=0)
            Label(weather_details_window, textvariable=self.low_var, font=self.font_style, bg="white", fg="black").grid(row=7, column=0)
            Label(weather_details_window, textvariable=self.humidity_var, font=self.font_style, bg="white", fg="black").grid(row=8, column=0)
            Label(weather_details_window, textvariable=self.wind_speed_var, font=self.font_style, bg="white", fg="black").grid(row=9, column=0)
            Label(weather_details_window, textvariable=self.cloudiness_var, font=self.font_style, bg="white", fg="black").grid(row=10, column=0)
            Label(weather_details_window, textvariable=self.rain_var, font=self.font_style, bg="white", fg="black").grid(row=11, column=0)

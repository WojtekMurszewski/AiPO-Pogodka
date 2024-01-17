import requests
import os
import tkinter as tk
from tkinter import Label, StringVar, messagebox, ttk
from collections import Counter
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import styles
from collections import OrderedDict

class WeatherData:
    def __init__(self, api_key, ui):
        self.api_key = api_key
        self.current_weather_data = {}
        self.forecast_weather_data = OrderedDict()
        self.current_weather_data['icon_url'] = None
        self.weather_charts = WeatherCharts(self)
        self.ui = ui

    def get_weather(self, location):
        if location is None:
            location = self.ui.entry.get()

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

        # Dodanie aktualnej daty do wykresu
        self.weather_charts = WeatherCharts(self)
        current_date = datetime.now().strftime('%A')
        self.weather_charts.plot_temperature_chart(current_date)

        # Wyświetlenie danych o bieżącej pogodzie i prognozie
        self.ui.display_current_weather()
        self.ui.display_5_day_forecast()

        # Update the weather icon
        icon_url = self.current_weather_data.get('icon_url')
        if icon_url:
            self.ui.update_icon(icon_url)

        # Wświetlenie danych w konsoli
        self.print_weather_data()

        # Dodanie aktualnej daty do wykresu
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.weather_charts.plot_temperature_chart(current_date)

    def process_current_data(self, result):
        # Przetwarzanie danych o bieżącej pogodzie
        current_data = {}

        current_data['city_name'] = result['name']
        icon_id = result['weather'][0]['icon']
        icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        self.update_icon(icon_url)
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
        forecast_data = OrderedDict()

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
    
    def convert_timestamp(self, timestamp):
        # Konwersja znacznika czasu na czytelną datę i godzinę
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %A %d-%m-%Y')
    
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

    def update_icon(self, icon_url):
        # Metoda do aktualizacji ikony pogody
        self.current_weather_data['icon_url'] = icon_url

class WeatherCharts: 

    def __init__(self, weather_data):
        self.weather_data = weather_data
        self.canvas = None
        self.chart_canvas = None

    def plot_temperature_chart(self, date):
        try:
            hours = list(self.weather_data.forecast_weather_data[datetime.now().strftime('%A')].keys())
            print(hours)

            hour_objects = [datetime.strptime(hour, '%H:%M') for hour in hours]

            temperatures = [data['temperature'] for data in self.weather_data.forecast_weather_data[datetime.now().strftime('%A')].values()]
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
                ax.annotate(txt, (hour_objects[i], temperatures[i]), textcoords="offset points", xytext=(0, 10), ha='center')

            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=len(hour_objects)))
            ax.set_xticks(hour_objects)
            ax.set_xticklabels([hour.strftime('%H:%M') for hour in hour_objects], rotation=0, ha='center')

            # Zmiana koloru tła
            fig.set_facecolor('#7EA3CC') #7EA3CC
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
            hours = list(self.weather_data.forecast_weather_data[day].keys())

            hour_objects = [datetime.strptime(hour, '%H:%M') for hour in hours]

            temperatures = [data['temperature'] for data in self.weather_data.forecast_weather_data[day].values()]

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
                ax.annotate(txt, (hour_objects[i], temperatures[i]), textcoords="offset points", xytext=(0, 10), ha='center')

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


class WeatherAppUI:
    def __init__(self, root, weather_data, font_style):
        self.root = root
        self.weather_data = weather_data
        self.font_style = font_style
        self.weather_data = weather_data

    def create_widgets(self):
        # Tworzenie widżetów interfejsu użytkownika
        if os.path.exists("last_location.txt"):
            self.load_last_location()
        else:
            self.entry = ttk.Entry(self.root, font=('Helvetica', 14))
            self.entry.grid(row=0, column=0, sticky="w")

            self.button = ttk.Button(self.root, text="Szukaj", command=lambda: self.weather_data.get_weather(self.entry.get()))
            self.button.grid(row=0, column=1, sticky="w")

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

        Label(self.root, textvariable=self.city_name_var, font=("Verdana", 16), bg="#7EA3CC", fg="black").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        Label(self.root, textvariable=self.timestamp_var, font=self.font_style, bg="#7EA3CC", fg="black").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        Label(self.root, textvariable=self.description_var, font=("Verdana", 16), bg="#7EA3CC", fg="black").grid(row=3, column=1, pady=10, padx=10, sticky="w")
        Label(self.root, textvariable=self.temperature_var, font=("Verdana", 40), bg="#7EA3CC", fg="black").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        Label(self.root, textvariable=self.feels_like_var, font=("Verdana", 12), bg="#7EA3CC", fg="black").grid(row=3, column=1, pady=10, padx=10, sticky="sw")
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

    def display_current_weather(self):
        # Wyświetlanie danych o bieżącej pogodzie na interfejsie użytkownika
        self.city_name_var.set(f"{self.weather_data.current_weather_data['city_name']}")
        self.timestamp_var.set(f"Aktualna pogoda\n{self.weather_data.current_weather_data['timestamp']}")
        print(f"seimano:{self.weather_data.current_weather_data['timestamp']}")
        self.description_var.set(f"{self.weather_data.current_weather_data['description']}")
        self.temperature_var.set(f"{self.weather_data.current_weather_data['temperature']}°C")
        self.feels_like_var.set(f"Temp. odczuwalna {self.weather_data.current_weather_data['feels_like']}°C")
        self.high_var.set(f"Najwyższa temp.\n{self.weather_data.current_weather_data['high']}°C")
        self.low_var.set(f"Najniższa temp.\n{self.weather_data.current_weather_data['low']}°C")
        self.humidity_var.set(f"Wilgotność\n{self.weather_data.current_weather_data['humidity']}%")
        self.wind_speed_var.set(f"Wiatr\n{self.weather_data.current_weather_data['wind_speed']} m/s")
        self.cloudiness_var.set(f"Zachmurzenie\n{self.weather_data.current_weather_data['cloudiness']}%")
        self.rain_var.set(f"Opady deszczu (1h)\n{self.weather_data.current_weather_data['rain']} mm")
        sunrise_time = datetime.strptime(self.weather_data.current_weather_data['sunrise'], '%H:%M %A %d-%m-%Y').strftime('%H:%M')
        self.sunrise_var.set(f"Wschód\n{sunrise_time}")
        sunset_time = datetime.strptime(self.weather_data.current_weather_data['sunset'], '%H:%M %A %d-%m-%Y').strftime('%H:%M')
        self.sunset_var.set(f"Zachód\n{sunset_time}")

    def display_5_day_forecast(self):
        # Stworzenie ramki dla prognozy na pięć dni
        forecast_frame = ttk.Frame(self.root, **styles.FRAME_STYLE)
        forecast_frame.grid(row=7, column=0, columnspan=5, pady=10, sticky="nsew")

        daily_temps = {}  # Słownik do przechowywania uśrednionych temperatur dla każdego dnia
        daily_descriptions = {}  # Słownik do przechowywania opisów pogody dla każdego dnia

        for date, hourly_data in self.weather_data.forecast_weather_data.items():
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
                                                    f"Śr. temp. w dzień: {round(averaged_temps_day[date])}°C\n"
                                                    f"Śr. temp. w nocy: {round(averaged_temps_night[date])}°C",
                                                    font=self.font_style)
            day_label.grid(row=0, column=i, pady=10)

            button = ttk.Button(forecast_frame, text="Pokaż wykres", command=lambda d=date: self.weather_charts.display_temperature_chart_for_day(d))
            button.grid(row=1, column=i, pady=5)

    def update_icon(self, icon_url):
        # Pobranie obrazu z URL
        print("Test update")
        image = self.get_image_from_url(icon_url)

        # Aktualizacja ikony
        if image:
            self.icon_image = image
            self.icon_label.config(image=self.icon_image, bg = "#7EA3CC")
            self.icon_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def get_image_from_url(self, url):
        try:
            print("Test get")
            # Pobranie obrazu z URL
            response = requests.get(url, stream=True)
            image = Image.open(response.raw)
            photo = ImageTk.PhotoImage(image)

            return photo
        except Exception as e:
            print(f"Błąd podczas pobierania obrazu: {e}")
            return None

    def load_last_location(self):
        # Wczytywanie ostatniej lokalizacji z pliku
        with open("last_location.txt", "r") as file:
            last_location = file.read()
            self.entry = ttk.Entry(self.root, font=('Helvetica', 14))
            self.entry.insert(0, last_location)
            self.entry.grid(row=0, column=0, sticky="w")

            self.button = ttk.Button(self.root, text="Szukaj", command=lambda: self.weather_data.get_weather(self.entry.get()))
            self.button.grid(row=0, column=1, sticky="w")
            
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
        self.ui = WeatherAppUI(self.root, None, self.font_style)  
        self.weather_data = WeatherData(self.api_key, self.ui)

        # Ustawienie ui w WeatherData po jego utworzeniu
        self.ui.weather_data = self.weather_data

        # Tworzenie interfejsu użytkownika
        self.ui.create_widgets()

        # Inicjalizacja ikony
        self.icon_label = tk.Label(self.root)
        self.icon_image = None

        # Inicjalizacja stylu
        self.style = ttk.Style()


        # Ustawienie ui w WeatherData po jego utworzeniu
        self.weather_data.ui = self.ui

        # Inicjalizacja atrybutu canvas
        self.canvas = None
        self.chart_canvas = None

        self.chart_canvas = tk.Frame(master=self.root)
        self.chart_canvas.grid(row=8, column=0, columnspan=4)

        # Dodajemy atrybut do przechowywania canvas
        self.canvas = None

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

        # Sprawdzenie, czy istnieje plik z ostatnią lokalizacją
        if os.path.exists("last_location.txt"):
            # Jeśli tak, wczytaj ostatnią lokalizację i pobierz aktualną prognozę
            self.ui.load_last_location()
            self.weather_data.get_weather(self.ui.entry.get())
            self.weather_data.weather_charts.plot_temperature_chart(datetime.now().strftime('%A'))

    def run(self):
        # Uruchomienie głównej pętli aplikacji tkinter
        self.root.mainloop()


if __name__ == "__main__":
    # Uruchomienie aplikacji pogodowej
    app = WeatherApp()
    app.run()
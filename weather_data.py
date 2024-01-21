import requests
from collections import OrderedDict
from datetime import datetime

class WeatherData:
    def __init__(self, api_key, ui):
        self.api_key = api_key
        self.ui = ui
        self.current_weather = CurrentWeatherData(api_key)
        self.forecast_weather = ForecastWeatherData(api_key)
        self.current_weather_data = {}  
        self.forecast_weather_data = {}

    def get_weather(self, location=None):
        if location is None:
            location = self.ui.entry.get()

        with open("last_location.txt", "w") as file:
            file.write(location)

        current_result, forecast_result = self.fetch_weather_data(location)

        if not self.validate_weather_data(current_result, forecast_result):
            return

        self.process_weather_data(current_result, forecast_result)

        return self.get_current_weather_data(), self.get_forecast_weather_data()
    
    def fetch_weather_data(self, location):
        current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&lang=en&appid={self.api_key}'
        current_result = requests.get(current_weather_url).json()

        forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&lang=en&appid={self.api_key}'
        forecast_result = requests.get(forecast_url).json()

        return current_result, forecast_result

    def validate_weather_data(self, current_result, forecast_result):
        if current_result.get('cod') == '404' or forecast_result.get('cod') == '404':
            print("Nieprawidłowa lokalizacja!")
            return False
        return True

    def process_weather_data(self, current_result, forecast_result):
        try:
            self.current_weather_data = self.current_weather.process_current_data(current_result)
            self.forecast_weather_data = self.forecast_weather.process_forecast_data(forecast_result)
        except Exception as e:
            print(f"Błąd podczas przetwarzania danych: {e}")

    def get_current_weather_data(self):
        return self.current_weather_data

    def get_forecast_weather_data(self):
        return self.forecast_weather_data

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

    @staticmethod
    def convert_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %A %d-%m-%Y')


class CurrentWeatherData:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def process_current_data(self, result):
        # Przetwarzanie danych o bieżącej pogodzie
        current_data = {}

        icon_id = result['weather'][0]['icon']
        current_data['city_name'] = result['name']
        current_data['icon_url'] = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        current_data['timestamp'] = WeatherData.convert_timestamp(result['dt'])
        current_data['description'] = result['weather'][0]['description']
        current_data['temperature'] = round(result['main']['temp'])
        current_data['feels_like'] = round(result['main']['feels_like'])
        current_data['high'] = round(result['main']['temp_max'])
        current_data['low'] = round(result['main']['temp_min'])
        current_data['humidity'] = result['main']['humidity']
        current_data['wind_speed'] = result['wind']['speed']
        current_data['cloudiness'] = result['clouds']['all']
        current_data['rain'] = result.get('rain', {}).get('1h', 0)
        current_data['sunrise'] = WeatherData.convert_timestamp(result['sys']['sunrise'])
        current_data['sunset'] = WeatherData.convert_timestamp(result['sys']['sunset'])

        return current_data

class ForecastWeatherData:
    def __init__(self, api_key):
        self.api_key = api_key

    def process_forecast_data(self, result):
        # Przetwarzanie danych o prognozie pogody na 5 dni
        forecast_list = result.get('list', {})
        forecast_data = OrderedDict()

        for forecast in forecast_list:
            date = WeatherData.convert_timestamp(forecast['dt']).split()[1]
            time = WeatherData.convert_timestamp(forecast['dt']).split()[0]

            if date not in forecast_data:
                forecast_data[date] = {}

            if time not in forecast_data[date]:
                forecast_data[date][time] = {}

            forecast_data[date][time]['timestamp'] = WeatherData.convert_timestamp(forecast['dt'])
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


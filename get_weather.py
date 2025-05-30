"""
    Файл для получения погоды
    Реализован на API OpenWeatherMap, тк я на нём уже писал код и оно имеет хороший модуль под Python

    Как работает?
    Подключение через ключ API => получаем данные о погоде => фильтруем и собираем в кучу => выводим через функцию,
    которую используем в основном файле

    Если запустить этот файл, то выведется погода в Саратове

    ВНИМАНИЕ! Код работал, выводил всё как нужно, но кончилась бесплатная API и теперь ПРОГНОЗЫ НЕДОСТУПНЫ
    и он будет везде выводить текущую погоду, пришлось исправить таблицу в index.html, она была более объёмная и
    расписана по времени (утро, день, вечер, ночь)
"""


from pyowm import OWM
from pyowm.utils.config import get_default_config
from pyowm.commons.exceptions import NotFoundError
from datetime import datetime, timedelta
import pytz


def city_weather(city_name):
    try:
        # Настройка подключения
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM('a91d60ef8afa92a36fecc341203b0b40', config_dict)
        mgr = owm.weather_manager()

        # Получаем текущую погоду
        observation = mgr.weather_at_place(city_name)
        current_weather = observation.weather
        current_data = {
            'time': 'Текущая',
            'temp': f"{round(current_weather.temperature('celsius')['temp'])}°C",
            'feels_like': f"{round(current_weather.temperature('celsius')['feels_like'])}°C",
            'wind': f"{current_weather.wind()['speed']} м/с",
            'humidity': f"{current_weather.humidity}%",
            'status': current_weather.detailed_status,
            'icon': current_weather.weather_icon_url()
        }

        # Получаем прогноз на сегодня
        forecast = mgr.forecast_at_place(city_name, '3h')
        tz = pytz.timezone('Europe/Moscow')
        now = datetime.now(tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Фильтруем только сегодняшние прогнозы
        todays_forecasts = [
            w for w in forecast.forecast.weathers
            if today_start.timestamp() <= w.reference_time() < today_end.timestamp()
        ]

        # Если нет прогнозов на сегодня, используем текущую погоду для всех периодов
        if not todays_forecasts:
            weather_data = {
                'city': city_name,
                'current': current_data,
                'morning': current_data,
                'noon': current_data,
                'evening': current_data,
                'night': current_data
            }
            return weather_data

        # Находим ближайшие прогнозы для каждого периода
        def get_nearest_weather(target_hour):
            target_time = today_start.replace(hour=target_hour)
            return min(todays_forecasts, key=lambda w: abs(w.reference_time() - target_time.timestamp()))

        morning_weather = get_nearest_weather(6)
        noon_weather = get_nearest_weather(12)
        evening_weather = get_nearest_weather(18)
        night_weather = get_nearest_weather(0) if now.hour < 6 else current_weather

        # Собираем все данные
        weather_data = {
            'city': city_name,
            'current': current_data,
            'morning': {
                'time': 'Утро',
                'temp': f"{round(morning_weather.temperature('celsius')['temp'])}°C",
                'feels_like': f"{round(morning_weather.temperature('celsius')['feels_like'])}°C",
                'wind': f"{morning_weather.wind()['speed']} м/с",
                'humidity': f"{morning_weather.humidity}%",
                'status': morning_weather.detailed_status,
                'icon': morning_weather.weather_icon_url()
            },
            'noon': {
                'time': 'День',
                'temp': f"{round(noon_weather.temperature('celsius')['temp'])}°C",
                'feels_like': f"{round(noon_weather.temperature('celsius')['feels_like'])}°C",
                'wind': f"{noon_weather.wind()['speed']} м/с",
                'humidity': f"{noon_weather.humidity}%",
                'status': noon_weather.detailed_status,
                'icon': noon_weather.weather_icon_url()
            },
            'evening': {
                'time': 'Вечер',
                'temp': f"{round(evening_weather.temperature('celsius')['temp'])}°C",
                'feels_like': f"{round(evening_weather.temperature('celsius')['feels_like'])}°C",
                'wind': f"{evening_weather.wind()['speed']} м/с",
                'humidity': f"{evening_weather.humidity}%",
                'status': evening_weather.detailed_status,
                'icon': evening_weather.weather_icon_url()
            },
            'night': {
                'time': 'Ночь',
                'temp': f"{round(night_weather.temperature('celsius')['temp'])}°C",
                'feels_like': f"{round(night_weather.temperature('celsius')['feels_like'])}°C",
                'wind': f"{night_weather.wind()['speed']} м/с" if hasattr(night_weather, 'wind')
                else current_data['wind'],
                'humidity': f"{night_weather.humidity}%" if hasattr(night_weather, 'humidity')
                else current_data['humidity'],
                'status': night_weather.detailed_status if hasattr(night_weather, 'detailed_status')
                else current_data['status'],
                'icon': night_weather.weather_icon_url() if hasattr(night_weather, 'weather_icon_url')
                else current_data['icon']
            }
        }

        return weather_data

    except NotFoundError:
        # Если город не найден, возвращаем погоду Москвы
        return city_weather("Москва")

    except Exception as e:
        return {"error": f"Не удалось получить погоду: {str(e)}"}


# Пример использования
if __name__ == "__main__":
    weather = city_weather("xcfsd")  # Выведет погоду в Москве
    if 'error' in weather:
        print(weather['error'])
    else:
        print(f"Погода в {weather['city']}:")
        for period in ['current', 'morning', 'noon', 'evening', 'night']:
            print(f"\n{weather[period]['time']}:")
            print(f"Температура: {weather[period]['temp']}")
            print(f"Ощущается как: {weather[period]['feels_like']}")
            print(f"Ветер: {weather[period]['wind']}")
            print(f"Влажность: {weather[period]['humidity']}")
            print(f"Состояние: {weather[period]['status']}")
            print(f"Иконка: {weather[period]['icon']}")

            
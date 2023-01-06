import aiohttp
from database import get_token
import json
import asyncio
import time
import copy


api_key = get_token("OPEN_WEATHER")
coordinates_request = "http://api.openweathermap.org/geo/1.0/direct?q={}&appid={}"
weather_info_request = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&lang=ru"
weather_forecasting_request = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&lang=ru"


CURRENT_WEATHER_INFO = None
CURRENT_WEATHER_FORECAST = None


def from_kel_to_cel(kelvin):
    celsius = kelvin - 273.15
    return celsius


def from_hPa_to_mmHg(value_in_hPa):
    mmHg = value_in_hPa * 0.75
    return mmHg


def time_view(unix_time):
    struct_time = time.localtime(int(unix_time))
    days = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
            3: 'Четверг', 4:'Пятница', 5:'Суббота', 6:'Воскресенье'}
    view = 'Погода на {:0>2d}.{:0>2d}.{} {:0>2d}:{:0>2d}, {}'.format(struct_time.tm_mday, struct_time.tm_mon, struct_time.tm_year,
                                                    struct_time.tm_hour, struct_time.tm_min, days[int(struct_time.tm_wday)])
    return view


def datetime_selection(forecasts):
    current_day = None
    all_forecasts = []
    one_day_forecasts = []
    for forecast in forecasts:
        unix_time = forecast.get('dt')
        if current_day == time.localtime(unix_time).tm_mday:
            one_day_forecasts.append(forecast)
        else:
            current_day = time.localtime(unix_time).tm_mday
            if one_day_forecasts:
                all_forecasts.append(copy.copy(one_day_forecasts))
            one_day_forecasts = []
    
    result = [forecast[len(forecast)//2] for forecast in all_forecasts]
    return result


async def get_coordinates(city_name, api_key) -> tuple:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=coordinates_request.format(city_name, api_key)) as response:
            response = await response.text()
            result = json.loads(response)[0]
    return result['lat'], result['lon']


async def get_weather_info(city_name="Volgograd"):
    lat, lon = await get_coordinates(city_name, api_key)
    async with aiohttp.ClientSession() as session:
        async with session.get(weather_info_request.format(lat=lat, lon=lon, key=api_key)) as response:
            return await handle_weather_info(response)
            

async def get_weather_forecast(city_name="Volgograd"):
    lat, lon = await get_coordinates(city_name, api_key)
    async with aiohttp.ClientSession() as session:
        async with session.get(weather_forecasting_request.format(lat=lat, lon=lon, key=api_key)) as response:
            return await handle_weather_forecast(response)
            

async def response_to_dict(response):
    response_text = await response.text()
    return(json.loads(response_text))


def get_pressure(raw_data_main):
    types_of_pressures = ('pressure', 'sea_level', 'grnd_level')
    for pressure_type in types_of_pressures:
        if result := raw_data_main.get(pressure_type, False):
            return from_hPa_to_mmHg(result)
    else:
        return 'Нет данных'


async def handle_weather_info(response):
    raw_data = await response_to_dict(response)
    view = 'Погода сейчас\n'
    view += weather_info_view(extract_data(raw_data))
    view = format_endings(view)
    return view


async def handle_weather_forecast(response):
    raw_data = await response_to_dict(response)
    forecasts = datetime_selection(raw_data.get('list'))
    forecasts = [extract_data(weather) for weather in forecasts]
    view = ''
    for forecast in forecasts:
        view += time_view(forecast.get('dt')) + '\n'
        view += weather_info_view(forecast) + '\n'
        
    return format_endings(view, future=True)


def extract_data(weather_info):
    handled_info = {}
    handled_info['dt'] = weather_info.get('dt')
    if weather := weather_info.get('weather'):
        handled_info['weather'] = weather[0].get('description').capitalize()
    if main := weather_info.get('main'):
        for key, value in main.items():
            handled_info[key] = round(from_kel_to_cel(value), 1) if key in ('feels_like', 'temp') else None     
        handled_info['pressure'] = round(get_pressure(main), 1)
        handled_info['humidity'] = main.get('humidity')
        handled_info['visibility'] = weather_info.get('visibility')
    if wind := weather_info.get('wind'):
        handled_info['wind_speed'] = round(wind.get('speed'), 1) if wind.get('speed') is not None else None
        handled_info['wind_gust'] = round(wind.get('gust'), 1) if wind.get('gust') is not None else None
    if rain := weather_info.get('rain'):
        handled_info['rain_1h'] = rain.get('1h')
        handled_info['rain_3h'] = rain.get('3h')
    if snow := weather_info.get('snow'):
        handled_info['snow_1h'] = snow.get('1h')
        handled_info['snow_3h'] = snow.get('3h')
    handled_info = {key: value for  key, value in handled_info.items() if value is not None}
    return handled_info


def format_endings(view, future=False):
    view = view.replace('\n', '\n ')
    words = view.split(' ')
    words = [format_word(word, future=True) for word in words]
    return ''.join(map(lambda word: (word + ' ').replace('\n ', '\n'), words))


def format_word(word, future=False):
    if '!s' in word or '!f' in word:
        if future:
            word = word[0:word.find('!s')] + word[word.find('!f')+2:]
        else:
            word = word[0:word.find('!f')].replace('!s', '')
    return word


def weather_info_view(handled_info):
    view = ''
    characteristics = {
        'weather': '{}', 'temp': 'Температура {} °C',
        'feels_like': 'Ощущается как {} °C', 'pressure': 'Давление {} мм рт. ст.',
        'humidity': 'Влажность {}%', 'visibility': 'Видимость {} м',
        'wind_speed': 'Скорость ветра {} м/c', 'wind_gust': 'Максимальная скорость ветра {} м/c',
        'rain_1h': 'Выпа!sло!fдет {} мм дождя за 1 час', 'rain_3h': 'Выпа!sло!fдет {} мм дождя за 3 часа',
        'snow_1h': 'Выпа!sло!fдет {} мм снега за 1 час', 'snow_3h': 'Выпа!sло!fдет {} мм снега за 3 час'
    }
    for key, value in handled_info.items():
        if key in characteristics.keys():
            view += characteristics[key].format(value) + '\n'
    return view


async def update_weather_loop():
    global CURRENT_WEATHER_FORECAST
    global CURRENT_WEATHER_INFO
    while True:
        try:
            CURRENT_WEATHER_INFO = await get_weather_info()
            CURRENT_WEATHER_FORECAST = await get_weather_forecast()
            await asyncio.sleep(20 * 60)
        except Exception as exception:
            print(exception)
            continue


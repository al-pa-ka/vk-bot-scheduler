import aiohttp
from database import get_token
import json
import asyncio
import typing

api_key = get_token("OPEN_WEATHER")
coordinates_request = "http://api.openweathermap.org/geo/1.0/direct?q={}&appid={}"
weather_info_request = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&lang=ru"
weather_forecasting_request = "api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}"


def from_kel_to_cel(kelvin):
    celsius = kelvin - 273.15
    return celsius


def from_hPa_to_mmHg(value_in_hPa):
    mmHg = value_in_hPa * 0.75
    return mmHg


async def get_coordinates(city_name, api_key) -> tuple:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=coordinates_request.format(city_name, api_key)) as response:
            response = await response.text()
            result = json.loads(response)[0]
        print(result)
    return result['lat'], result['lon']


async def get_weather_info(city_name="Volgograd"):
    lat, lon = await get_coordinates(city_name, api_key)
    async with aiohttp.ClientSession() as session:
        async with session.get(weather_info_request.format(lat=lat, lon=lon, key=api_key)) as response:
            result = await handle_weather_info(response)
            print(result)
            return result


async def get_weather_forecast(city_name="Volgograd"):
    lat, lon = await get_coordinates(city_name, api_key)
    async with aiohttp.ClientSession() as session:
        async with session.get(weather_forecasting_request.format(lat=lat, lon=lon, key=api_key)) as response:
            response = await response.text()


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
    handled_info = {}
    if weather := raw_data.get('weather'):
        handled_info['weather'] = weather[0].get('description')
    if main := raw_data.get('main'):
        for key, value in main.items():
            handled_info[key] = round(from_kel_to_cel(value), 1) if key in ('feels_like', 'temp') else None     
        handled_info['pressure'] = round(get_pressure(main), 1)
        handled_info['humidity'] = main.get('humidity')
        handled_info['visibility'] = raw_data.get('visibility')
    if wind := raw_data.get('wind'):
        handled_info['wind_speed'] = wind.get('speed')
        handled_info['wind_gust'] = wind.get('gust')
    if rain := raw_data.get('rain'):
        handled_info['rain_1h'] = rain.get('1h')
        handled_info['rain_3h'] = rain.get('3h')
    if snow := raw_data.get('snow'):
        handled_info['snow_1h'] = snow.get('1h')
        handled_info['snow_3h'] = snow.get('3h')
    handled_info = {key: value for  key, value in handled_info.items() if value is not None}
    return weather_info_view(handled_info)

def weather_info_view(handled_info):
    view = ''
    characteristics = {
        'weather': 'Погода {}', 'temp': 'Температура {} °C',
        'feels_like': 'Ощущается как {} °C', 'pressure': 'Давление {} мм рт. ст.',
        'humidity': 'Влажность {}%', 'visibility': 'Видимость {} м',
        'wind_speed': 'Скорость ветра {} м/c', 'wind_gust': 'Максимальная скорость ветра {} м/c',
        'rain_1h': 'Выпало {} мм дождя за 1 час', 'rain_3h': 'Выпало {} мм дождя за 3 часа',
        'snow_1h': 'Выпало {} мм снега за 1 час', 'snow_3h': 'Выпало {} мм снега за 3 час'
    }
    for key, value in handled_info.items():
        if key in characteristics.keys():
            view += characteristics[key].format(value) + '\n'
    print(view)
    return view

async def main():
    await asyncio.gather(get_weather_info(), test())

async def test():
    while True:
        print('obeqw')
        await asyncio.sleep(10)

asyncio.run(main())
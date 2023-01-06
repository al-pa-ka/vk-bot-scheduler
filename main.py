# -*- coding: utf-8 -*-
import random
from vkbottle.bot import Bot
import asyncio
import aiohttp
from parser_1 import Parser
import io
from database import DataBase
from rules import Subscribe, Attachments, ManualMailing
from rules import ManualMailing, Weather, Forecast
from database import get_token, get_last_status
import logging
from open_weather import CURRENT_WEATHER_FORECAST, CURRENT_WEATHER_INFO
from open_weather import update_weather_loop, get_weather_forecast, get_weather_info
from qq_parser import QQParser

PUBLIC_ID = -213599387
PUBLIC_TOKEN = get_token('PUBLIC_TOKEN')
TEST_TOKEN = get_token('TEST_TOKEN')
bot = Bot(token=PUBLIC_TOKEN)
last_schedule = "https://www.energocollege.ru/vec_assistant/Расписание/{}-{}-20{}.jpg".format(*get_last_status())
parser = Parser("https://www.energocollege.ru", "/schedule/", last_schedule)
db = DataBase()
logging.getLogger("vkbottle").setLevel(logging.INFO)

@bot.labeler.message(text="Привет")
async def hi_handle(message):
    await message.answer("Ну привет! Как дела?")


@bot.labeler.message(Subscribe())
async def add_user(message):
    if not await db.is_user_subscribed(message.from_id):
        await db.add_user(message.from_id)
        await message.answer("Вы успешно подписаны")
        attachment = await create_attachment(message.from_id, parser.schedule)
        await bot.api.messages.send(peer_id=message.from_id, random_id=random.getrandbits(64),
                                    attachment=attachment)
    else:
        await message.answer("Вы уже подписаны")


@bot.labeler.message(Attachments(), blocking=False)
async def attachments(message, attachment_types):
    if attachment_types.get('photo'):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment_types.get('photo')) as response:  
                    result = await QQParser.convert_image(await response.read())
            attachment = await create_attachment(message.from_id, result)
            await message.answer(attachment=attachment)
        except Exception as exception:
            await message.answer(message = ("Ой-ой кажется произошла ошибка\n" + str(exception)))


@bot.labeler.message(ManualMailing())
async def manual_mailing(message, handled=None):
    users = await db.get_all_users()
    try:
        await asyncio.gather(*[asyncio.create_task(send_message(handled, *user_id)) for user_id in users])
    except Exception as exception:
        print(exception)


@bot.labeler.message(Weather())
async def weather_info(message):
    global CURRENT_WEATHER_INFO
    if CURRENT_WEATHER_INFO:
        await message.answer(CURRENT_WEATHER_INFO)
    else:
        CURRENT_WEATHER_INFO = await get_weather_info()
        await message.answer(CURRENT_WEATHER_INFO)


@bot.labeler.message(Forecast())
async def weather_forecast(message):
    global CURRENT_WEATHER_FORECAST
    if CURRENT_WEATHER_FORECAST:
        await message.answer(CURRENT_WEATHER_FORECAST)
    else:
        CURRENT_WEATHER_FORECAST = await get_weather_forecast()
        await message.answer(CURRENT_WEATHER_FORECAST)


async def create_attachment(peer_id, attachment: bytes):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.vk.com/method/photos.getMessagesUploadServer?peer_id={peer_id}"
                                f"&access_token={PUBLIC_TOKEN}&v={5.131}", data={}) as response:
            response = await response.json()
            print(response)
            url = response['response']['upload_url']

            data = aiohttp.FormData()
            data.add_field('photo', io.BytesIO(attachment), filename='file.jpg')

            async with session.post(url, data=data) as response:
                response = await response.json(content_type='text/html')
        async with session.post(f"https://api.vk.com/method/photos.saveMessagesPhoto?photo={response['photo']}"
                                f"&server={response['server']}&hash={response['hash']}"
                                f"&access_token={PUBLIC_TOKEN}&v={5.131}") as response:
            response = await response.json()
            return 'photo{}_{}'.format(response['response'][0]['owner_id'], response['response'][0]['id'])


async def send_schedule(user_id):
    try:
        attachment = await create_attachment(int(user_id), parser.schedule)
        await bot.api.messages.send(attachment=attachment, peer_id=int(user_id),
                                    random_id=random.getrandbits(64))
    except Exception as exception:
        print(exception)


async def send_message(message, user_id):
    try:
        await bot.api.messages.send(message=message, peer_id=int(user_id), random_id=random.getrandbits(64))
    except Exception as exception:
        print(exception)


async def send_out():
    users = await db.get_all_users()
    if not users:
        return
    await asyncio.gather(*[asyncio.create_task(send_schedule(*user_id)) for user_id in users])


async def main():
    await asyncio.gather(parser.parser_loop(send_out), bot.run_polling(), 
                            update_weather_loop())

try:
    asyncio.run(main())
except Exception as error:
    print(error, file=open('logs.txt', 'w'))

# -*- coding: utf-8 -*-
import random
from vkbottle.bot import Bot
import asyncio
import aiohttp
from parser import Parser
import io
from database import DataBase
from rules import Subscribe, Attachments
from database import get_token, get_last_status

PUBLIC_ID = -213599387
PUBLIC_TOKEN = get_token('PUBLIC_TOKEN')
TEST_TOKEN = get_token('TEST_TOKEN')
bot = Bot(token=PUBLIC_TOKEN)
last_schedule = "https://www.energocollege.ru/vec_assistant/Расписание/{}-{}-20{}.jpg".format(*get_last_status())
parser = Parser("https://www.energocollege.ru", "/schedule/", last_schedule)
db = DataBase()


@bot.labeler.message(text="Привет")
async def hi_handle(message):
    await message.answer("Ну привет! Как дела?")


@bot.labeler.message(Subscribe())
async def add_user(message):
    if not await db.is_user_subscribed(message.from_id):
        await db.add_user(message.from_id)
        await message.answer("Вы успешно подписаны")
    else:
        await message.answer("Вы уже подписаны")


@bot.labeler.message(Attachments())
async def attachments(message, attachment_types):
    if attachment_types['photo']:
        await message.answer('Как красиво!')


async def create_attachment(peer_id, schedule):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.vk.com/method/photos.getMessagesUploadServer?peer_id={peer_id}"
                                f"&access_token={PUBLIC_TOKEN}&v={5.131}", data={}) as response:
            response = await response.json()
            print(response)
            url = response['response']['upload_url']

            data = aiohttp.FormData()
            data.add_field('photo', io.BytesIO(schedule), filename='fiek.jpg')

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


async def send_out():
    users = await db.get_all_users()
    if not users:
        return
    await asyncio.gather(*[asyncio.create_task(send_schedule(*user_id)) for user_id in users])


async def main():
    task1 = asyncio.create_task(parser.parse(send_out))
    task2 = asyncio.create_task(bot.run_polling())
    await task1
    await task2

try:
    asyncio.run(main())
except Exception as error:
    print(error, file=open('logs.txt', 'w'))

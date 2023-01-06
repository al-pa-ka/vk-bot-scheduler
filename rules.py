from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message, MessageEvent
import typing


class Subscribe(ABCRule[Message]):
    async def check(self, event) -> bool:
        if event.text.lower() in ['начать', 'подписаться']:
            return True
        return False


class Unsubscribe(ABCRule[Message]):
    async def check(self, event) -> bool:
        if event.text.lower() == 'отписаться':
            return True
        return False


class ManualMailing(ABCRule[Message]):
    async def check(self, event) -> typing.Union[str, bool]:
        if '!command -mm' in event.text:
            message = event.text.replace('!command -mm', '')
            return {'handled': message.strip()}
        return False


class Attachments(ABCRule[Message]):
    async def check(self, event) -> dict:
        result = {'photo': False, 'audio': False}
        if event.get_photo_attachments():
            photos = event.get_photo_attachments()[0]
            photo = photos.sizes[-1]
            result['photo'] = photo.url
        if event.get_audio_attachments():
            result['audio'] = True

        return {'attachment_types': result}


class Weather(ABCRule[Message]):
    async def check(self, event):
        if 'погода' == event.text.lower():
            return True
        return False


class Forecast(ABCRule[Message]):
    async def check(self, event):
        if 'прогноз' == event.text.lower():
            return True
        return False
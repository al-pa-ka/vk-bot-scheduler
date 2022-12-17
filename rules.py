from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message
import typing


class Subscribe(ABCRule[Message]):
    async def check(self, event) -> bool:
        if event.text.lower() in ['начать', 'подписаться']:
            return True
        return False


class Unsubscribe(ABCRule[Message]):
    async def check(self, event):
        if event.text.lower() == 'отписаться':
            return True
        return False


class Attachments(ABCRule[Message]):
    async def check(self, event) -> dict:
        result = {'photo': False, 'audio': False}
        if event.get_photo_attachments():
            print(event.get_photo_attachments())
            result['photo'] = True
        if event.get_audio_attachments():
            result['audio'] = True

        return {'attachment_types': result}

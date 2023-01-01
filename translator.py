import asyncio
import aiohttp
import json


async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://mc.yandex.ru/watch/28584306?wmode=7&page-url=https://translate.yandex.ru/&page-ref=https://www.google.com/&charset=utf-8&site-info={"ui":"ru","domain":"ru","loggedIn":false,"view":"none","isFirstVisit":false,"firstVisitSrc":"www.google.com","deviceType":"desktop","expId":[],"browserPrefersDarkMode":true,"darkThemeEnabled":true,"serverSideTranslation":false,"seoDumpUsed":false}&ut=noindex&browser-info=pv:1:vf:75h6wcsjl31tvi5xjf8ir:fp:727:fu:0:en:utf-8:la:en-US:v:943:cn:1:dp:0:ls:269106810077:hid:597900102:z:180:i:20230101205523:et:1672595724:c:1:rn:638262800:rqn:60:u:1672590818954166785:w:1920x442:s:1920x1080x24:sk:1:ds:48,69,82,75,10,0,,398,6,,,,724:co:0:cpf:1:eu:0:ns:1672595722716:adb:1:pu:38007005711672590818954166785:zzlc:na:fip:398de729c07854e5d32589aba83e67c7-0ed8ce9e1e39cec802dafc59181dfc61-a81f3b9bcdd80a361c14af38dc09b309-4bd84c89c35a312599d807af285e7b5f-44a27f30e430c516676c87ba3434d8dd-eb7a2140f79c40abe099ef1fddc804ba-61b9878bbce18de73aafc8582a198c0c-db3ca58f6de6311381776d95eb4ae9c7-a81f3b9bcdd80a361c14af38dc09b309-c6d7b47b2dcff33f80cab17f3a360d0b-7f352510bde719c9d71416ba567ebe6d:rqnl:1:st:1672595724:t:Словарь и онлайн перевод на английский, русский, немецкий, французский, украинский и другие языки - Яндекс Переводчик.&t=gdpr(3-0)clc(0-0-0)rqnt(1)aw(1)fip(1)ti(2)') as response:
            print(await response.text())
            print(response.cookies)
        '''async with session.post('https://translate.yandex.ru/?source_lang=en&target_lang=ru&text=hello', 
                                json={'text': 'hello', 'lang': 'en', 'options': '516'}) as response:
            print(await response.text())'''


asyncio.run(test())

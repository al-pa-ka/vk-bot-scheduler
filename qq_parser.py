import uuid
import pydantic
from typing import Any
import hashlib
import asyncio
import aiohttp
import base64
import json

class RequestBody(pydantic.BaseModel):

    busiId: str = 'ai_painting_anime_entry' #"different_dimension_me_img_entry"

    class Extra(pydantic.BaseModel):
        face_rects: list = []
        version: int = 2
        language: str = "en"
        platform: str = "web"
        
        class DataReport(pydantic.BaseModel):
            parent_trace_id: str = pydantic.Field(default_factory= lambda:str(uuid.uuid4()))
            root_channel: str = ''
            level: int = 0

        data_report: str = pydantic.Field(default_factory=lambda:RequestBody.Extra.DataReport().dict())
    
    extra: str = pydantic.Field(default_factory=lambda:RequestBody.Extra().json())
    images: list[str] = []

        
    def set_images(self, images: list):
        self.images = images


class QQParser():

    DEFAULT_USER_AGENT ={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'}
    AI_PROCESSOR_URL = "https://ai.tu.qq.com/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process"


    @staticmethod
    def to_base64(image: bytes):
        file = open('test.jpg', 'wb')
        file.write(image)
        return base64.b64encode(image).decode()

    @staticmethod
    def get_sign_values(request_body: RequestBody):
        body = request_body.json()
        value = 'https://h5.tu.qq.com' + \
                str(len(body)) + \
                'HQ31X02e'
        value = hashlib.md5(value.encode()).hexdigest()
        return {
            "x-sign-value": value,
            "x-sign-version": "v1",
            "Origin": "https://h5.tu.qq.com",
            "Referer": "https://h5.tu.qq.com/",
        }

    @staticmethod
    async def request(image: bytes):
        body = RequestBody()
        body.set_images([QQParser.to_base64(image)])
        headers = QQParser.get_sign_values(body) | QQParser.DEFAULT_USER_AGENT
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.post(url=QQParser.AI_PROCESSOR_URL, 
            headers=headers, json=body.dict(exclude_none=True), proxy='http://101.32.184.53:3128') as response:
                if "extra" in await response.text():
                    return json.loads(json.loads(await response.text()).get('extra')).get('img_urls')
                else:
                    description = (await response.json()).get('msg')
                    if isinstance(description, (bytes, bytearray)):
                        description = description.decode()
                    description = description.replace('b\'', '')
                    description = description.replace('\'', '')
                    raise Exception(description)
            
    @staticmethod
    async def convert_image(image: bytes) -> bytes:
        urls = await QQParser.request(image)
        if urls:
            try:
                url =  urls[2]
            except Exception:
                url = urls[0]
        else:
            return 
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.read()
                return result


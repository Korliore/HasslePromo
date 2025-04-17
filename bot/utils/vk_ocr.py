import aiohttp
import json
import os
import cv2
import numpy as np
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from mimetypes import guess_type
from typing import Tuple, List, Optional
from bot.config import VK_CLOUD_TOKEN, VK_CLOUD_HOST

# Инициализация логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[OCR]")


class APIError(Exception):
    """Базовое исключение для ошибок API"""
    pass


class RecognitionError(APIError):
    """Ошибка распознавания"""
    pass


class VKService:
    def __init__(self):
        self.host = VK_CLOUD_HOST
        self.token = VK_CLOUD_TOKEN
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def recognize_text(self,
                             image: bytes,
                             filename: str = 'file',
                             mode: Optional[str] = None) -> str:
        """
        Распознает текст на изображении через VK API

        :param image: Байты изображения
        :param filename: Имя файла для определения MIME-типа
        :param mode: Режим распознавания
        :return: Распознанный текст
        """
        url = f"{self.host}/api/v1/text/recognize"
        params = {
            'oauth_token': self.token,
            'oauth_provider': 'mcs'
        }

        content_type, _ = guess_type(filename)
        if not content_type or not content_type.startswith('image/'):
            content_type = 'image/jpeg'

        meta = {'images': [{'name': filename}]}
        if mode:
            meta['mode'] = mode

        form_data = aiohttp.FormData()
        form_data.add_field(
            name='image',  # Проверьте имя поля согласно документации API
            value=image,
            filename=filename,
            content_type=content_type
        )
        form_data.add_field(
            'meta',
            json.dumps(meta),
            content_type='application/json'
        )

        try:
            async with self.session.post(url, params=params, data=form_data) as response:
                if response.status != 200:
                    error_msg = f"HTTP Error {response.status}"
                    try:
                        error_body = await response.json()
                        error_msg += f": {error_body.get('body', 'Unknown error')}"
                    except json.JSONDecodeError:
                        error_msg += f": {await response.text()}"
                    raise APIError(error_msg)

                response_data = await response.json()
                body = response_data.get('body', {})

                if isinstance(body, str):
                    raise RecognitionError(f"API returned string body: {body}")

                if not isinstance(body, dict) or not body.get('objects'):
                    raise RecognitionError("Invalid response structure")

                obj = body['objects'][0]
                if obj.get('status') != 0:
                    raise RecognitionError(obj.get('error', 'Unknown recognition error'))

                return obj.get('text', '')

        except aiohttp.ClientError as e:
            raise APIError(f"Connection error: {str(e)}")




# Инициализация сервисов
vk_service_ocr = VKService()
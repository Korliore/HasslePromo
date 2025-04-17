import aiohttp
import json
import logging
from mimetypes import guess_type
from typing import Optional
from bot.config import VK_CLOUD_TOKEN, VK_CLOUD_HOST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[OCR]")

class APIError(Exception):
    pass

class RecognitionError(APIError):
    pass

class VKService:
    def __init__(self, session: aiohttp.ClientSession, host: str, token: str):
        self.session = session
        self.host = host
        self.token = token

    @classmethod
    async def create(cls):
        session = aiohttp.ClientSession()
        return cls(session, VK_CLOUD_HOST, VK_CLOUD_TOKEN)

    async def close(self):
        await self.session.close()

    async def recognize_text(
        self,
        image: bytes,
        filename: str = "file",
        mode: Optional[str] = None
    ) -> str:
        url = f"{self.host}/api/v1/text/recognize"
        params = {
            "oauth_token": self.token,
            "oauth_provider": "mcs"
        }

        content_type, _ = guess_type(filename)
        if not content_type or not content_type.startswith("image/"):
            content_type = "image/jpeg"

        # Meta с именем, совпадающим с полем формы
        meta = {"images": [{"name": filename}]}
        if mode:
            meta["mode"] = mode

        form_data = aiohttp.FormData()
        form_data.add_field(
            name=filename,
            value=image,
            filename=filename,
            content_type=content_type
        )
        form_data.add_field(
            name="meta",
            value=json.dumps(meta),
            content_type="application/json"
        )

        try:
            async with self.session.post(url, params=params, data=form_data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise APIError(f"HTTP {resp.status}: {text}")

                data = await resp.json()
                body = data.get("body", {})
                if isinstance(body, str):
                    raise RecognitionError(f"API returned string body: {body}")
                objs = body.get("objects") or []
                if not objs:
                    raise RecognitionError("No objects in response")
                obj = objs[0]
                if obj.get("status") != 0:
                    raise RecognitionError(obj.get("error", "Unknown error"))
                return obj.get("text", "")
        except aiohttp.ClientError as e:
            raise APIError(f"Connection error: {e}")

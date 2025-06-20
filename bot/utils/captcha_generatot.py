from captcha.image import ImageCaptcha
import random, string

async def gen_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = ImageCaptcha(width=280, height=90)
    data = image.generate(captcha_text)
    path = f"/tmp/captcha_{captcha_text}.png"
    image.write(captcha_text, path)
    return captcha_text, path
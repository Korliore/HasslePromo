import os

os.environ["OMP_NUM_THREADS"] = "1"
import easyocr
import cv2
import numpy as np
import logging

# Инициализация логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[OCR]")

try:
    logger.info(f"EASYOCR_CACHE_DIR: {os.environ.get('EASYOCR_CACHE_DIR')}")
    reader = easyocr.Reader(['ru'], gpu=False)
    logger.info("EasyOCR reader initialized")
except Exception as e:
    logger.error(f"Ошибка инициализации: {e}")
    raise


def has_color(img, target_color, tolerance=40, scale_factor=0.25):
    """Проверка цвета на уменьшенном изображении"""
    try:
        h, w = img.shape[:2]
        img_small = cv2.resize(img, (int(w * scale_factor), int(h * scale_factor)))
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        lower = np.array([max(0, c - tolerance) for c in target_color], dtype=np.uint8)
        upper = np.array([min(255, c + tolerance) for c in target_color], dtype=np.uint8)

        mask = cv2.inRange(img_rgb, lower, upper)
        return cv2.countNonZero(mask) > 0
    except Exception as e:
        logger.error(f"Ошибка проверки цвета: {e}")
        return False


def extract_text(img):
    """Распознавание текста с глобальным ридером"""
    try:
        result = reader.readtext(img, detail=0, paragraph=True, text_threshold=0.7)
        return [t for t in result if t.strip()]
    except Exception as e:
        logger.error(f"Ошибка распознавания: {e}")
        return []


def analyze_screenshot_sync(file_bytes, texts, color=None):
    """Основная логика обработки"""
    try:
        # Декодирование изображения
        img = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            logger.error("Ошибка декодирования изображения")
            return False

        # Приоритетная проверка цвета
        if color and has_color(img, color):
            logger.info("Обнаружен целевой цвет")
            return True

        # Оптимизированная проверка текста
        recognized = ' '.join(extract_text(img)).lower().replace(' ', '')
        targets = [t.lower().replace(' ', '') for t in texts]

        return any(t in recognized for t in targets)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return False


# Асинхронная обертка
from concurrent.futures import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=1)


async def analyze_screenshot(file_bytes, texts, color=None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor,
        analyze_screenshot_sync,
        file_bytes,
        texts,
        color
    )
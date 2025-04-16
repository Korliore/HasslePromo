import os
os.environ["OMP_NUM_THREADS"] = "1"
import easyocr
import cv2
import numpy as np
import tempfile


try:
    print(f"[OCR] EASYOCR_CACHE_DIR: {os.environ.get('EASYOCR_CACHE_DIR')}")
    reader = easyocr.Reader(['ru'], gpu=False)
    print("[OCR] EasyOCR reader initialized with language: ru")
except Exception as e:
    print(f"[OCR] Ошибка инициализации EasyOCR: {e}")
    raise

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    
    # Увеличение резкости
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(img, -1, kernel)
    
    # Увеличение контраста через CLAHE
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    limg = cv2.merge((clahe.apply(l), a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # Адаптивная бинаризация с оптимизированными параметрами
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY, 25, 12)
    
    # Морфологическая операция для соединения символов
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,1))
    processed = cv2.morphologyEx(adapt, cv2.MORPH_CLOSE, kernel)
    
    processed_path = image_path.replace('.png', '_proc.png')
    cv2.imwrite(processed_path, processed)
    return processed_path

def preprocess_adaptive(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    adapt_path = image_path.replace('.png', '_adapt.png')
    cv2.imwrite(adapt_path, adapt)
    return adapt_path

def extract_text(image_path):
    import easyocr
    try:
        print(f"[OCR] EasyOCR reader initializing inside extract_text for: {image_path}", flush=True)
        reader = easyocr.Reader(['ru'], gpu=False)
        print(f"[OCR] EasyOCR reader created", flush=True)
        result = reader.readtext(image_path, detail=0, paragraph=True)
        print(f"[OCR] EasyOCR readtext result: {result}", flush=True)
        return result
    except Exception as e:
        import traceback
        print(f"[OCR][ERROR] Ошибка EasyOCR в extract_text: {e}", flush=True)
        traceback.print_exc()
        return []

def count_matches_ignore_spaces(text, required_texts):
    text_flat = text.replace(' ', '').lower()
    count = 0
    for req in required_texts:
        req_flat = req.replace(' ', '').lower()
        if req_flat in text_flat:
            count += 1
    return count

def has_color(image_path, rgb_color, tolerance=30):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lower = np.array([c - tolerance for c in rgb_color])
    upper = np.array([c + tolerance for c in rgb_color])
    mask = cv2.inRange(img_rgb, lower, upper)
    return np.any(mask)

def count_matches(text, required_texts):
    text_l = text.lower()
    return sum(1 for req in required_texts if req.lower() in text_l)


from concurrent.futures import ThreadPoolExecutor
import asyncio

_executor = ThreadPoolExecutor()

def analyze_screenshot_sync(file_bytes, required_texts, required_color=None):
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(file_bytes)
    tmp_path = tmp.name
    tmp.close()

    import shutil
    import re
    # Сохраняем изображение для отладки
    debug_img_path = tmp_path.replace('.png', '_ocrdebug.png')
    shutil.copy(tmp_path, debug_img_path)
    print(f"[OCR] Saved debug image: {debug_img_path}", flush=True)

    import traceback
    print(f"[OCR] Начало работы OCR для файла: {tmp_path}", flush=True)
    try:
        text_list = extract_text(tmp_path)
        print(f"[OCR] Text list: {text_list}", flush=True)
        joined_text = ''.join([t.replace(' ', '').lower() for t in text_list if isinstance(t, str)])
        print(f"[OCR] Joined text: {joined_text}", flush=True)
        # Логируем если результат пустой или нет кириллицы
        if not joined_text:
            print("[OCR][WARNING] Пустой результат OCR!", flush=True)
        elif not re.search(r'[а-яё]', joined_text):
            print(f"[OCR][WARNING] В результате OCR нет кириллических символов! text={joined_text}", flush=True)
        found_any = False
        for req in required_texts:
            req_flat = req.replace(' ', '').lower()
            if req_flat in joined_text:
                found_any = True
                print(f"[OCR] Найдено совпадение: {req_flat}", flush=True)
        text_found = found_any

        # Сначала ищем цвет
        if required_color:
            color_found = has_color(tmp_path, required_color)
            print(f"[OCR] Проверка цвета: color_found={color_found}", flush=True)
            if color_found:
                print(f"[OCR] Цвет найден, текст не проверяем. Возвращаем True.", flush=True)
                return True
            else:
                print(f"[OCR] Цвет не найден, переходим к проверке текста.", flush=True)
        # Если цвет не найден — ищем текст
        found_any = False
        for req in required_texts:
            req_flat = req.replace(' ', '').lower()
            if req_flat in joined_text:
                found_any = True
                print(f"[OCR] Найдено совпадение: {req_flat}", flush=True)
        text_found = found_any
        print(f"[OCR] Конец работы OCR. text_found={text_found}", flush=True)
        return text_found
    except Exception as e:
        print(f"[OCR][ERROR] Ошибка при распознавании: {e}", flush=True)
        traceback.print_exc()
        return False

async def analyze_screenshot(file_bytes, required_texts, required_color=None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _executor,
        analyze_screenshot_sync,
        file_bytes,
        required_texts,
        required_color
    )
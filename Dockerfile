FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 tesseract-ocr tesseract-ocr-rus fonts-dejavu fonts-dejavu-core fonts-dejavu-extra && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  --extra-index-url https://download.pytorch.org/whl/cu111

# Кэшировать модели EasyOCR
ENV EASYOCR_CACHE_DIR=/root/.cache/easyocr
RUN python -c "import easyocr; easyocr.Reader(['ru'], gpu=False)"

COPY . .

CMD ["python", "-m", "bot.main"]
FROM python:3.8

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN apt update
RUN apt install -y tesseract-ocr ffmpeg libsm6 libxext6

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt

COPY . .

CMD python -u /app/server.py
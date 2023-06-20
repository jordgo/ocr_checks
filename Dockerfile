FROM python:3.8

WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt update
RUN apt install tesseract-ocr -y

COPY . .

CMD python -u /app/server.py
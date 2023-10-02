FROM python:3.10

WORKDIR /arseneWenger
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]

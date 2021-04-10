FROM python:3.8.9-slim

RUN \
    pip install discord pymysql requests pydub

COPY . /opt/ColdOneBot
CMD ["python", "/opt/ColdOneBot/application.py"]
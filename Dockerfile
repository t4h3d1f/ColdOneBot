FROM python:3.9.7

COPY . /opt/ColdOneBot
RUN \
    pip install discord discordutils[voice] requests pydub discord-py-interactions \
    && apt update \
    && apt install -y opus-tools ffmpeg \
    && apt clean


CMD ["python", "/opt/ColdOneBot/application.py"]

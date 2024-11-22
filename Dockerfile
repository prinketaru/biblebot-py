FROM python:3
FROM bot.py

RUN mkdir -p /usr/bot/src
WORKDIR /usr/bot/src

COPY . .

CMD [ "python3", "bot.py" ]

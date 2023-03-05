FROM python:3.10-alpine AS build

ENV POETRY_VERSION 1.3.1

RUN apk add build-base python3-dev linux-headers pcre-dev jpeg-dev zlib-dev pcre-dev

RUN pip install --upgrade pip

RUN pip install yt-dlp pillow

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /twitfix

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes | pip install -r /dev/stdin

WORKDIR /twitfix

COPY . .

EXPOSE 9000

ENTRYPOINT [ "gunicorn", "--config", "gunicorn.conf.py", "--bind", "0.0.0.0:9000" ]

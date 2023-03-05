FROM python:3.6-alpine AS build

RUN apk add build-base python3-dev linux-headers pcre-dev jpeg-dev zlib-dev

RUN pip install --upgrade pip

RUN pip install yt-dlp pillow uwsgi

FROM python:3.6-alpine AS deps

WORKDIR /twitfix

COPY requirements.txt requirements.txt
COPY --from=build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

RUN pip install -r requirements.txt

FROM python:3.6-alpine AS runner

EXPOSE 9000

RUN apk add pcre-dev jpeg-dev zlib-dev

WORKDIR /twitfix

CMD ["uwsgi", "twitfix.ini"]

COPY --from=build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=deps /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY . .

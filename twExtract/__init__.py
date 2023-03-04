import json
import re

import requests
import yt_dlp
from yt_dlp.extractor import twitter

from . import twExtractError

guestToken = None
pathregex = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"


def getGuestToken():
    global guestToken
    if guestToken is None:
        r = requests.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={
                "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
            },
        )
        guestToken = json.loads(r.text)["guest_token"]
    return guestToken


def extractStatus_fallback(url):
    twIE = twitter.TwitterIE()
    twIE.set_downloader(yt_dlp.YoutubeDL())
    twid = twIE._match_id(url)
    status = twIE._call_api(
        "statuses/show/%s.json" % twid,
        twid,
        {
            "cards_platform": "Web-12",
            "include_cards": 1,
            "include_reply_count": 1,
            "include_user_entities": 0,
            "tweet_mode": "extended",
        },
    )
    return status


def extractStatus(url):
    try:
        # get tweet ID
        m = re.search(pathregex, url)
        if m is None:
            return extractStatus_fallback(url)
        twid = m.group(2)
        # get guest token
        guestToken = getGuestToken()
        # get tweet
        tweet = requests.get(
            "https://api.twitter.com/1.1/statuses/show/"
            + twid
            + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0",
            headers={
                "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw",
                "x-guest-token": guestToken,
            },
        )
        output = tweet.json()
        if "errors" in output:
            # pick the first error and create a twExtractError
            error = output["errors"][0]
            raise twExtractError.TwExtractError(error["code"], error["message"])
        return output
    except Exception as e:
        return extractStatus_fallback(url)


def lambda_handler(event, context):
    if "queryStringParameters" not in event:
        return {"statusCode": 400, "body": "Invalid request."}
    url = event["queryStringParameters"].get("url", "")
    return {"statusCode": 200, "body": extractStatus(url)}

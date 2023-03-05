import re
from urllib import parse

import yt_dlp
from aiohttp import ClientSession
from aiohttp.http_exceptions import HttpProcessingError
from yt_dlp.extractor import twitter

from twExtract import twExtractError

PATH_REGEX = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"

GUEST_BEARER = "AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"

TWITTER_API_URL = parse.urlparse("https://api.twitter.com/1.1")


async def get_guest_token():
    url = TWITTER_API_URL._replace(path=f"{TWITTER_API_URL.path}/guest/activate.json")
    async with ClientSession() as session:
        async with session.post(
            url.geturl(), headers={"Authorization": f"Bearer {GUEST_BEARER}"}
        ) as r:
            if r.ok:
                data = await r.json()
                return data["guest_token"]
            raise HttpProcessingError(code=r.status, message=await r.text())


def extract_status_fallback(url):
    tw_ie = twitter.TwitterIE()
    tw_ie.set_downloader(yt_dlp.YoutubeDL())
    twid = tw_ie._match_id(url)
    status = tw_ie._call_api(
        f"statuses/show/{twid}.json",
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


async def extract_status(url):
    try:
        # get tweet ID
        m = re.search(PATH_REGEX, url)
        if m is None:
            return extract_status_fallback(url)
        twid = m.group(2)
        guest_token = await get_guest_token()
        url = TWITTER_API_URL._replace(
            path=f"{TWITTER_API_URL.path}/statuses/show/{twid}.json",
            query=parse.urlencode(
                dict(
                    tweet_mode="extended",
                    cards_platform="Web-12",
                    include_cards=1,
                    include_reply_count=1,
                    include_user_entities=0,
                )
            ),
        )
        async with ClientSession() as session:
            async with session.get(
                url.geturl(),
                headers={
                    "Authorization": f"Bearer {GUEST_BEARER}",
                    "x-guest-token": guest_token,
                },
            ) as tweet:
                output = await tweet.json()
                if "errors" in output:
                    # pick the first error and create a twExtractError
                    error = output["errors"][0]
                    raise twExtractError.TwExtractError(error["code"], error["message"])
                return output
    except Exception:
        return extract_status_fallback(url)

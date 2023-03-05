import os

os.environ["RUNNING_TESTS"] = "1"

import cache
from quart.testing import QuartClient

import twExtract
from twitfix import constants, utils
from twitfix.app import app

client = QuartClient(app)

testTextTweet = "https://twitter.com/jack/status/20"
testVideoTweet = "https://twitter.com/Twitter/status/1263145271946551300"
testMediaTweet = "https://twitter.com/Twitter/status/1118295916874739714"
testMultiMediaTweet = "https://twitter.com/Twitter/status/1293239745695211520"
testPollTweet = "https://twitter.com/norm/status/651169346518056960"
testQRTTweet = "https://twitter.com/Twitter/status/1232823570046255104"
testQrtCeptionTweet = "https://twitter.com/CatherineShu/status/585253766271672320"
testQrtVideoTweet = "https://twitter.com/Twitter/status/1494436688554344449"

textVNF_compare = {
    "tweet": "https://twitter.com/jack/status/20",
    "url": "",
    "description": "just setting up my twttr",
    "screen_name": "jack",
    "type": "Text",
    "images": ["", "", "", "", ""],
    "time": "Tue Mar 21 20:50:14 +0000 2006",
    "qrtURL": None,
    "nsfw": False,
}
videoVNF_compare = {
    "tweet": "https://twitter.com/Twitter/status/1263145271946551300",
    "url": "https://video.twimg.com/amplify_video/1263145212760805376/vid/1280x720/9jous8HM0_duxL0w.mp4?tag=13",
    "description": "Testing, testing...\n\nA new way to have a convo with exactly who you want. We’re starting with a small % globally, so keep your 👀 out to see it in action. https://t.co/pV53mvjAVT",
    "thumbnail": "http://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg",
    "screen_name": "Twitter",
    "type": "Video",
    "images": ["", "", "", "", ""],
    "time": "Wed May 20 16:31:15 +0000 2020",
    "qrtURL": None,
    "nsfw": False,
    "verified": True,
    "size": {"width": 1920, "height": 1080},
}
testMedia_compare = {
    "tweet": "https://twitter.com/Twitter/status/1118295916874739714",
    "url": "",
    "description": "On profile pages, we used to only show someone’s replies, not the original Tweet 🙄 Now we’re showing both so you can follow the conversation more easily! https://t.co/LSBEZYFqmY",
    "thumbnail": "https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg",
    "screen_name": "Twitter",
    "type": "Image",
    "images": ["https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg", "", "", "", "1"],
    "time": "Tue Apr 16 23:31:38 +0000 2019",
    "qrtURL": None,
    "nsfw": False,
    "size": {},
}
testMultiMedia_compare = {
    "tweet": "https://twitter.com/Twitter/status/1293239745695211520",
    "url": "",
    "description": "We tested, you Tweeted, and now we’re rolling it out to everyone! https://t.co/w6Q3Q6DiKz",
    "thumbnail": "https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg",
    "screen_name": "Twitter",
    "type": "Image",
    "images": [
        "https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg",
        "https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg",
        "",
        "",
        "2",
    ],
    "time": "Tue Aug 11 17:35:57 +0000 2020",
    "qrtURL": None,
    "nsfw": False,
    "verified": True,
    "size": {},
}

testPoll_comparePoll = {
    "name": "poll2choice_text_only",
    "binding_values": {
        "choice1_label": {"type": "STRING", "string_value": "Mean one thing"},
        "choice2_label": {"type": "STRING", "string_value": "Mean multiple things"},
        "end_datetime_utc": {"type": "STRING", "string_value": "2015-10-06T22:57:24Z"},
        "counts_are_final": {"type": "BOOLEAN", "boolean_value": True},
        "choice2_count": {"type": "STRING", "string_value": "33554"},
        "choice1_count": {"type": "STRING", "string_value": "124875"},
        "last_updated_datetime_utc": {
            "type": "STRING",
            "string_value": "2015-10-06T22:57:31Z",
        },
        "duration_minutes": {"type": "STRING", "string_value": "1440"},
    },
}
testPoll_comparePollVNF = {
    "total_votes": 158429,
    "choices": [
        {"text": "Mean one thing", "votes": 124875, "percent": 78.8},
        {"text": "Mean multiple things", "votes": 33554, "percent": 21.2},
    ],
}


def compare_dict(original, compare):
    for key in original:
        assert key in compare
        if type(compare[key]) is not dict:
            assert compare[key] == original[key]
        else:
            compare_dict(original[key], compare[key])


# Tweet retrieve tests


def test_text_tweet_extract():
    tweet = twExtract.extractStatus(testTextTweet)
    assert tweet["full_text"] == textVNF_compare["description"]
    assert tweet["user"]["screen_name"] == "jack"
    assert "extended_entities" not in tweet
    assert tweet["is_quote_status"] == False


def test_video_tweet_extract():
    tweet = twExtract.extractStatus(testVideoTweet)
    assert tweet["full_text"] == videoVNF_compare["description"]
    assert tweet["user"]["screen_name"] == "Twitter"
    assert "extended_entities" in tweet
    assert len(tweet["extended_entities"]["media"]) == 1
    video = tweet["extended_entities"]["media"][0]
    assert video["media_url_https"] == "https://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg"
    assert video["type"] == "video"
    assert tweet["is_quote_status"] == False


def test_media_tweet_extract():
    tweet = twExtract.extractStatus(testMediaTweet)
    assert tweet["full_text"] == testMedia_compare["description"]
    assert tweet["user"]["screen_name"] == "Twitter"
    assert "extended_entities" in tweet
    assert len(tweet["extended_entities"]["media"]) == 1
    video = tweet["extended_entities"]["media"][0]
    assert video["media_url_https"] == "https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg"
    assert video["type"] == "photo"
    assert tweet["is_quote_status"] == False


def test_multimedia_tweet_extract():
    tweet = twExtract.extractStatus(testMultiMediaTweet)
    assert tweet["full_text"] == testMultiMedia_compare["description"]
    assert tweet["user"]["screen_name"] == "Twitter"
    assert "extended_entities" in tweet
    assert len(tweet["extended_entities"]["media"]) == 2
    video = tweet["extended_entities"]["media"][0]
    assert video["media_url_https"] == "https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg"
    assert video["type"] == "photo"
    video = tweet["extended_entities"]["media"][1]
    assert video["media_url_https"] == "https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg"
    assert video["type"] == "photo"


def test_poll_tweet_extract():
    tweet = twExtract.extractStatus(
        "https://twitter.com/norm/status/651169346518056960"
    )
    assert "card" in tweet
    compare_dict(testPoll_comparePoll, tweet["card"])


# VNF conversion test


async def test_text_tweet_vnf():
    vnf = await utils.link_to_vnf_from_unofficial_api(testTextTweet)
    compare_dict(textVNF_compare, vnf)


async def test_video_tweet_vnf():
    vnf = await utils.link_to_vnf_from_unofficial_api(testVideoTweet)
    compare_dict(videoVNF_compare, vnf)


async def test_media_tweet_vnf():
    vnf = await utils.link_to_vnf_from_unofficial_api(testMediaTweet)
    compare_dict(testMedia_compare, vnf)


async def test_multimedia_tweet_vnf():
    vnf = await utils.link_to_vnf_from_unofficial_api(testMultiMediaTweet)
    compare_dict(testMultiMedia_compare, vnf)


async def test_poll_tweet_vnf():
    vnf = await utils.link_to_vnf_from_unofficial_api(testPollTweet)
    compare_dict(testPoll_comparePollVNF, vnf["poll"])


async def test_qrt_tweet():
    cache.clear_cache()
    # this is an incredibly lazy test, todo: improve it in the future
    resp = await client.get(
        testQRTTweet.replace("https://twitter.com", ""), headers={"User-Agent": "test"}
    )
    assert resp.status_code == 200
    assert "Twitter says I have 382 followers" in str(resp.data)
    # test qrt-ception
    resp = await client.get(
        testQrtCeptionTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )  # get top level tweet
    assert resp.status_code == 200
    assert "Please retweet this to spread awareness for retweets" in str(resp.data)
    qtd_tweet = cache.get_vnf_from_link_cache(
        "https://twitter.com/EliLanger/status/585253161260216320"
    )  # check that the quoted tweet for the top level tweet is cached
    assert qtd_tweet is not None
    assert (
        qtd_tweet["qrtURL"] is not None
    )  # check that the quoted tweet for the top level tweet has a qrtURL
    assert (
        cache.get_vnf_from_link_cache(
            "https://twitter.com/EliLanger/status/313143446842007553"
        )
        is None
    )  # check that the bottom level tweet has NOT been cached
    resp = await client.get(
        "/EliLanger/status/585253161260216320", headers={"User-Agent": "test"}
    )  # get mid level tweet
    assert resp.status_code == 200
    assert (
        cache.get_vnf_from_link_cache(
            "https://twitter.com/EliLanger/status/313143446842007553"
        )
        is not None
    )  # check that the bottom level tweet has been cached now


async def test_qrt_video_tweet():
    cache.clear_cache()
    # this is an incredibly lazy test, todo: improve it in the future
    resp = await client.get(
        testQrtVideoTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    assert (
        'twitter:player:stream" content="https://video.twimg.com/tweet_video/FL0gdK8WUAIHHKa.mp4'
        in str(resp.data)
    )


# Test adding to cache ; cache should be empty
async def test_add_to_cache():
    cache.clear_cache()
    await utils.vnf_from_cache_or_dl(testTextTweet)
    await utils.vnf_from_cache_or_dl(testVideoTweet)
    await utils.vnf_from_cache_or_dl(testMediaTweet)
    await utils.vnf_from_cache_or_dl(testMultiMediaTweet)
    # retrieve
    compare_dict(textVNF_compare, cache.get_vnf_from_link_cache(testTextTweet))
    compare_dict(videoVNF_compare, cache.get_vnf_from_link_cache(testVideoTweet))
    compare_dict(testMedia_compare, cache.get_vnf_from_link_cache(testMediaTweet))
    compare_dict(
        testMultiMedia_compare, cache.get_vnf_from_link_cache(testMultiMediaTweet)
    )
    cache.clear_cache()


def test_embed_from_scratch():
    cache.clear_cache()
    client.get(
        testTextTweet.replace("https://twitter.com", ""), headers={"User-Agent": "test"}
    )
    client.get(
        testVideoTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    client.get(
        testMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    client.get(
        testMultiMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )


async def test_embed_from_cache():
    cache.clear_cache()
    await utils.vnf_from_cache_or_dl(testTextTweet)
    await utils.vnf_from_cache_or_dl(testVideoTweet)
    await utils.vnf_from_cache_or_dl(testMediaTweet)
    await utils.vnf_from_cache_or_dl(testMultiMediaTweet)
    # embed time
    resp = await client.get(
        testTextTweet.replace("https://twitter.com", ""), headers={"User-Agent": "test"}
    )
    assert resp.status_code == 200
    resp = await client.get(
        testVideoTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    resp = await client.get(
        testMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    resp = await client.get(
        testMultiMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200


async def test_very_long_embed():
    cache.clear_cache()
    cache.set_cache(
        {
            "https://twitter.com/TEST/status/1234": {
                "description": "A" * 1024,
                "hits": 0,
                "images": ["", "", "", "", ""],
                "likes": 1234,
                "nsfw": False,
                "pfp": "",
                "qrt": {},
                "rts": 1234,
                "screen_name": "TEST",
                "thumbnail": "",
                "time": "",
                "tweet": "https://twitter.com/TEST/status/1234",
                "type": "Text",
                "uploader": "Test",
                "url": "",
            }
        }
    )
    resp = await client.get(
        "https://twitter.com/TEST/status/1234".replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200


async def test_embed_from_outdated_cache():
    # presets a cache that has VNF's with missing fields; there's probably a better way to do this
    cache.set_cache(
        {
            "https://twitter.com/Twitter/status/1118295916874739714": {
                "description": "On profile pages, we used to only show someone’s replies, not the original Tweet 🙄 Now we’re showing both so you can follow the conversation more easily! https://t.co/LSBEZYFqmY",
                "hits": 0,
                "images": [
                    "https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg",
                    "",
                    "",
                    "",
                    "1",
                ],
                "likes": 5033,
                "nsfw": False,
                "pfp": "http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg",
                "qrt": {},
                "rts": 754,
                "screen_name": "Twitter",
                "thumbnail": "https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg",
                "time": "Tue Apr 16 23:31:38 +0000 2019",
                "tweet": "https://twitter.com/Twitter/status/1118295916874739714",
                "type": "Image",
                "uploader": "Twitter",
                "url": "",
            },
            "https://twitter.com/Twitter/status/1263145271946551300": {
                "description": "Testing, testing...\n\nA new way to have a convo with exactly who you want. We’re starting with a small % globally, so keep your 👀 out to see it in action. https://t.co/pV53mvjAVT",
                "hits": 0,
                "images": ["", "", "", "", ""],
                "likes": 61584,
                "nsfw": False,
                "pfp": "http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg",
                "qrt": {},
                "rts": 17138,
                "screen_name": "Twitter",
                "thumbnail": "http://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg",
                "time": "Wed May 20 16:31:15 +0000 2020",
                "tweet": "https://twitter.com/Twitter/status/1263145271946551300",
                "type": "Video",
                "uploader": "Twitter",
                "url": "https://video.twimg.com/amplify_video/1263145212760805376/vid/1280x720/9jous8HM0_duxL0w.mp4?tag=13",
            },
            "https://twitter.com/Twitter/status/1293239745695211520": {
                "description": "We tested, you Tweeted, and now we’re rolling it out to everyone! https://t.co/w6Q3Q6DiKz",
                "hits": 0,
                "images": [
                    "https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg",
                    "https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg",
                    "",
                    "",
                    "2",
                ],
                "likes": 5707,
                "nsfw": False,
                "pfp": "http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg",
                "qrt": {},
                "rts": 1416,
                "screen_name": "Twitter",
                "thumbnail": "https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg",
                "time": "Tue Aug 11 17:35:57 +0000 2020",
                "tweet": "https://twitter.com/Twitter/status/1293239745695211520",
                "type": "Image",
                "uploader": "Twitter",
                "url": "",
            },
            "https://twitter.com/jack/status/20": {
                "description": "just setting up my twttr",
                "hits": 0,
                "images": ["", "", "", "", ""],
                "likes": 179863,
                "nsfw": False,
                "pfp": "http://pbs.twimg.com/profile_images/1115644092329758721/AFjOr-K8_normal.jpg",
                "qrt": {},
                "rts": 122021,
                "screen_name": "jack",
                "thumbnail": "",
                "time": "Tue Mar 21 20:50:14 +0000 2006",
                "tweet": "https://twitter.com/jack/status/20",
                "type": "Text",
                "uploader": "jack",
                "url": "",
            },
            testQrtVideoTweet: {
                "tweet": "https://twitter.com/Twitter/status/1494436688554344449",
                "url": "",
                "description": "https://twitter.com/TwitterSupport/status/1494386367467593737",
                "thumbnail": "",
                "uploader": "Twitter",
                "screen_name": "Twitter",
                "pfp": "http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg",
                "type": "Text",
                "images": ["", "", "", "", ""],
                "likes": 5186,
                "rts": 703,
                "time": "Thu Feb 17 22:20:46 +0000 2022",
                "qrt": {
                    "desc": "Keep your fave DM convos easily accessible by pinning them! You can now pin up to six conversations that will stay at the top of your DM inbox.\n\nAvailable on Android, iOS, and web. https://t.co/kIjlzf9XLJ",
                    "handle": "Twitter Support",
                    "screen_name": "TwitterSupport",
                    "verified": True,
                    "id": "1494386367467593737",
                },
                "nsfw": False,
                "verified": True,
                "size": {},
            },
        }
    )
    # embed time
    resp = await client.get(
        testTextTweet.replace("https://twitter.com", ""), headers={"User-Agent": "test"}
    )
    assert resp.status_code == 200
    resp = await client.get(
        testVideoTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    resp = await client.get(
        testMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    resp = await client.get(
        testMultiMediaTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    # qrt
    resp = await client.get(
        testQrtVideoTweet.replace("https://twitter.com", ""),
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    assert (
        'twitter:player:stream" content="https://video.twimg.com/tweet_video/FL0gdK8WUAIHHKa.mp4'
        in str(resp.data)
    )


async def test_directEmbed():
    resp = await client.get(
        testVideoTweet.replace("https://twitter.com", "") + ".mp4",
        headers={"User-Agent": "test"},
    )
    assert resp.status_code == 200
    assert videoVNF_compare["url"] in str(resp.data)


async def test_message404():
    resp = await client.get(
        "https://twitter.com/jack/status/12345", headers={"User-Agent": "test"}
    )
    assert resp.status_code == 200
    assert constants.tweet_not_found in str(resp.data)


async def test_combine():
    twt, e = await utils.vnf_from_cache_or_dl(testMultiMediaTweet)
    img1 = twt["images"][0]
    img2 = twt["images"][1]
    resp = await client.get(
        f"/rendercombined.jpg?imgs={img1},{img2}", headers={"User-Agent": "test"}
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "image/jpeg"
    assert len(await resp.data) > 1000

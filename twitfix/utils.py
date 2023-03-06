import re
import textwrap
import urllib.parse
from datetime import datetime, timedelta

from loguru import logger
from quart import redirect, render_template
from yt_dlp.utils import ExtractorError

from twExtract import extract_status
from twExtract.twExtractError import TwExtractError
from twitfix import constants, messages
from twitfix.cache import cache
from twitfix.config_handler import config


def oembed_gen(description, user, video_link, ttype):
    return {
        "type": ttype,
        "version": "1.0",
        "provider_name": config["config"]["appname"],
        "provider_url": config["config"]["repo"],
        "title": description,
        "author_name": user,
        "author_url": video_link,
    }


async def vnf_from_cache_or_dl(video_link: str):
    cached_vnf = cache.get_vnf_from_link_cache(video_link)
    if cached_vnf is None:
        try:
            vnf = await link_to_vnf(video_link)
            cache.add_vnf_to_link_cache(video_link, vnf)
            return vnf, None
        except (ExtractorError, TwExtractError) as exErr:
            if (
                "HTTP Error 404" in exErr.msg
                or "No status found with that ID" in exErr.msg
            ):
                exErr.msg = constants.TWEET_NOT_FOUND
            elif "suspended" in exErr.msg:
                exErr.msg = constants.TWEET_SUSPENDED
            else:
                exErr.msg = None
            return None, exErr.msg
        except Exception as e:
            logger.error(e)
            return None, None
    else:
        return upgrade_vnf(cached_vnf), None


def get_default_ttl():
    # TTL for deleting items from the database
    return datetime.today().replace(microsecond=0) + timedelta(days=1)


async def direct_video(video_link):
    # Just get a redirect to a MP4 link from any tweet link
    vnf, e = await vnf_from_cache_or_dl(video_link)
    if vnf is not None:
        return redirect(vnf["url"], 301)
    else:
        if e is not None:
            return await message(
                constants.FAILED_TO_SCAN + constants.FAILED_TO_SCAN_EXTRA + e
            )
        return await message(constants.FAILED_TO_SCAN)


async def direct_video_link(video_link):
    # Just get a redirect to a MP4 link from any tweet link
    vnf, e = await vnf_from_cache_or_dl(video_link)
    if vnf is not None:
        return vnf["url"]
    else:
        if e is not None:
            return await message(
                constants.FAILED_TO_SCAN + constants.FAILED_TO_SCAN_EXTRA + e
            )
        return await message(constants.FAILED_TO_SCAN)


async def embed_video(video_link, image=0):
    # Return Embed from any tweet link
    vnf, e = await vnf_from_cache_or_dl(video_link)

    if vnf is not None:
        return await embed(video_link, vnf, image)
    else:
        if e is not None:
            return await message(
                constants.FAILED_TO_SCAN + constants.FAILED_TO_SCAN_EXTRA + e
            )
        return await message(constants.FAILED_TO_SCAN)


def upgrade_vnf(vnf):
    # Makes sure any VNF object passed through this has proper fields if they're added in later versions
    if "verified" not in vnf:
        vnf["verified"] = False
    if "size" not in vnf:
        if vnf["type"] == "Video":
            vnf["size"] = {"width": 720, "height": 480}
        else:
            vnf["size"] = {}
    if "qrtURL" not in vnf:
        if vnf["qrt"] == {}:
            vnf["qrtURL"] = None
        else:  #
            vnf[
                "qrtURL"
            ] = f"https://twitter.com/{vnf['qrt']['screen_name']}/status/{vnf['qrt']['id']}"
    if "isGif" not in vnf:
        vnf["isGif"] = False
    return vnf


def tweet_info(
    url,
    tweet="",
    desc="",
    thumb="",
    uploader="",
    screen_name="",
    pfp="",
    tweet_type="",
    images="",
    hits=0,
    likes=0,
    rts=0,
    time="",
    qrt_url="",
    nsfw=False,
    ttl=None,
    verified=False,
    size=None,
    poll=None,
    is_gif=False,
):
    # Return a dict of video info with default values
    if ttl is None:
        ttl = get_default_ttl()
    vnf = {
        "tweet": tweet,
        "url": url,
        "description": desc,
        "thumbnail": thumb,
        "uploader": uploader,
        "screen_name": screen_name,
        "pfp": pfp,
        "type": tweet_type,
        "images": images,
        "hits": hits,
        "likes": likes,
        "rts": rts,
        "time": time,
        "qrtURL": qrt_url,
        "nsfw": nsfw,
        "ttl": ttl,
        "verified": verified,
        "size": size or {},
        "poll": poll,
        "isGif": is_gif,
    }
    if poll is None:
        del vnf["poll"]
    return vnf


def link_to_vnf_from_tweet_data(tweet, video_link):
    images = [""] * 5
    logger.info(" ➤ [ + ] Tweet Type: " + tweet_type(tweet))
    is_gif = False
    # Check to see if tweet has a video, if not, make the url passed to the VNF the first t.co link in the tweet
    match tweet_type(tweet):
        case "Video":
            if tweet["extended_entities"]["media"][0]["video_info"]["variants"]:
                best_bitrate = -1
                thumb = tweet["extended_entities"]["media"][0]["media_url"]
                size = tweet["extended_entities"]["media"][0]["original_info"]
                for video in tweet["extended_entities"]["media"][0]["video_info"][
                    "variants"
                ]:
                    if (
                        video["content_type"] == "video/mp4"
                        and video["bitrate"] > best_bitrate
                    ):
                        url = video["url"]
                        best_bitrate = video["bitrate"]
        case "Text":
            url = ""
            thumb = ""
            size = {}
        case _:
            images = [""] * 5
            i = 0
            for media in tweet["extended_entities"]["media"]:
                images[i] = media["media_url_https"]
                i = i + 1

            images[4] = str(i)
            url = ""
            images = images
            thumb = tweet["extended_entities"]["media"][0]["media_url_https"]
            size = {}

    if (
        "extended_entities" in tweet
        and "media" in tweet["extended_entities"]
        and tweet["extended_entities"]["media"][0]["type"] == "animated_gif"
    ):
        is_gif = True

    qrt_url = None
    if "quoted_status" in tweet and "quoted_status_permalink" in tweet:
        qrt_url = tweet["quoted_status_permalink"]["expanded"]

    text = tweet["full_text"]

    if "possibly_sensitive" in tweet:
        nsfw = tweet["possibly_sensitive"]
    else:
        nsfw = False

    if "entities" in tweet and "urls" in tweet["entities"]:
        for entity_url in tweet["entities"]["urls"]:
            if "/status/" in entity_url["expanded_url"] and entity_url[
                "expanded_url"
            ].startswith("https://twitter.com/"):
                text = text.replace(entity_url["url"], "")
            else:
                text = text.replace(entity_url["url"], entity_url["expanded_url"])
    ttl = None

    if "card" in tweet and tweet["card"]["name"].startswith("poll"):
        poll = get_poll_object(tweet["card"])
        if not tweet["card"]["binding_values"]["counts_are_final"]["boolean_value"]:
            ttl = datetime.today().replace(microsecond=0) + timedelta(minutes=1)
    else:
        poll = None

    vnf = tweet_info(
        url,
        video_link,
        text,
        thumb,
        tweet["user"]["name"],
        tweet["user"]["screen_name"],
        tweet["user"]["profile_image_url"],
        tweet_type(tweet),
        likes=tweet["favorite_count"],
        rts=tweet["retweet_count"],
        time=tweet["created_at"],
        qrt_url=qrt_url,
        images=images,
        nsfw=nsfw,
        verified=tweet["user"]["verified"],
        size=size,
        poll=poll,
        ttl=ttl,
        is_gif=is_gif,
    )

    return vnf


async def link_to_vnf_from_unofficial_api(video_link):
    logger.info(
        " ➤ [ + ] Attempting to download tweet info from UNOFFICIAL Twitter API"
    )
    tweet = await extract_status(video_link)
    logger.success(" ➤ [ ✔ ] Unofficial API Success")
    return link_to_vnf_from_tweet_data(tweet, video_link)


async def link_to_vnf(video_link):
    # Return a VideoInfo object or die trying
    return await link_to_vnf_from_unofficial_api(video_link)


async def get_template(
    template,
    vnf,
    desc,
    image,
    color,
    url_desc,
    url_user,
    url_link,
    app_name_suffix="",
    embed_vnf=None,
):
    if embed_vnf is None:
        embed_vnf = vnf
    if "width" in embed_vnf["size"] and "height" in embed_vnf["size"]:
        embed_vnf["size"]["width"] = min(embed_vnf["size"]["width"], 2000)
        embed_vnf["size"]["height"] = min(embed_vnf["size"]["height"], 2000)
    return await render_template(
        template,
        likes=vnf["likes"],
        rts=vnf["rts"],
        time=vnf["time"],
        screenName=vnf["screen_name"],
        vidlink=embed_vnf["url"],
        userLink=f"https://twitter.com/{vnf['screen_name']}",
        pfp=vnf["pfp"],
        vidurl=embed_vnf["url"],
        desc=desc,
        pic=image,
        user=vnf["uploader"],
        video_link=vnf,
        color=color,
        appname=config["config"]["appname"] + app_name_suffix,
        repo=config["config"]["repo"],
        url=config["config"]["url"],
        urlDesc=url_desc,
        urlUser=url_user,
        urlLink=url_link,
        urlUserLink=urllib.parse.quote(f"https://twitter.com/{vnf['screen_name']}"),
        tweetLink=vnf["tweet"],
        videoSize=embed_vnf["size"],
    )


async def embed(video_link, vnf, image):
    logger.info(" ➤ [ E ] Embedding " + vnf["type"] + ": " + video_link)

    desc = re.sub(r" http.*t\.co\S+", "", vnf["description"])
    url_user = urllib.parse.quote(vnf["uploader"])
    url_desc = urllib.parse.quote(desc)
    url_link = urllib.parse.quote(video_link)
    like_display = messages.gen_likes_display(vnf)

    if "poll" in vnf:
        poll_display = messages.gen_poll_display(vnf["poll"])
    else:
        poll_display = ""

    qrt = None
    if vnf["qrtURL"] is not None:
        qrt, e = await vnf_from_cache_or_dl(vnf["qrtURL"])
        if qrt is not None:
            desc = messages.format_embed_desc(
                vnf["type"], desc, qrt, poll_display, like_display
            )
    else:
        desc = messages.format_embed_desc(
            vnf["type"], desc, None, poll_display, like_display
        )
    embed_vnf = None
    app_name_post = ""

    match vnf["type"]:
        # Change the template based on tweet type
        case "Text":
            template = "text.html"
            if qrt is not None and qrt["type"] != "Text":
                embed_vnf = qrt
                if qrt["type"] == "Image":
                    if embed_vnf["images"][4] != "1":
                        app_name_post = (
                            " - Image " + str(image + 1) + "/" + str(vnf["images"][4])
                        )
                    image = embed_vnf["images"][image]
                    template = "image.html"
                elif qrt["type"] == "Video" or qrt["type"] == "":
                    url_desc = urllib.parse.quote(
                        textwrap.shorten(desc, width=220, placeholder="...")
                    )
                    template = "video.html"
        case "Image":
            if vnf["images"][4] != "1":
                app_name_post = (
                    " - Image " + str(image + 1) + "/" + str(vnf["images"][4])
                )
            image = vnf["images"][image]
            template = "image.html"
        case "Video":
            if vnf["isGif"] and config["config"]["gifConvertAPI"] not in ["", "none"]:
                vnf[
                    "url"
                ] = f"{config['config']['gifConvertAPI']}/convert.mp4?url={vnf['url']}"
                app_name_post = " - GIF"
            url_desc = urllib.parse.quote(
                textwrap.shorten(desc, width=220, placeholder="...")
            )
            template = "video.html"
        case _:
            url_desc = urllib.parse.quote(
                textwrap.shorten(desc, width=220, placeholder="...")
            )
            template = "video.html"

    color = "#7FFFD4"  # Green

    if vnf["nsfw"]:
        color = "#800020"  # Red

    return await get_template(
        template,
        vnf,
        desc,
        image,
        color,
        url_desc,
        url_user,
        url_link,
        app_name_post,
        embed_vnf,
    )


async def embed_combined(video_link):
    vnf, e = await vnf_from_cache_or_dl(video_link)

    if vnf is not None:
        return await embed_combined_vnf(video_link, vnf)
    else:
        if e is not None:
            return await message(
                constants.FAILED_TO_SCAN + constants.FAILED_TO_SCAN_EXTRA + e
            )
        return await message(constants.FAILED_TO_SCAN)


async def embed_combined_vnf(video_link, vnf):
    if vnf["type"] != "Image" or vnf["images"][4] == "1":
        return embed(video_link, vnf, 0)

    desc = re.sub(r" http.*t\.co\S+", "", vnf["description"])
    url_user = urllib.parse.quote(vnf["uploader"])
    url_desc = urllib.parse.quote(desc)
    url_link = urllib.parse.quote(video_link)
    like_display = messages.gen_likes_display(vnf)

    if "poll" in vnf:
        poll_display = messages.gen_poll_display(vnf["poll"])
    else:
        poll_display = ""

    if vnf["qrtURL"] is not None:
        qrt, e = await vnf_from_cache_or_dl(vnf["qrtURL"])
        if qrt is not None:
            desc = messages.format_embed_desc(
                vnf["type"], desc, qrt, poll_display, like_display
            )

    image = "https://vxtwitter.com/rendercombined.jpg?imgs="
    for i in range(0, int(vnf["images"][4])):
        image = image + vnf["images"][i] + ","
    image = image[:-1]  # Remove last comma

    color = "#7FFFD4"  # Green

    if vnf["nsfw"]:
        color = "#800020"  # Red
    return await get_template(
        "image.html",
        vnf,
        desc,
        image,
        color,
        url_desc,
        url_user,
        url_link,
        app_name_suffix=" - View original tweet for full quality",
    )


def get_poll_object(card):
    poll = {"total_votes": 0, "choices": []}
    choice_count = 0
    if card["name"] == "poll2choice_text_only":
        choice_count = 2
    elif card["name"] == "poll3choice_text_only":
        choice_count = 3
    elif card["name"] == "poll4choice_text_only":
        choice_count = 4

    for i in range(0, choice_count):
        choice = {
            "text": card["binding_values"][f"choice{i+1}_label"]["string_value"],
            "votes": int(card["binding_values"][f"choice{i+1}_count"]["string_value"]),
        }
        poll["total_votes"] += choice["votes"]
        poll["choices"].append(choice)
    # update each choice with a percentage
    for choice in poll["choices"]:
        choice["percent"] = round((choice["votes"] / poll["total_votes"]) * 100, 1)

    return poll


def tweet_type(tweet):
    # Are we dealing with a Video, Image, or Text tweet?
    if "extended_entities" in tweet:
        if "video_info" in tweet["extended_entities"]["media"][0]:
            out = "Video"
        else:
            out = "Image"
    else:
        out = "Text"
    return out


async def message(text):
    return await render_template(
        "default.html",
        message=text,
        color=config["config"]["color"],
        appname=config["config"]["appname"],
        repo=config["config"]["repo"],
        url=config["config"]["url"],
    )

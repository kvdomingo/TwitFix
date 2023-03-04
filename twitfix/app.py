import os
from http import HTTPStatus
from io import BytesIO

from flask import Flask, abort, redirect, request, send_file, send_from_directory
from flask_cors import CORS

import combineImg
import twitfix.constants
from twitfix.config_handler import config
from twitfix.constants import GENERATE_EMBED_USER_AGENTS, PATH_REGEX
from twitfix.utils import (
    direct_video,
    embed_combined,
    embed_video,
    get_template,
    message,
    oembed_gen,
    vnf_from_cache_or_dl,
)

app = Flask(__name__)
CORS(app)


@app.route("/")
def default():
    # If the useragent is discord, return the embed, if not, redirect to configured repo directly
    user_agent = request.headers.get("user-agent")
    if user_agent in GENERATE_EMBED_USER_AGENTS:
        return message(
            "TwitFix is an attempt to fix twitter video embeds in discord! created by Robin Universe :)\n\n💖\n\nClick me to be redirected to the repo!"
        )
    else:
        return redirect(config["config"]["repo"], HTTPStatus.MOVED_PERMANENTLY)


@app.route("/oembed.json")  # oEmbed endpoint
def oembed_end():
    desc = request.args.get("desc", None)
    user = request.args.get("user", None)
    link = request.args.get("link", None)
    ttype = request.args.get("ttype", None)
    return oembed_gen(desc, user, link, ttype)


@app.route("/<path:sub_path>")  # Default endpoint used by everything
def twitfix(sub_path):
    user_agent = request.headers.get("user-agent")
    match = PATH_REGEX.search(sub_path)

    if request.url.startswith("https://d.vx"):
        # Matches d.fx? Try to give the user a direct link
        if match.start() == 0:
            twitter_url = "https://twitter.com/" + sub_path
        if user_agent in GENERATE_EMBED_USER_AGENTS:
            print(" ➤ [ D ] d.vx link shown to discord user-agent!")
            if request.url.endswith(".mp4") and "?" not in request.url:

                if "?" not in request.url:
                    clean = twitter_url[:-4]
                else:
                    clean = twitter_url

                vnf, e = vnf_from_cache_or_dl(clean)
                if vnf is None:
                    if e is not None:
                        return message(
                            twitfix.constants.failed_to_scan
                            + twitfix.constants.failed_to_scan_extra
                            + e
                        )
                    return message(twitfix.constants.failed_to_scan)
                return get_template("rawvideo.html", vnf, "", "", "", "", "", "")
            else:
                return message(
                    "To use a direct MP4 link in discord, remove anything past '?' and put '.mp4' at the end"
                )
        else:
            print(" ➤ [ R ] Redirect to MP4 using d.fxtwitter.com")
            return dir(sub_path)
    elif request.url.endswith(".mp4") or request.url.endswith("%2Emp4"):
        twitter_url = "https://twitter.com/" + sub_path

        if "?" not in request.url:
            clean = twitter_url[:-4]
        else:
            clean = twitter_url

        vnf, e = vnf_from_cache_or_dl(clean)
        if vnf is None:
            if e is not None:
                return message(
                    twitfix.constants.failed_to_scan
                    + twitfix.constants.failed_to_scan_extra
                    + e
                )
            return message(twitfix.constants.failed_to_scan)
        return get_template("rawvideo.html", vnf, "", "", "", "", "", "")

    elif (
        request.url.endswith("/1")
        or request.url.endswith("/2")
        or request.url.endswith("/3")
        or request.url.endswith("/4")
        or request.url.endswith("%2F1")
        or request.url.endswith("%2F2")
        or request.url.endswith("%2F3")
        or request.url.endswith("%2F4")
    ):
        twitter_url = "https://twitter.com/" + sub_path

        if "?" not in request.url:
            clean = twitter_url[:-2]
        else:
            clean = twitter_url

        image = int(request.url[-1]) - 1
        return embed_video(clean, image)

    if match is not None:
        twitter_url = sub_path

        if match.start() == 0:
            twitter_url = "https://twitter.com/" + sub_path

        if user_agent in GENERATE_EMBED_USER_AGENTS:
            res = embed_combined(twitter_url)
            return res

        else:
            print(" ➤ [ R ] Redirect to " + twitter_url)
            return redirect(twitter_url, 301)
    else:
        return message("This doesn't appear to be a twitter URL")


@app.route(
    "/dir/<path:sub_path>"
)  # Try to return a direct link to the MP4 on twitters servers
def dir(sub_path):
    user_agent = request.headers.get("user-agent")
    url = sub_path
    match = PATH_REGEX.search(url)
    if match is not None:
        twitter_url = url

        if match.start() == 0:
            twitter_url = "https://twitter.com/" + url

        if user_agent in GENERATE_EMBED_USER_AGENTS:
            res = embed_video(twitter_url)
            return res

        else:
            print(" ➤ [ R ] Redirect to direct MP4 URL")
            return direct_video(twitter_url)
    else:
        return redirect(url, 301)


@app.route("/favicon.ico")
def favicon():  # pragma: no cover
    return send_from_directory(
        os.path.join(app.root_path, "../static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/rendercombined.jpg")
def rendercombined():
    # get "imgs" from request arguments
    imgs = request.args.get("imgs", "")

    if (
        "combination_method" in config["config"]
        and config["config"]["combination_method"] != "local"
    ):
        url = (
            config["config"]["combination_method"] + "/rendercombined.jpg?imgs=" + imgs
        )
        return redirect(url, 302)
    # Redirecting here instead of setting the embed URL directly to this because if the config combination_method changes in the future, old URLs will still work

    imgs = imgs.split(",")
    if len(imgs) == 0 or len(imgs) > 4:
        abort(400)
    # check that each image starts with "https://pbs.twimg.com"
    for img in imgs:
        if not img.startswith("https://pbs.twimg.com"):
            abort(400)
    finalImg = combineImg.genImageFromURL(imgs)
    imgIo = BytesIO()
    finalImg = finalImg.convert("RGB")
    finalImg.save(imgIo, "JPEG", quality=70)
    imgIo.seek(0)
    return send_file(imgIo, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

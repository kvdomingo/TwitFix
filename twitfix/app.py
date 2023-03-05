import os
import re
from http import HTTPStatus
from io import BytesIO
from urllib import parse

from loguru import logger
from quart import Quart, abort, redirect, request, send_file, send_from_directory
from quart_cors import cors

from combine_img import gen_image_from_url
from twitfix.config_handler import config
from twitfix.constants import APP_HOSTNAME, GENERATE_EMBED_USER_AGENTS, PATH_REGEX
from twitfix.utils import (
    direct_video,
    embed_combined,
    embed_video,
    get_template,
    message,
    oembed_gen,
    vnf_from_cache_or_dl,
)

app = Quart(__name__)
app = cors(app, allow_origin="*")


@app.route("/")
async def default():
    # If the useragent is discord, return the embed, if not, redirect to configured repo directly
    user_agent = request.headers.get("user-agent")
    if user_agent in GENERATE_EMBED_USER_AGENTS:
        return await message(
            "TwitFix is an attempt to fix twitter video embeds in discord! created by Robin Universe :)\n\n💖\n\nClick me to be redirected to the repo!"
        )
    else:
        return redirect(config["config"]["repo"], HTTPStatus.MOVED_PERMANENTLY)


@app.route("/oembed.json")
async def oembed_end():
    # oEmbed endpoint
    desc = request.args.get("desc")
    user = request.args.get("user")
    link = request.args.get("link")
    ttype = request.args.get("ttype")
    return oembed_gen(desc, user, link, ttype)


@app.route("/<path:sub_path>")
async def twitfix(sub_path):
    # Default endpoint used by everything
    user_agent = request.headers.get("user-agent")
    match = PATH_REGEX.search(sub_path)
    request_url = parse.urlparse(request.url)

    if request_url.hostname.startswith(f"d.{APP_HOSTNAME[:2]}"):
        twitter_url = parse.urlparse(f"https://twitter.com/{sub_path}")
        if user_agent in GENERATE_EMBED_USER_AGENTS:
            logger.info(" ➤ [ D ] d.vx link shown to discord user-agent!")
            clean = twitter_url._replace(query="")
            vnf, e = await vnf_from_cache_or_dl(clean.geturl())
            if vnf is None:
                if e is not None:
                    return await message(
                        twitfix.constants.FAILED_TO_SCAN
                        + twitfix.constants.FAILED_TO_SCAN_EXTRA
                        + e
                    )
                return await message(twitfix.constants.FAILED_TO_SCAN)
            return await get_template("rawvideo.html", vnf, "", "", "", "", "", "")
        else:
            logger.info(f" ➤ [ R ] Redirect to MP4 using {APP_HOSTNAME}")
            return await dir_(sub_path)
    elif request_url.path.endswith("mp4"):
        twitter_url = parse.urlparse(f"https://twitter.com/{sub_path}")
        clean = twitter_url._replace(query="")
        vnf, e = await vnf_from_cache_or_dl(clean.geturl())
        if vnf is None:
            if e is not None:
                return await message(
                    twitfix.constants.FAILED_TO_SCAN
                    + twitfix.constants.FAILED_TO_SCAN_EXTRA
                    + e
                )
            return await message(twitfix.constants.FAILED_TO_SCAN)
        return await get_template("rawvideo.html", vnf, "", "", "", "", "", "")

    elif re.search(r"(/|%2F)?[1234]$", request_url.path):
        twitter_url = parse.urlparse(f"https://twitter.com/{sub_path}")
        clean = twitter_url._replace(query="")
        image = int(request_url.path[-1]) - 1
        return await embed_video(clean.geturl(), image)

    if match is not None:
        twitter_url = parse.urlparse(f"https://twitter.com/{sub_path}")

        if user_agent in GENERATE_EMBED_USER_AGENTS:
            return await embed_combined(twitter_url.geturl())
        else:
            logger.info(f" ➤ [ R ] Redirect to {twitter_url.geturl()}")
            return redirect(twitter_url.geturl(), HTTPStatus.MOVED_PERMANENTLY)
    else:
        return await message("This doesn't appear to be a twitter URL")


@app.route("/dir/<path:sub_path>")
async def dir_(sub_path):
    # Try to return a direct link to the MP4 on twitters servers
    user_agent = request.headers.get("user-agent")
    url = sub_path
    match = PATH_REGEX.search(url)
    if match is not None:
        twitter_url = "https://twitter.com/" + url
        if user_agent in GENERATE_EMBED_USER_AGENTS:
            return await embed_video(twitter_url)
        else:
            logger.info(" ➤ [ R ] Redirect to direct MP4 URL")
            return await direct_video(twitter_url)
    else:
        return redirect(url, HTTPStatus.MOVED_PERMANENTLY)


@app.route("/favicon.ico")
async def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/rendercombined.jpg")
async def render_combined():
    # get "images" from request arguments
    images = request.args.get("imgs", "")

    if (
        "combination_method" in config["config"]
        and config["config"]["combination_method"] != "local"
    ):
        url = (
            config["config"]["combination_method"]
            + "/rendercombined.jpg?imgs="
            + images
        )
        return redirect(url, HTTPStatus.TEMPORARY_REDIRECT)
    # Redirecting here instead of setting the embed URL directly to this because if the config combination_method
    # changes in the future, old URLs will still work

    images = images.split(",")
    if len(images) == 0 or len(images) > 4:
        abort(400)
    # check that each image starts with "https://pbs.twimg.com"
    for img in images:
        if not img.startswith("https://pbs.twimg.com"):
            abort(400)
    final_img = gen_image_from_url(images)
    img_io = BytesIO()
    final_img = final_img.convert("RGB")
    final_img.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    return await send_file(img_io, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

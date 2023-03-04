from twitfix.constants import tweet_desc_limit


def gen_likes_display(vnf):
    return f"\n\n💖 {vnf['likes']} 🔁 {vnf['rts']}"


def gen_qrt_display(qrt):
    verified_check = "☑️" if ("verified" in qrt and qrt["verified"]) else ""
    return f"\n【QRT of {qrt['uploader']} (@{qrt['screen_name']}){verified_check}:】\n'{qrt['description']}'"


def gen_poll_display(poll):
    pct_split = 10
    output = "\n\n"
    for choice in poll["choices"]:
        output += (
            choice["text"]
            + "\n"
            + ("█" * int(choice["percent"] / pctSplit))
            + " "
            + str(choice["percent"])
            + "%\n"
        )
    return output


def format_embed_desc(type_, body, qrt, poll_display, likes_display):
    # Trim the embed description to 248 characters, prioritizing poll and likes
    output = ""
    if poll_display is None:
        poll_display = ""

    if qrt is not None and not (type_ == "" or type_ == "Video"):

        qrt_display = gen_qrt_display(qrt)
        if (
            "id" in qrt
            and ("https://twitter.com/" + qrt["screen_name"] + "/status/" + qrt["id"])
            in body
        ):
            body = body.replace(
                ("https://twitter.com/" + qrt["screen_name"] + "/status/" + qrt["id"]),
                "",
            )
            body = body.strip()
        body += qrt_display
        qrt = None

    if type_ == "" or type_ == "Video":
        output = body + poll_display
    elif qrt is None:
        output = body + poll_display + likes_display
    else:
        output = body + likes_display
    if len(output) > tweet_desc_limit:
        # find out how many characters we need to remove
        diff = len(output) - tweet_desc_limit
        # remove the characters from body, add ellipsis
        body = body[: -(diff + 1)] + "…"
        return format_embed_desc(type_, body, qrt, poll_display, likes_display)
    else:
        return output

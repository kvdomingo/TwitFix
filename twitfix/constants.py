import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PATH_REGEX = re.compile(r"\w{1,15}/(status|statuses)/\d{2,20}")

GENERATE_EMBED_USER_AGENTS = [
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/1596241936; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0",
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam FriendsUI Tenfoot/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
    "TelegramBot (like TwitterBot)",
    "Mozilla/5.0 (compatible; January/1.0; +https://gitlab.insrt.uk/revolt/january)",
    "Synapse (bot; +https://github.com/matrix-org/synapse)",
    "test",
]

FAILED_TO_SCAN = "Failed to scan your link! This may be due to an incorrect link, private/suspended account, deleted tweet, or Twitter itself might be having issues (Check here: https://api.twitterstat.us/)"

FAILED_TO_SCAN_EXTRA = "\n\nTwitter gave me this error: "

TWEET_NOT_FOUND = "deleted tweet"

TWEET_SUSPENDED = "This Tweet is from a suspended account."

TWEET_DESC_LIMIT = 340

APP_HOSTNAME = "qxtwitter.com"

APP_NAME = "qxTwitter"

GITHUB_REPO = "kvdomingo/TwitFix"

import json
import os

from twitfix.constants import BASE_DIR

if os.environ.get("RUNNING_TESTS"):
    config = {
        "config": {
            "link_cache": "ram",
            "database": "",
            "table": "",
            "color": "",
            "appname": "vxTwitter",
            "repo": "https://github.com/dylanpdx/BetterTwitFix",
            "url": "https://vxtwitter.com",
            "combination_method": "local",
            "gifConvertAPI": "",
        }
    }
elif os.environ.get("RUNNING_SERVERLESS") == "1":  # pragma: no cover
    config = {
        "config": {
            "link_cache": os.environ["VXTWITTER_LINK_CACHE"],
            "database": os.environ["VXTWITTER_DATABASE"],
            "table": os.environ["VXTWITTER_CACHE_TABLE"],
            "color": os.environ["VXTWITTER_COLOR"],
            "appname": os.environ["VXTWITTER_APP_NAME"],
            "repo": os.environ["VXTWITTER_REPO"],
            "url": os.environ["VXTWITTER_URL"],
            "combination_method": os.environ[
                "VXTWITTER_COMBINATION_METHOD"
            ],  # can either be 'local' or a URL to a server handling requests in the same format
            "gifConvertAPI": os.environ["VXTWITTER_GIF_CONVERT_API"],
        }
    }
else:
    # Read config from config.json. If it does not exist, create new.
    if not (path := BASE_DIR / "twitfix" / "config.json").exists():
        with open(path, "w+") as outfile:
            default_config = {
                "config": {
                    "link_cache": "json",
                    "database": "[url to mongo database goes here]",
                    "table": "TwiFix",
                    "color": "#43B581",
                    "appname": "vxTwitter",
                    "repo": "https://github.com/dylanpdx/BetterTwitFix",
                    "url": "https://vxtwitter.com",
                    "combination_method": "local",  # can either be 'local' or a URL to a server handling requests in the same format
                    "gifConvertAPI": "",
                }
            }

            json.dump(default_config, outfile, indent=4, sort_keys=True)
        config = default_config
    else:
        with open(path, "r") as f:
            config = json.load(f)

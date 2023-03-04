import json
import os

if "RUNNING_TESTS" in os.environ:
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
elif (
    "RUNNING_SERVERLESS" in os.environ and os.environ["RUNNING_SERVERLESS"] == "1"
):  # pragma: no cover
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
    if not os.path.exists("config.json"):
        with open("config.json", "w") as outfile:
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
        f = open("config.json")
        config = json.load(f)
        f.close()

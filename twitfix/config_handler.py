import json
import os

from twitfix.constants import APP_HOSTNAME, APP_NAME, BASE_DIR, GITHUB_REPO

if os.environ.get("RUNNING_TESTS"):
    config = {
        "config": {
            "link_cache": "memory",
            "database": "",
            "table": "",
            "color": "",
            "appname": APP_NAME,
            "repo": f"https://github.com/{GITHUB_REPO}",
            "url": f"https://{APP_HOSTNAME}",
            "combination_method": "local",
            "gifConvertAPI": "",
        }
    }
elif os.environ.get("RUNNING_SERVERLESS") == "1":  # pragma: no cover
    config = {
        "config": {
            "link_cache": "memory",
            "database": os.environ["VXTWITTER_DATABASE"],
            "table": os.environ["VXTWITTER_CACHE_TABLE"],
            "color": os.environ["VXTWITTER_COLOR"],
            "appname": APP_NAME,
            "repo": f"https://github.com/{GITHUB_REPO}",
            "url": f"https://{APP_HOSTNAME}",
            "combination_method": os.environ["VXTWITTER_COMBINATION_METHOD"],
            # can either be 'local' or a URL to a server handling requests in the same format
            "gifConvertAPI": os.environ["VXTWITTER_GIF_CONVERT_API"],
        }
    }
else:
    # Read config from config.json. If it does not exist, create new.
    if not (path := BASE_DIR / "twitfix" / "config.json").exists():
        with open(path, "w+") as outfile:
            default_config = {
                "config": {
                    "link_cache": "memory",
                    "database": "[url to mongo database goes here]",
                    "table": "qxTwitter",
                    "color": "#43B581",
                    "appname": APP_NAME,
                    "repo": f"https://github.com/{GITHUB_REPO}",
                    "url": f"https://{APP_HOSTNAME}",
                    "combination_method": "local",
                    # can either be 'local' or a URL to a server handling requests in the same format
                    "gifConvertAPI": "",
                }
            }
            json.dump(default_config, outfile, indent=4, sort_keys=True)
        config = default_config
    else:
        with open(path, "r") as f:
            config = json.load(f)

import json
from datetime import date, datetime
from functools import lru_cache

from loguru import logger

from twitfix.config_handler import config
from twitfix.constants import BASE_DIR

link_cache_system = config["config"]["link_cache"]

link_cache = {}

match link_cache_system:
    case "json":
        if not (path := BASE_DIR / "twitfix" / "links.json").exists():
            with open(path, "w+") as outfile:
                default_link_cache = {}
                json.dump(default_link_cache, outfile)
        with open(path, "r") as f:
            link_cache = json.load(f)
    case "memory":
        pass


def serialize_unknown(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def add_vnf_to_link_cache(video_link, vnf):
    video_link = video_link.lower()
    try:
        match link_cache_system:
            case "json":
                link_cache[video_link] = vnf
                with open(BASE_DIR / "twitfix" / "links.json", "w+") as outfile:
                    json.dump(
                        link_cache,
                        outfile,
                        indent=4,
                        sort_keys=True,
                        default=serialize_unknown,
                    )
                logger.info(" ➤ [ + ] Link added to JSON cache ")
                return True
            case "memory":
                link_cache[video_link] = vnf
                logger.info(" ➤ [ + ] Link added to memory cache ")
                return True
    except Exception as e:
        logger.error(" ➤ [ X ] Failed to add link to cache")
        logger.error(e)
        return False


@lru_cache(100)
def get_vnf_from_link_cache(video_link: str):
    video_link = video_link.lower()
    match link_cache_system:
        case "json":
            if video_link in link_cache:
                logger.info("Link located in json cache")
                return link_cache[video_link]
            else:
                logger.error(" ➤ [ X ] Link not in json cache")
                return None
        case "memory":  # FOR TESTS ONLY
            if video_link in link_cache:
                logger.info("Link located in json cache")
                vnf = link_cache[video_link]
                return vnf
            else:
                logger.error(" ➤ [ X ] Link not in cache")
                return None
        case _:
            return None


def clear_cache():
    if link_cache_system == "memory":
        link_cache = {}  # noqa


def set_cache(value):
    new_cache = {}
    for key in value:
        new_cache[key.lower()] = value[key]
    if link_cache_system == "memory":
        link_cache = new_cache  # noqa

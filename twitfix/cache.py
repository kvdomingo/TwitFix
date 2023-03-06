import json
from datetime import date, datetime

from loguru import logger

from twitfix.config_handler import config
from twitfix.constants import BASE_DIR


class Cache:
    def __init__(self):
        self.link_cache_system = config["config"]["link_cache"]
        if self.link_cache_system == "json":
            if not (path := BASE_DIR / "twitfix" / "links.json").exists():
                with open(path, "w+") as outfile:
                    default_link_cache = {}
                    json.dump(default_link_cache, outfile)
            with open(path, "r") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    @staticmethod
    def serialize_unknown(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    def add_vnf_to_link_cache(self, video_link, vnf):
        video_link = video_link.lower()
        try:
            match self.link_cache_system:
                case "json":
                    self.cache[video_link] = vnf
                    with open(BASE_DIR / "twitfix" / "links.json", "w+") as outfile:
                        json.dump(
                            self.cache,
                            outfile,
                            indent=4,
                            sort_keys=True,
                            default=self.serialize_unknown,
                        )
                    logger.info(" ➤ [ + ] Link added to JSON cache ")
                    return True
                case "memory":
                    self.cache[video_link] = vnf
                    logger.info(" ➤ [ + ] Link added to memory cache ")
        except Exception as e:
            logger.error(" ➤ [ X ] Failed to add link to cache")
            logger.error(e)
            return False

    def get_vnf_from_link_cache(self, video_link):
        video_link = video_link.lower()
        match self.link_cache_system:
            case "json":
                if video_link in self.cache.keys():
                    logger.info("Link located in json cache")
                    return self.cache[video_link]
                else:
                    logger.error(" ➤ [ X ] Link not in json cache")
                    return None
            case "memory":
                if (cached := self.cache.get(video_link)) is not None:
                    logger.info("Link located in json cache")
                    return cached
                else:
                    logger.error(" ➤ [ X ] Link not in cache")
                    return None
            case _:
                return None

    def clear_cache(self):
        if self.link_cache_system == "memory":
            self.cache.clear()

    def set_cache(self, value):
        for key, val in value.items():
            if self.link_cache_system == "memory":
                self.cache[key.lower()] = val


cache = Cache()

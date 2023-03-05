import json
from datetime import date, datetime

import boto3
import pymongo
from loguru import logger

from twitfix.config_handler import config
from twitfix.constants import BASE_DIR

link_cache_system = config["config"]["link_cache"]

link_cache = {}

DYNAMO_CACHE_TBL = None

match link_cache_system:
    case "json":
        if not (path := BASE_DIR / "twitfix" / "links.json").exists():
            with open(path, "w+") as outfile:
                default_link_cache = {}
                json.dump(default_link_cache, outfile)
        with open(path, "r") as f:
            link_cache = json.load(f)
    case "ram":
        logger.warning(
            "Your link_cache_system is set to 'ram' which is not recommended; this is only intended to be used for tests"
        )
    case "db":
        client = pymongo.MongoClient(config["config"]["database"], connect=False)
        table = config["config"]["table"]
        db = client[table]
    case "dynamodb":
        DYNAMO_CACHE_TBL = config["config"]["table"]
        client = boto3.resource("dynamodb")


def serialize_unknown(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def add_vnf_to_link_cache(video_link, vnf):
    video_link = video_link.lower()
    try:
        match link_cache_system:
            case "db":
                db.linkCache.update_one(vnf)
                logger.info(" ➤ [ + ] Link added to DB cache ")
                return True
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
            case "ram":  # FOR TESTS ONLY
                link_cache[video_link] = vnf
                logger.info(" ➤ [ + ] Link added to RAM cache ")
            case "dynamodb":
                vnf["ttl"] = int(vnf["ttl"].strftime("%s"))
                table = client.Table(DYNAMO_CACHE_TBL)
                table.put_item(
                    Item={"tweet": video_link, "vnf": vnf, "ttl": vnf["ttl"]}
                )
                logger.info(" ➤ [ + ] Link added to dynamodb cache ")
                return True
    except Exception as e:
        logger.error(" ➤ [ X ] Failed to add link to DB cache")
        logger.error(e)
        return False


def get_vnf_from_link_cache(video_link):
    video_link = video_link.lower()
    match link_cache_system:
        case "db":
            collection = db.linkCache
            vnf = collection.find_one({"tweet": video_link})
            if vnf is not None:
                hits = vnf["hits"] + 1
                logger.info(
                    " ➤ [ ✔ ] Link located in DB cache. "
                    + "hits on this link so far: ["
                    + str(hits)
                    + "]"
                )
                query = {"tweet": video_link}
                change = {"$set": {"hits": hits}}
                db.linkCache.update_one(query, change)
                return vnf
            else:
                logger.error(" ➤ [ X ] Link not in DB cache")
                return None
        case "json":
            if video_link in link_cache:
                logger.info("Link located in json cache")
                return link_cache[video_link]
            else:
                logger.error(" ➤ [ X ] Link not in json cache")
                return None
        case "dynamodb":
            table = client.Table(DYNAMO_CACHE_TBL)
            response = table.get_item(Key={"tweet": video_link})
            if "Item" in response:
                logger.info("Link located in dynamodb cache")
                vnf = response["Item"]["vnf"]
                return vnf
            else:
                logger.error(" ➤ [ X ] Link not in dynamodb cache")
                return None
        case "ram":  # FOR TESTS ONLY
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
    # only intended for use in tests
    if link_cache_system == "ram":
        link_cache = {}


def set_cache(value):
    new_cache = {}
    for key in value:
        new_cache[key.lower()] = value[key]
    # only intended for use in tests
    if link_cache_system == "ram":
        link_cache = new_cache

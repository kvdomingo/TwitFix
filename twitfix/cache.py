import json
import os
from datetime import date, datetime

import boto3
import pymongo

from twitfix.config_handler import config

link_cache_system = config["config"]["link_cache"]

link_cache = {}

DYNAMO_CACHE_TBL = None
if link_cache_system == "dynamodb":  # pragma: no cover
    DYNAMO_CACHE_TBL = config["config"]["table"]

if link_cache_system == "json":
    link_cache = {}
    if not os.path.exists("links.json"):
        with open("links.json", "w") as outfile:
            default_link_cache = {}
            json.dump(default_link_cache, outfile)
    try:
        f = open("links.json")
        link_cache = json.load(f)
    except json.decoder.JSONDecodeError:
        print(" ➤ [ X ] Failed to load cache JSON file. Creating new file.")
        link_cache = {}
    except FileNotFoundError:
        print(" ➤ [ X ] Failed to load cache JSON file. Creating new file.")
        link_cache = {}
    finally:
        f.close()
elif link_cache_system == "ram":
    link_cache = {}
    print(
        "Your link_cache_system is set to 'ram' which is not recommended; this is only intended to be used for tests"
    )
elif link_cache_system == "db":
    client = pymongo.MongoClient(config["config"]["database"], connect=False)
    table = config["config"]["table"]
    db = client[table]
elif link_cache_system == "dynamodb":  # pragma: no cover
    client = boto3.resource("dynamodb")


def serialize_unknown(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def add_vnf_to_link_cache(video_link, vnf):
    video_link = video_link.lower()
    global link_cache
    try:
        if link_cache_system == "db":
            db.linkCache.update_one(vnf)
            print(" ➤ [ + ] Link added to DB cache ")
            return True
        elif link_cache_system == "json":
            link_cache[video_link] = vnf
            with open("links.json", "w") as outfile:
                json.dump(
                    link_cache,
                    outfile,
                    indent=4,
                    sort_keys=True,
                    default=serialize_unknown,
                )
            print(" ➤ [ + ] Link added to JSON cache ")
            return True
        elif link_cache_system == "ram":  # FOR TESTS ONLY
            link_cache[video_link] = vnf
            print(" ➤ [ + ] Link added to RAM cache ")
        elif link_cache_system == "dynamodb":  # pragma: no cover
            vnf["ttl"] = int(vnf["ttl"].strftime("%s"))
            table = client.Table(DYNAMO_CACHE_TBL)
            table.put_item(Item={"tweet": video_link, "vnf": vnf, "ttl": vnf["ttl"]})
            print(" ➤ [ + ] Link added to dynamodb cache ")
            return True
    except Exception as e:
        print(" ➤ [ X ] Failed to add link to DB cache")
        print(e)
        return False


def get_vnf_from_link_cache(video_link):
    video_link = video_link.lower()
    global link_cache
    if link_cache_system == "db":
        collection = db.linkCache
        vnf = collection.find_one({"tweet": video_link})
        if vnf is not None:
            hits = vnf["hits"] + 1
            print(
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
            print(" ➤ [ X ] Link not in DB cache")
            return None
    elif link_cache_system == "json":
        if video_link in link_cache:
            print("Link located in json cache")
            vnf = link_cache[video_link]
            return vnf
        else:
            print(" ➤ [ X ] Link not in json cache")
            return None
    elif link_cache_system == "dynamodb":  # pragma: no cover
        table = client.Table(DYNAMO_CACHE_TBL)
        response = table.get_item(Key={"tweet": video_link})
        if "Item" in response:
            print("Link located in dynamodb cache")
            vnf = response["Item"]["vnf"]
            return vnf
        else:
            print(" ➤ [ X ] Link not in dynamodb cache")
            return None
    elif link_cache_system == "ram":  # FOR TESTS ONLY
        if video_link in link_cache:
            print("Link located in json cache")
            vnf = link_cache[video_link]
            return vnf
        else:
            print(" ➤ [ X ] Link not in cache")
            return None
    elif link_cache_system == "none":
        return None


def clear_cache():
    global link_cache
    # only intended for use in tests
    if link_cache_system == "ram":
        link_cache = {}


def set_cache(value):
    new_cache = {}
    for key in value:
        new_cache[key.lower()] = value[key]
    global link_cache
    # only intended for use in tests
    if link_cache_system == "ram":
        link_cache = new_cache

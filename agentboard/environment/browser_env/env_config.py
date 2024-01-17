# websites domain
import os

REDDIT = os.environ.get("REDDIT", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:9999")
SHOPPING = os.environ.get("SHOPPING", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770")
SHOPPING_ADMIN = os.environ.get("SHOPPING_ADMIN", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7780/admin")
GITLAB = os.environ.get("GITLAB", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:8023")
WIKIPEDIA = os.environ.get("WIKIPEDIA", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing")
MAP = os.environ.get("MAP", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:3000")
HOMEPAGE = os.environ.get("HOMEPAGE", "PASS")
PREFIX = os.environ.get("PREFIX", "http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com")

assert (
    REDDIT
    and SHOPPING
    and SHOPPING_ADMIN
    and GITLAB
    and WIKIPEDIA
    and MAP
    and HOMEPAGE
), (
    f"Please setup the URLs to each site. Current: \n"
    + f"Reddit: {REDDIT}\n"
    + f"Shopping: {SHOPPING}\n"
    + f"Shopping Admin: {SHOPPING_ADMIN}\n"
    + f"Gitlab: {GITLAB}\n"
    + f"Wikipedia: {WIKIPEDIA}\n"
    + f"Map: {MAP}\n"
    + f"Homepage: {HOMEPAGE}\n"
)

ACCOUNTS = {
    "reddit": {"username": "MarvelsGrantMan136", "password": "test1234"},
    "gitlab": {"username": "byteblaze", "password": "hello1234"},
    "shopping": {
        "username": "emma.lopez@gmail.com",
        "password": "Password.123",
    },
    "shopping_admin": {"username": "admin", "password": "admin1234"},
    "shopping_site_admin": {"username": "admin", "password": "admin1234"},
}

URL_MAPPINGS = {
    REDDIT: "http://reddit.com",
    SHOPPING: "http://onestopmarket.com",
    SHOPPING_ADMIN: "http://luma.com/admin",
    GITLAB: "http://gitlab.com",
    WIKIPEDIA: "http://wikipedia.org",
    MAP: "http://openstreetmap.org",
    HOMEPAGE: "http://homepage.com",
}


from googleapiclient.discovery import build
from urllib.parse import urlparse

API_KEY = "AIzaSyCGw26TZirurhgA0KtsO7as7a6kdcEgrAE"

youtube = build("youtube", "v3", developerKey=API_KEY)


def get_channel_id(url: str):
    """
    Hỗ trợ:
    - https://www.youtube.com/channel/UCxxx
    - https://www.youtube.com/@username
    - https://www.youtube.com/c/customname
    - https://www.youtube.com/user/oldname
    - Link video bất kỳ
    """

    if not url:
        return None

    url = url.strip()

    # 1️⃣ Dạng /channel/UCxxxx
    if "/channel/" in url:
        return url.split("/channel/")[1].split("/")[0]

    # Parse URL
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # 2️⃣ Dạng @username
    if path.startswith("@"):
        query = path.replace("@", "")
    # 3️⃣ /c/xxx hoặc /user/xxx
    elif path.startswith("c/") or path.startswith("user/"):
        query = path.split("/", 1)[1]
    # 4️⃣ Link video → search ngược
    else:
        query = url

    # Search channel
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=1
    )
    response = request.execute()

    items = response.get("items", [])
    if items:
        return items[0]["snippet"]["channelId"]

    return None


def get_channel_info(channel_id: str):
    if not channel_id:
        return None

    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()

    items = response.get("items", [])
    if not items:
        return None

    item = items[0]
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})

    return {
        "Channel Name": snippet.get("title", ""),
        "Subscribers": int(stats.get("subscriberCount", 0)),
        "Total Views": int(stats.get("viewCount", 0)),
        "Video Count": int(stats.get("videoCount", 0)),
        "Channel ID": channel_id,
        "Channel URL": f"https://www.youtube.com/channel/{channel_id}"
    }



# from googleapiclient.discovery import build

# API_KEY = "AIzaSyCGw26TZirurhgA0KtsO7as7a6kdcEgrAE"

# youtube = build("youtube", "v3", developerKey=API_KEY)

# def get_channel_id(url):
#     if "channel/" in url:
#         return url.split("channel/")[1].split("/")[0]

#     request = youtube.search().list(
#         part="snippet",
#         q=url,
#         type="channel",
#         maxResults=1
#     )
#     response = request.execute()

#     if response["items"]:
#         return response["items"][0]["snippet"]["channelId"]

#     return None


# def get_channel_info(channel_id):
#     request = youtube.channels().list(
#         part="snippet,statistics",
#         id=channel_id
#     )
#     response = request.execute()

#     if not response["items"]:
#         return None

#     item = response["items"][0]

#     return {
#         "Channel Name": item["snippet"]["title"],
#         "Subscribers": int(item["statistics"].get("subscriberCount", 0)),
#         "Total Views": int(item["statistics"].get("viewCount", 0)),
#         "Video Count": int(item["statistics"].get("videoCount", 0)),
#         "Channel ID": channel_id,
#         "Channel URL": f"https://www.youtube.com/channel/{channel_id}"
#     }

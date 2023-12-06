import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()

DATABASE_ID = os.getenv("NOTION_DB_ID")
headers = {
    "Authorization": "Bearer " + os.getenv("NOTION_API_KEY"),
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # Comment this out to dump all data to a file
    # with open("db.json", "w", encoding="utf8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]

    # while data["has_more"] and get_all:
    #     payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
    #     url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    #     response = requests.post(url, json=payload, headers=headers)
    #     data = response.json()
    #     results.extend(data["results"])

    return results


def create_page(data: dict):
    url = f"https://api.notion.com/v1/pages/"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}

    res = requests.post(url, json=payload, headers=headers)
    return res

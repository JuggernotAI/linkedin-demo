import openai
import streamlit as st
import requests
import time
from PIL import Image
from dotenv import load_dotenv
import os
import notion_helper
from datetime import datetime, timezone
import json
from utilities import initialise_state_vars


# State Variables
st.session_state.file_id_list, st.session_state.start_chat, st.session_state.thread_id, st.session_state.messages, st.session_state.image_count_temp, st.session_state.image_paths,st.session_state.image_count = initialise_state_vars()

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
client=openai

def generate_image(prompt, size="1024x1024"):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=1,
        quality="standard",
    )
    path = os.path.join("./dalle", str(round(time.time() * 1000)) + ".png")
    image_url = response.data[0].url
    Image.open(requests.get(image_url, stream=True).raw).save(path)
    st.session_state.image_paths.append(path)
    st.session_state.image_count += 1
    return image_url


def post_on_twitter(twitter_post, pic=None):
    url = "https://replyrocket-backend.onrender.com/twitter/post"
    data = {"text": twitter_post}
    try:
        if pic is not None:
            with open(pic, "rb") as file:
                files = {"image": file}
                response = requests.post(url, files=files, data=data, timeout=10000)
                if response.status_code == 200:
                    return "Post successful!"
                else:
                    return f"Failed to post. Status code: {response.status_code}"
        else:
            response = requests.post(url, data=data, timeout=10000)
            if response.status_code == 200:
                return "Post successful!"
            else:
                return f"Failed to post. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def post_on_linkedin(text, pic=None):
    body = {
        "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN"),
        "linkedin_id": os.getenv("LINKEDIN_ID"),
        "content": text,
    }

    url = "https://replyrocket-flask.onrender.com/upload"

    try:
        if pic is None:
            response = requests.post(url, data=body, timeout=10000)
            if response.status_code == 200:
                return "Post successful!"
            else:
                return f"Failed to post. Status code: {response.status_code}"
        else:
            with open(pic, "rb") as file:
                files = {"file": file}
                response = requests.post(url, files=files, data=body, timeout=10000)
                if response.status_code == 200:
                    return "Post successful!"
                else:
                    return f"Failed to post. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def make_post(linkedin_post, twitter_post, pic=None):
    linkedin_data = post_on_linkedin(linkedin_post, pic)
    twitter_data = post_on_twitter(twitter_post, pic)
    return linkedin_data + "\n" + twitter_data


def add_to_notion(
    linkedin_post=None,
    linkedin_post_date=None,
    twitter_post=None,
    twitter_post_date=None,
    pic=None,
):
    data = {
        "copy": {
            "title": [
                {
                    "text": {"content": ""},
                }
            ]
        },
        "image": {
            "rich_text": [
                {
                    "text": {"content": ""},
                }
            ]
        },
        "created_at": {
            "date": {
                "start": datetime.now(timezone.utc).date().isoformat(),
                "end": None,
            }
        },
        "post_date": {
            "date": {
                "start": "",
                "end": None,
            }
        },
        "status": {
            "select": {
                "name": "Not Published",
            }
        },
        "platform": {
            "select": {
                "name": "",
            }
        },
    }
    res = ""
    datetime_format = "%B %d, %Y"
    if pic is not None:
        data["image"]["rich_text"][0]["text"]["content"] = pic
    if linkedin_post is not None:
        data["copy"]["title"][0]["text"]["content"] = linkedin_post
        data["platform"]["select"]["name"] = "Linkedin"
        dt = datetime.strptime(linkedin_post_date, datetime_format)
        formatted_date = dt.date().isoformat()
        print(formatted_date)
        data["post_date"]["date"]["start"] = formatted_date
        res = notion_helper.create_page(data)
    if twitter_post is not None:
        data["copy"]["title"][0]["text"]["content"] = twitter_post
        data["platform"]["select"]["name"] = "Twitter"
        dt = datetime.strptime(twitter_post_date, datetime_format)
        formatted_date = dt.date().isoformat()
        print(formatted_date)
        data["post_date"]["date"]["start"] = formatted_date
        res = notion_helper.create_page(data)

    return res
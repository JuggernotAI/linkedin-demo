# Import necessary libraries
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
from function_calls import generate_image, post_on_linkedin, post_on_twitter, make_post, add_to_notion
from instructions import instruction
print(instruction)


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_DEMO")

client = openai

def process_message_with_citations(message):
    return message.content[0].text.value

def create_thread():
    thread = client.beta.threads.create()
    return thread

def get_response_openai(prompt):
    # Add the user's message to the existing thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=prompt
    )
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
        instructions=instruction,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "generate image by Dall-e 3",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The prompt to generate image",
                            },
                            "size": {
                                "type": "string",
                                "enum": ["1024x1024", "other_sizes"],
                            },
                        },
                        "required": ["prompt"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "make_post",
                    "description": "make a post to linkedin",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "linkedin_post": {
                                "type": "string",
                                "description": "The linkedin post text content",
                            },
                            "twitter_post": {
                                "type": "string",
                                "description": "The twitter post text content",
                            },
                            "image": {
                                "type": "string",
                                "description": "Image URL of the post generated by generate_image function",
                            },
                        },
                        "required": ["linkedin_post", "twitter_post"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_notion",
                    "description": "add data to notion",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "linkedin_post": {
                                "type": "string",
                                "description": "The linkedin post text content",
                            },
                            "linkedin_post_date": {
                                "type": "string",
                                "description": "date to post the content on linkedin in the format 'December 4, 2023'",
                            },
                            "twitter_post": {
                                "type": "string",
                                "description": "The twitter post text content",
                            },
                            "twitter_post_date": {
                                "type": "string",
                                "description": "date to post the content on twitter in the format 'December 4, 2023'",
                            },
                            "image": {
                                "type": "string",
                                "description": "Image URL of the post generated by generate_image function",
                            },
                        },
                        "required": [
                            "linkedin_post",
                            "linkedin_post_date",
                            "twitter_post",
                            "twitter_post_date",
                        ],
                    },
                },
            },
        ],
    )
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id, run_id=run.id
        )
        if run.status == "requires_action":
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            if tool_call.function.name == "generate_image":
                print("image generation initiated...")
                prompt = (
                    json.loads(tool_call.function.arguments)["prompt"]
                    + ". make sure that you do not generate images with texts in it."
                )
                image_url = generate_image(prompt)
                try:
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {"tool_call_id": tool_call.id, "output": image_url}
                        ],
                    )
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": e}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(e)
            elif tool_call.function.name == "make_post":
                print("make post initiated...")
                linkedin_post = json.loads(tool_call.function.arguments).get(
                    "linkedin_post", None
                )
                twitter_post = json.loads(tool_call.function.arguments).get(
                    "twitter_post", None
                )
                pic = json.loads(tool_call.function.arguments).get("image", None)
                data = ""
                if pic != None:
                    path = os.path.join(
                        "./dalle", str(round(time.time() * 1000)) + ".png"
                    )
                    Image.open(
                        requests.get(pic, stream=True, timeout=10000).raw
                    ).save(path)
                    data = make_post(linkedin_post, twitter_post, path)
                else:
                    data = make_post(linkedin_post, twitter_post)
                try:
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {"tool_call_id": tool_call.id, "output": data}
                        ],
                    )
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": e}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(e)
            elif tool_call.function.name == "add_to_notion":
                print("add to notion initiated...")
                linkedin_post = json.loads(tool_call.function.arguments).get(
                    "linkedin_post", None
                )
                twitter_post = json.loads(tool_call.function.arguments).get(
                    "twitter_post", None
                )
                twitter_post_date = json.loads(tool_call.function.arguments).get(
                    "twitter_post_date", None
                )
                linkedin_post_date = json.loads(tool_call.function.arguments).get(
                    "linkedin_post_date", None
                )
                pic = json.loads(tool_call.function.arguments).get("image", None)
                data = ""
                if pic is not None:
                    path = os.path.join(
                        "./dalle", str(round(time.time() * 1000)) + ".png"
                    )
                    Image.open(
                        requests.get(pic, stream=True, timeout=10000).raw
                    ).save(path)

                    data = add_to_notion(
                        linkedin_post,
                        linkedin_post_date,
                        twitter_post,
                        twitter_post_date,
                        path,
                    )
                else:
                    data = add_to_notion(
                        linkedin_post,
                        linkedin_post_date,
                        twitter_post,
                        twitter_post_date,
                    )
                try:
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {"tool_call_id": tool_call.id, "output": data}
                        ],
                    )
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": e}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(e)

    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    for message in [
        m for m in messages if m.run_id == run.id and m.role == "assistant"
    ]:
        full_response = process_message_with_citations(message)
    return full_response
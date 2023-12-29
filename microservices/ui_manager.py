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
from openai_service import create_thread, get_response_openai

# State Variables
st.session_state.file_id_list, st.session_state.start_chat, st.session_state.thread_id, st.session_state.messages, st.session_state.image_count_temp, st.session_state.image_paths,st.session_state.image_count = initialise_state_vars()

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="Content Generator", page_icon=":speech_balloon:")

# Start Chat Button
if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = create_thread()
    st.session_state.thread_id = thread.id
    st.write("Thread ID: ", thread.id)

# Main chat interface setup
st.title("Agent Baani")
st.write(
    """As an AI copilot  for making posts on Social Media, I will assist you with making an engaging copy.

*Made By Juggernot.ai* """
)

# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image_count_temp" not in st.session_state:
        st.session_state.image_count_temp = 0
    if "image_paths" not in st.session_state:
        st.session_state.image_paths = []
    if "image_count" not in st.session_state:
        st.session_state.image_count = 0

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"])
            if "content" in message:
                st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("What is up?"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            full_response = get_response_openai(prompt)
            if st.session_state.image_count > st.session_state.image_count_temp:
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "image": st.session_state.image_paths[-1],
                    }
                )
                with st.chat_message("assistant"):
                    st.image(st.session_state.image_paths[-1])
                st.session_state.image_count_temp += 1
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)
else:
    st.write("Please click 'Start Chat' to begin the conversation.")

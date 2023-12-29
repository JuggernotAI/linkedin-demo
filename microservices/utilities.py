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

load_dotenv()

def initialise_state_vars():
    if "file_id_list" not in st.session_state:
        st.session_state.file_id_list = []
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image_count_temp" not in st.session_state:
        st.session_state.image_count_temp = 0
    if "image_paths" not in st.session_state:
        st.session_state.image_paths = []
    if "image_count" not in st.session_state:
        st.session_state.image_count = 0
    return st.session_state.file_id_list, st.session_state.start_chat, st.session_state.thread_id, st.session_state.messages, st.session_state.image_count_temp, st.session_state.image_paths,st.session_state.image_count 
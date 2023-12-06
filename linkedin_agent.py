# Import necessary libraries
import openai
import streamlit as st
import requests
import time
from dotenv import load_dotenv
import os
import re
import notion_helper
import json
from datetime import datetime, timezone

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
# Set your OpenAI Assistant ID here
assistant_id = os.getenv("OPENAI_LINKEDIN_ASSISTANT_ID")
instruction = """As a 'LinkedIn Content Specialist' for AgentGPT, your primary responsibility is to generate three distinct, long-form LinkedIn post variants for each user request. These posts should be detailed and expansive, maximizing the 3000-character limit of LinkedIn to provide comprehensive and engaging content. Your creations will reflect professional standards suitable for LinkedIn, covering a wide range of themes as per user input, like business insights, industry news, thought leadership, career advice, or inspirational stories.

Once you receive a user's input, you will create three diverse post options, ensuring each is extensive and detailed, similar to the provided examples. These posts will be presented in double quotes for clarity and professionalism.

After a user selects a post, you will return their chosen option, also enclosed in double quotes, matching their preferences and the comprehensive style of the examples given. Your adaptability to each user's specific needs is vital, aiming to deliver optimal, LinkedIn-specific content that maximizes user engagement and satisfaction on the platform."""

client = openai
# Initialize session state variables for file IDs and chat control
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="Linkedin Content Creator", page_icon=":speech_balloon:")


def extract_text(text):
    matches = re.findall(r'"([^"]*)"', text)
    if matches:
        st.session_state.extracted_text = matches[0]  # First occurrence
        print("Extracted text:", st.session_state.extracted_text)
    else:
        print("No text found within double quotes.")


def post_linkedin():
    url = "https://replyrocket-flask.onrender.com/post"
    data = {
        "access_token": "AQUOSL3LqJf3EEVLrv6mE1OEDNG17AUx8urUKiy9krA86_AL4Sioi1yFV8VEW9BULrkd65lMasSy_I7h2YoFeb876Hl0HCB0PGOPqd0JxzRIe_JtcSJIQkH87Wx9yVFQU48bUIT3-7WBeQ5A4_Q2AUS3SxmWZ_nnBtecjACrT0MSMLzKXW3hJqk7EoEkm0vSeC3WVkpOkrHinNix2mYJ415mabBMMdSWDvb2u3hqsEpWdP2Jrmd6g2KiJ_v_lHEO5mNgdob8LdfnISPdqJsIjNRjiJ_urxdiU9hwLRIAflJm4TPlK2lRKX_nAXPjQ8ycS1DYKTJSKi61Bi6LL68CXVZFqOn3Uw",
        "linkedin_id": "kFeIRZdelq",
        "content": "Remote Work: Embracing the Future of Work-Life Balance and Productivity\n\nThe landscape of work has undergone a remarkable transformation in recent years, with remote work emerging as a predominant trend reshaping the traditional 9-5 office dynamic. As we navigate through this paradigm shift, it's crucial to recognize the multifaceted impact of remote work on individuals, organizations, and the broader economy.\n\nFirst and foremost, remote work has redefined the work-life balance for professionals across industries. By eliminating the daily commute and offering a more flexible schedule, remote work enables employees to reclaim valuable time that would have otherwise been spent traveling to and from the office. This newfound flexibility not only enhances personal well-being but also allows individuals to allocate more time to their families, hobbies, and other non-work-related pursuits. As a result, remote work fosters a more harmonious integration of professional and personal life, contributing to improved overall job satisfaction and mental health.\n\nFrom an organizational standpoint, the benefits of remote work are equally compelling. Companies have experienced significant cost savings by scaling down their physical office spaces and adopting remote-friendly policies. Moreover, remote work has broadened the talent pool, enabling organizations to recruit top-tier professionals regardless of geographical constraints. This diversity in talent not only enriches the workforce but also brings forth a spectrum of fresh perspectives and innovative ideas, ultimately propelling businesses towards greater success.\n\nDespite these advantages, it's important to acknowledge the challenges associated with remote work, such as maintaining team cohesiveness, combating feelings of isolation, and establishing effective communication channels. As we continue to embrace remote work, it remains imperative for organizations to invest in robust virtual collaboration tools, prioritize regular team check-ins, and cultivate a supportive remote work culture.\n\nIn conclusion, remote work represents a pivotal evolution in the way we approach work, offering unparalleled flexibility, cost-efficiency, and access to a global talent pool. As professionals and organizations adapt to this new paradigm, it's essential to harness the opportunities presented by remote work while proactively addressing its inherent challenges. By doing so, we can usher in an era where work thrives beyond the confines of traditional offices, empowering individuals to achieve a harmonious blend of professional achievement and personal fulfillment.",
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return "Post successful!"
        else:
            return f"Failed to post. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Button to start the chat session
if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    # Create a thread once and store its ID in session state
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.write("thread id: ", thread.id)
    # else:
    #     st.sidebar.warning("Please upload at least one file to start the chat.")


# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    # Add footnotes to the end of the message content
    full_response = message_content.value
    return full_response


# Main chat interface setup
st.title("Linkedin Content Creator")
st.write("I can create your posts and content for you")

# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("What is up?"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if prompt.startswith("!post"):
            res = post_linkedin()
            st.session_state.messages.append({"role": "assistant", "content": res})
            with st.chat_message("assistant"):
                st.markdown(res)
        elif prompt.startswith("!delete"):
            pages = notion_helper.get_pages()
            data = []
            for page in pages:
                page_id = page["id"]
                props = page["properties"]
                copy = props["copy"]["title"][0]["text"]["content"]
                image = props["image"]["rich_text"][0]["text"]["content"]
                created_at = props["created_at"]["date"]["start"]
                post_date = props["post_date"]["date"]["start"]
                status = props["status"]["select"]["name"]
                platform = props["platform"]["multi_select"][0]["name"]
                data.append(
                    {
                        "id": page_id,
                        "copy": copy,
                        "image": image,
                        "created_at": created_at,
                        "post_date": post_date,
                        "status": status,
                        "platform": platform,
                    }
                )
            st.markdown(json.dumps(data, indent=4))
        elif prompt.startswith("!database"):
            data = {
                "copy": {
                    "title": [
                        {
                            "text": {"content": "tweet 3.0"},
                        }
                    ]
                },
                "image": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "https://media.wired.com/photos/5b899992404e112d2df1e94e/master/pass/trash2-01.jpg"
                            },
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
                        "start": datetime.now(timezone.utc).date().isoformat(),
                        "end": None,
                    }
                },
                "status": {
                    "select": {
                        "name": "Not Published",
                    }
                },
                "platform": {
                    "multi_select": [
                        {
                            "name": "Twitter",
                        }
                    ]
                },
            }
            notion_helper.create_page(data)
            st.markdown("added")
        else:
            # Add the user's message to the existing thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id, role="user", content=prompt
            )

            # Create a run with additional instructions
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions=instruction,
            )

            # Poll for the run to complete and retrieve the assistant's messages
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )

            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                full_response = process_message_with_citations(message)
                extract_text(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)
else:
    st.write("Please click 'Start Chat' to begin the conversation.")

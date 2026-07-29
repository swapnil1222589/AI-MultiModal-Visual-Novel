import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import requests
from PIL import Image
from io import BytesIO
from gtts import gTTS
from urllib.parse import quote

load_dotenv()

# -----------------------------
# CACHE GEMINI
# -----------------------------

@st.cache_resource
def load_model():
    genai.configure(api_key=os.getenv("AIzaSyDvoEdPHPrLD3NqA74M-8aJwBems4tEvpU"))
    return genai.GenerativeModel("gemini-2.5-flash")

model = load_model()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🎮 Story Settings")

genre = st.sidebar.selectbox(
    "Story Genre",
    [
        "Fantasy",
        "Sci-Fi",
        "Mystery",
        "Horror",
        "Cyberpunk",
        "Adventure"
    ]
)

art = st.sidebar.selectbox(
    "Art Style",
    [
        "Anime",
        "Pixar",
        "Realistic",
        "Comic",
        "Oil Painting",
        "Fantasy Art"
    ]
)

# -----------------------------
# SESSION STATE
# -----------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "started" not in st.session_state:
    st.session_state.started = False

# -----------------------------
# SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = f"""
You are a Visual Novel AI.

Genre:
{genre}

Art Style:
{art}

Always reply ONLY in JSON.

Format:

{{
"story_text":"...",
"image_prompt":"...",
"options":[
"Choice 1",
"Choice 2",
"Choice 3"
]
}}

No markdown.
No explanation.
"""

# -----------------------------
# AI FUNCTION
# -----------------------------

def ask_ai(user_input):

    prompt = SYSTEM_PROMPT + "\nPlayer: " + user_input

    response = model.generate_content(prompt)

    text = response.text

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)

# -----------------------------
# IMAGE
# -----------------------------

def generate_image(prompt):

    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"

    r = requests.get(url, timeout=30)

    return Image.open(BytesIO(r.content))

# -----------------------------
# TTS
# -----------------------------

def speak(text):

    tts = gTTS(text)

    filename = "generated_audio.mp3"

    tts.save(filename)

    return filename

# -----------------------------
# STORY
# -----------------------------

st.title("🎮 AI Multi-Modal Visual Novel")

if not st.session_state.started:

    if st.button("Start Story"):

        st.session_state.started = True

        data = ask_ai("Begin the story")

        st.session_state.history.append(data)

# -----------------------------
# DISPLAY
# -----------------------------

if st.session_state.started:

    latest = st.session_state.history[-1]

    st.subheader("📖 Story")

    st.write(latest["story_text"])

    # IMAGE

    try:

        img = generate_image(latest["image_prompt"])

        st.image(img, use_container_width=True)

    except:

        st.toast("Image server busy. Skipping visual...")

    # AUDIO

    audio = speak(latest["story_text"])

    st.audio(audio)

    st.divider()

    st.subheader("Choose your action")

    for option in latest["options"]:

        if st.button(option):

            try:

                data = ask_ai(option)

                st.session_state.history.append(data)

                st.rerun()

            except Exception as e:

                st.error(e)

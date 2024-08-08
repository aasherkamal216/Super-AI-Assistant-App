import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_vertical_slider import vertical_slider
from streamlit_lottie import st_lottie
import json
from PIL import Image
from io import BytesIO
import base64
from utils import visualize_display_page
import google.generativeai as genai
from langchain_groq import ChatGroq
import os , random
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Super GPT",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Super GPT Assistant")

google_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

groq_models = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]


@st.cache_data
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

def get_llm_info(available_models):
    with st.sidebar:
        tip =tip = "Select Gemini models if you require multi-modal capabilities (text, image, audio and video inputs)"
        model = st.selectbox("Choose LLM:", available_models, help=tip)

        model_type = None
        if model.startswith(("llama", "gemma", "mixtral")): model_type = "groq"
        elif model.startswith("gemini"): model_type = "google"

        with st.popover("⚙️Model Parameters", use_container_width=True):
            temp = st.slider("Temperature:", min_value=0.0,
                                            max_value=2.0, value=0.5, step=0.5)
            
            max_tokens = st.slider("Maximum Tokens:", min_value=100,
                                        max_value=2000, value=400, step=200)
    return model, model_type, temp, max_tokens

def messages_to_gemini(messages):
    gemini_messages = []
    prev_role = None
    for message in messages:
        if prev_role and (prev_role == message["role"]):
            gemini_message = gemini_messages[-1]
        else:
            gemini_message = {
                "role": "model" if message["role"] == "assistant" else "user",
                "parts": [],
            }

        for content in message["content"]:
            if content["type"] == "text":
                gemini_message["parts"].append(content["text"])
            elif content["type"] == "image_url":
                gemini_message["parts"].append(base64_to_image(content["image_url"]["url"]))
            elif content["type"] == "video_file":
                gemini_message["parts"].append(genai.upload_file(content["video_file"]))
            elif content["type"] == "audio_file":
                gemini_message["parts"].append(genai.upload_file(content["audio_file"]))

        if prev_role != message["role"]:
            gemini_messages.append(gemini_message)

        prev_role = message["role"]
        
    return gemini_messages

# Function to convert file to base64
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode('utf-8')


def add_media_files_to_messages():
    if st.session_state.uploaded_file:
        file_type = st.session_state.uploaded_file.type
        file_content = st.session_state.uploaded_file.getvalue()
        
        if file_type.startswith("image"):
            img = base64.b64encode(file_content).decode()
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "image_url",
                        "image_url": {"url": f"data:{file_type};base64,{img}"}
                    }]
                }
            )
        elif file_type == "video/mp4":
            video_base64 = base64.b64encode(file_content).decode()
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "video_file",
                        "video_file": f"data:{file_type};base64,{video_base64}",
                    }]
                }
            )
        elif file_type.startswith("audio"):
            audio_base64 = base64.b64encode(file_content).decode()
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "audio_file",
                        "audio_file": f"data:{file_type};base64,{audio_base64}",
                    }]
                }
            )


def add_camera_img_to_messages():
    if "camera_img" in st.session_state and st.session_state.camera_img:
        img = base64.b64encode(st.session_state.camera_img.getvalue()).decode()
        st.session_state.messages.append(
            {
                "role": "user", 
                "content": [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                }]
            }
        )



with st.sidebar:
    st.logo("logo.png")
    api_cols = st.columns(2)
    with api_cols[0]:
        default_groq_api_key = os.getenv("GROQ_API_KEY") if os.getenv("GROQ_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        with st.popover("🔐 Groq", use_container_width=True):
            groq_api_key = st.text_input("Get your Groq API Key (https://console.groq.com/keys)", value=default_groq_api_key, type="password")
    
    with api_cols[1]:
        default_google_api_key = os.getenv("GOOGLE_API_KEY") if os.getenv("GOOGLE_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        with st.popover("🔐 Google", use_container_width=True):
            google_api_key = st.text_input("Get your Google API Key (https://aistudio.google.com/app/apikey)", value=default_google_api_key, type="password")
    

if (groq_api_key == "" or groq_api_key is None or "gsk" not in groq_api_key) and (google_api_key == "" or google_api_key is None or "AIza" not in google_api_key):
    st.warning("Please Add an API Key to proceed.")

else:
    col1, col2 = st.columns([1,6])

    with col1:

        audio_bytes = audio_recorder("Speak",
                                     neutral_color="#728796",
                                     recording_color="#f81f6f",
                                     icon_name="microphone-lines",
                                     icon_size="3x")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Handle speech input
    if "prev_speech_hash" not in st.session_state:
        st.session_state.prev_speech_hash = None

    if audio_bytes and st.session_state.prev_speech_hash != hash(audio_bytes):
        st.session_state.prev_speech_hash = hash(audio_bytes)
        speech_base64 = base64.b64encode(audio_bytes).decode()
        st.session_state.messages.append(
            {
                "role": "user",
                "content": [{
                    "type": "speech_input",
                    "speech_input": f"data:audio/wav;base64,{speech_base64}",
                }]
            }
        )

    for message in st.session_state.messages:
        with col2:
            with st.chat_message(message["role"]):
                for content in message["content"]:
                    if content["type"] == "text":
                        st.markdown(content["text"])
                    elif content["type"] == "image_url":      
                        st.image(content["image_url"]["url"], use_column_width=True)
                    elif content["type"] == "video_file":
                        st.video(content["video_file"])
                    elif content["type"] == "audio_file":
                        st.audio(content["audio_file"], autoplay=True)
                    elif content["type"] == "speech_input":
                        st.audio(content["speech_input"])

    with st.sidebar:
        st.divider()
        columns = st.columns(2)
        # animation
        with columns[0]:
            lottie_animation = load_lottie_file("animation.json")
            if lottie_animation:
                st_lottie(lottie_animation, height=100, width=100, quality="high", key="lottie_anim")

        with columns[1]:
            if st.toggle("Voice Response"):
                response_lang = st.selectbox("Available Voices:", options=["Alex","Ana","Daniel"], key="voice_response")
        
        available_models = []  + (google_models if google_api_key else []) + (groq_models if groq_api_key else [])
        model, model_type, temperature, max_tokens = get_llm_info(available_models)
        st.divider()

        if model_type == "google":
            st.write("Upload a file or take a picture")

            media_cols = st.columns(2)

            with media_cols[0]:
                with st.popover("📁 Upload", use_container_width=True):
                    st.file_uploader(
                        "Upload an image, audio or a video", 
                        type=["png", "jpg", "jpeg", "wav", "mp3", "mp4"], 
                        accept_multiple_files=False,
                        key="uploaded_file",
                        on_change=add_media_files_to_messages,
                    )

            with media_cols[1]:                    
                with st.popover("📷 Camera", use_container_width=True):
                    activate_camera = st.checkbox("Activate camera")
                    if activate_camera:
                        st.camera_input(
                            "Take a picture", 
                            key="camera_img",
                            on_change=add_camera_img_to_messages,
                        )
    
        
        
        
        
        
        
        
        else:
            pass





    # temperature = vertical_slider(
    #     label = "Temperature",  #Optional
    #     key = "vert_01" ,
    #     height = 100, #Optional - Defaults to 300#Optional - Defaults to "circle"
    #     step = 1, #Optional - Defaults to 1
    #     default_value=5,#Optional - Defaults to 0
    #     min_value= 0, # Defaults to 0
    #     max_value= 10, # Defaults to 10
    #     track_color = "blue",
    #     thumb_shape="square", #Optional - Defaults to #D3D3D3
    #     slider_color = 'lighgray', #Optional - Defaults to #29B5E8
    #     thumb_color= "orange", #Optional - Defaults to #11567f
    #     value_always_visible = False ,#Optional - Defaults to False
    # )


                                



if prompt:= st.chat_input("Type you question", key="question"):

    with col2:
        st.session_state.messages.append(
                    {
                        "role": "user", 
                        "content": [{
                            "type": "text",
                            "text": prompt,
                        }]
                    }
                )
        st.chat_message("user").markdown(prompt)
# Confirmation popup window
# selection_dict = {"file_and_answer": "", "prompt": "", "respuesta_chat": ""}
# st.button("Visualize", on_click=visualize_display_page, key="visualiza", args=[selection_dict])




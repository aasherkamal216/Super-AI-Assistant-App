import streamlit as st
from audio_recorder_streamlit import audio_recorder
from PIL import Image
from io import BytesIO
import base64
from streamlit_lottie import st_lottie
import json
from utils import set_safety_settings, about, extract_all_pages_as_images
import google.generativeai as genai
import os, random, time
import tempfile
import asyncio
import edge_tts
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Super GPT",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": about(), "Get Help":"https://www.linkedin.com/in/aasher-kamal-a227a124b/"},
)

###--- Title ---###
st.markdown("""
    <h1 style='text-align: center;'>
        <span style='color: #F81F6F;'>Super</span> 
        <span style='color: #f5f8fc;'>GPT Assistant</span>
    </h1>
""", unsafe_allow_html=True)


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

voices = {
    "William":"en-AU-WilliamNeural",
    "James":"en-PH-JamesNeural",
    "Jenny":"en-US-JennyNeural",
    "US Guy":"en-US-GuyNeural",
    "Sawara":"hi-IN-SwaraNeural",
}

@st.cache_data
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        await communicate.save(temp_file.name)
        temp_file_path = temp_file.name
    return temp_file_path


def get_audio_player(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'

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


###--- Function to convert base64 to temp file ---###
def base64_to_temp_file(base64_string, unique_name, file_extension):
    base64_string = base64_string.split(",")[1]
    file_bytes = BytesIO(base64.b64decode(base64_string))
    temp_file_path = f"{unique_name}.{file_extension}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_bytes.read())
        time.sleep(1) 
    return temp_file_path


def messages_to_gemini(messages):
    gemini_messages = []
    prev_role = None
    uploaded_files = set([file.display_name.split(".")[0] for file in genai.list_files()])

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

            elif content["type"] in ["video_file", "audio_file"]:
                file_name = content['unique_name']

                if file_name not in uploaded_files:
                    temp_file_path = base64_to_temp_file(content[content["type"]], file_name, "mp4" if content["type"] == "video_file" else "wav")
                    for attempt in range(3):
                        try:
                            with st.spinner(f"Sending {content['type'].replace('_', ' ')} to Gemini..."):
                                gemini_message["parts"].append(genai.upload_file(path=temp_file_path))
                            break 

                        except FailedPrecondition as e:
                            if attempt < max_retries - 1:
                                st.warning("Retrying file upload...")
                                time.sleep(1)  # Brief delay before retrying
                            else:
                                st.error("Failed to upload file after several attempts.")
                                raise e
                    os.remove(temp_file_path)

            elif content["type"] == "pdf_file":
                if content['pdf_file'].split(".")[0] not in uploaded_files:
                    with st.spinner("Sending your PDF to Gemini..."):
                        gemini_message["parts"].append(genai.upload_file(path=content['pdf_file']))
                    os.remove(content['pdf_file'])


            elif content["type"] == "speech_input":
                file_name = content['unique_name']
                if file_name not in uploaded_files:
                    temp_file_path = base64_to_temp_file(content["speech_input"], file_name, "wav")

                    with st.spinner("Sending your speech to Gemini..."):
                        gemini_message["parts"].append(genai.upload_file(path=temp_file_path))
                    os.remove(temp_file_path)

        if prev_role != message["role"]:
            gemini_messages.append(gemini_message)

        prev_role = message["role"]

    return gemini_messages


##-- Converting base64 to image ---##
def base64_to_image(base64_string):
    base64_string = base64_string.split(",")[1]
    
    return Image.open(BytesIO(base64.b64decode(base64_string)))

def add_pdf_file_to_messages():
    if st.session_state.pdf_uploaded:
        # Save the PDF file
        pdf_id = random.randint(1000, 9999)
        pdf_filename = f"pdf_{pdf_id}.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(st.session_state.pdf_uploaded.read())
        
        # Add the PDF file to session_state messages
        st.session_state.messages.append(
            {
                "role": "user", 
                "content": [{
                    "type": "pdf_file",
                    "pdf_file": pdf_filename,
                }]
            }
        )


##--- Function for adding media files to session_state messages ---###
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
            unique_id = random.randint(1000, 9999)
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "video_file",
                        "video_file": f"data:{file_type};base64,{video_base64}",
                        "unique_name": f"temp_{unique_id}"
                    }]
                }
            )
        elif file_type.startswith("audio"):
            audio_base64 = base64.b64encode(file_content).decode()
            unique_id = random.randint(1000, 9999)
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "audio_file",
                        "audio_file": f"data:{file_type};base64,{audio_base64}",
                        "unique_name": f"temp_{unique_id}"
                    }]
                }
            )

###--- FUNCTION TO ADD CAMERA IMAGE TO MESSAGES ---##
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

##--- FUNCTION TO RESET CONVERSATION ---##
def reset_conversation():
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.session_state.pop("messages", None)

    for file in genai.list_files():
        genai.delete_file(file.name)

    # Reset the uploaded files list
    if "uploaded_files" in st.session_state:
        st.session_state.pop("uploaded_files", None)

    if "pdf_uploaded" in st.session_state:
        st.session_state.pop("pdf_uploaded", None)

##--- FUNCTION TO STREAM LLM RESPONSE ---##
def stream_llm_response(model_params, model_type="google", api_key=None):
    response_message = ""
    if model_type == "google": 
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
                model_name = model_params["model"],
                generation_config={
                    "temperature": model_params["temperature"],
                    "max_output_tokens": model_params["max_tokens"],
                },
                safety_settings=set_safety_settings(),
                system_instruction="""You are a helpful assistant who asnwers user's questions professionally and politely."""
            )
        gemini_messages = messages_to_gemini(st.session_state.messages)

        for chunk in model.generate_content(contents=gemini_messages, stream=True):
            chunk_text = chunk.text or ""
            response_message += chunk_text
            yield chunk_text

    st.session_state.messages.append({
    "role": "assistant", 
    "content": [
        {
            "type": "text",
            "text": response_message,
        }
    ]})


##--- API KEYS ---##
with st.sidebar:
    st.logo("logo.png")
    api_cols = st.columns(2)
    with api_cols[0]:
        with st.popover("🔐 Groq", use_container_width=True):
            groq_api_key = st.text_input("Click [here](https://console.groq.com/keys) to get your Groq API key", type="password")
    
    with api_cols[1]:
        with st.popover("🔐 Google", use_container_width=True):
            google_api_key = st.text_input("Click [here](https://aistudio.google.com/app/apikey) to get your Google API key", type="password")
 
##--- API KEY CHECK ---##
if (groq_api_key == "" or groq_api_key is None or "gsk" not in groq_api_key) and (google_api_key == "" or google_api_key is None or "AIza" not in google_api_key):
    st.info("Please enter an API key in the sidebar to proceed.")

####--- LLM SIDEBAR ---###
else:
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
                response_lang = st.selectbox("Available Voices:", options=voices.keys(), key="voice_response")
    
        available_models = [] + (google_models if google_api_key else []) + (groq_models if groq_api_key else [])
        model, model_type, temperature, max_tokens = get_llm_info(available_models)

        model_params = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        st.divider()

        ###---- Google Gemini Sidebar Customization----###
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
            st.divider()
            tip = "If you upload a PDF, it will be sent to LLM."
            pdf_upload = st.file_uploader("Upload a PDF", type="pdf", key="pdf_uploaded", on_change=add_pdf_file_to_messages, help=tip)
        ###---- Groq Models Sidebar Customization----###
        else:
            pass  # will add later

######-----  Main Interface -----#######
    chat_col1, chat_col2 = st.columns([1,3.5])

    with chat_col1:
        ###--- Audio Recording ---###
        audio_bytes = audio_recorder("Speak",
                                     neutral_color="#f5f8fc",
                                     recording_color="#f81f6f",
                                     icon_name="microphone-lines",
                                     icon_size="3x")

        ###--- Reset Conversation ---###
        st.button(
                "🗑 Reset",
                use_container_width=True,
                on_click=reset_conversation,
                help="If clicked, conversation will be reset.",
            )
        
        if pdf_upload:
            pdf_pages = extract_all_pages_as_images(pdf_upload)
            st.session_state["pdf_pages"] = pdf_pages
            zoom_level = st.slider(label="",label_visibility="collapsed",
                min_value=100, max_value=1000, value=400, step=100, key="zoom_level"
            )
            with st.container(height=200, border=True):
                    for page_image in pdf_pages:
                        st.image(page_image, width=zoom_level)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Handle speech input
    speech_file_added = False
    if "prev_speech_hash" not in st.session_state:
        st.session_state.prev_speech_hash = None

    if audio_bytes and st.session_state.prev_speech_hash != hash(audio_bytes):
        st.session_state.prev_speech_hash = hash(audio_bytes)
        speech_base64 = base64.b64encode(audio_bytes).decode()
        unique_id = random.randint(1000, 9999)
        st.session_state.messages.append(
            {
                "role": "user",
                "content": [{
                    "type": "speech_input",
                    "speech_input": f"data:audio/wav;base64,{speech_base64}",
                    "unique_name": f"temp_{unique_id}"
                }]
            }
        )
        speech_file_added = True

        
    with chat_col2:
        message_container = st.container(height=400, border=False)

        for message in st.session_state.messages:
            avatar = "assistant.png" if message["role"] == "assistant" else "user.png"
            valid_content = [
                content for content in message["content"]
                if not (
                    (content["type"] == "text" and content["text"] == "Please Answer what is asked in the audio.") or
                    content["type"] == "pdf_file"
                )
            ]
            if valid_content:
                with message_container.chat_message(message["role"], avatar=avatar):
                    for content in message["content"]:
                        if content["type"] == "text":
                            st.markdown(content["text"])
                        elif content["type"] == "image_url":      
                            st.image(content["image_url"]["url"])
                        elif content["type"] == "video_file":
                            st.video(content["video_file"])
                        elif content["type"] == "audio_file":
                            st.audio(content["audio_file"], autoplay=True)
                        elif content["type"] == "speech_input":
                            st.audio(content["speech_input"])


    ###----- User Question -----###
    if prompt:= st.chat_input("Type you question", key="question") or speech_file_added:
        if not speech_file_added:
            message_container.chat_message("user", avatar="user.png").markdown(prompt)

            st.session_state.messages.append(
                        {
                            "role": "user", 
                            "content": [{
                                "type": "text",
                                "text": prompt,
                            }]
                        }
                    )
        else:
            st.session_state.messages.append(
                        {
                            "role": "user", 
                            "content": [{
                                "type": "text",
                                "text": "Please Answer what is asked in the audio.",
                            }]
                        }
                    )

        ###----- Generate response -----###
        with message_container.chat_message("assistant", avatar="assistant.png"):
            try:
                final_response = st.write_stream(stream_llm_response(
                                model_params=model_params, 
                                model_type=model_type, 
                                api_key= google_api_key if model_type == "google" else groq_api_key
                            )
                        )
                if "voice_response" in st.session_state and st.session_state.voice_response:
                    response_lang = st.session_state.voice_response
                    text_to_speak = (final_response).translate(str.maketrans('', '', '#-*_😊👋😄😁🥳👍🤩😂😎')) # Removing special chars and emojis
                    with st.spinner("Generating voice response..."):
                        temp_file_path = asyncio.run(generate_speech(text_to_speak, voices[response_lang])) 
                        audio_player_html = get_audio_player(temp_file_path)  # Create an audio player
                        st.markdown(audio_player_html, unsafe_allow_html=True)
                        os.unlink(temp_file_path)  # Clean up the temporary audio file

            except genai.types.generation_types.BlockedPromptException as e:
                st.error(f"An error occurred: {e}", icon="❌")

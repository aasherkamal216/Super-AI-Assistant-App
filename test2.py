import streamlit as st
from audio_recorder_streamlit import audio_recorder
from PIL import Image
from io import BytesIO
import base64
from utils import set_safety_settings, google_models, groq_models, get_llm_info
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

st.title("Super AI Assistant")

###--- Function to convert base64 to temp file ---###
def base64_to_temp_file(base64_string, file_extension):
    base64_string = base64_string.split(",")[1]
    file_bytes = BytesIO(base64.b64decode(base64_string))
    temp_file_path = f"temp_file.{file_extension}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_bytes.read())
    return temp_file_path

###--- Function for preparing messages for Gemini---###
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
                video_file_path = base64_to_temp_file(content["video_file"], "mp4")
                with st.spinner("Sending video file to Gemini..."):
                    gemini_message["parts"].append(genai.upload_file(path=video_file_path))
                os.remove(video_file_path)

            elif content["type"] == "audio_file":
                audio_file_path = base64_to_temp_file(content["audio_file"], "wav")
                with st.spinner("Sending audio file to Gemini..."):
                    gemini_message["parts"].append(genai.upload_file(path=audio_file_path))
                os.remove(audio_file_path)

            elif content["type"] == "speech_input":
                speech_file_path = base64_to_temp_file(content["speech_input"], "wav")
                with st.spinner("Sending audio file to Gemini..."):
                    gemini_message["parts"].append(genai.upload_file(path=speech_file_path))
                os.remove(speech_file_path)

        if prev_role != message["role"]:
            gemini_messages.append(gemini_message)

        prev_role = message["role"]

    return gemini_messages


##-- Converting base64 to image ---##
def base64_to_image(base64_string):
    base64_string = base64_string.split(",")[1]
    
    return Image.open(BytesIO(base64.b64decode(base64_string)))

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

        for chunk in model.generate_content(contents=gemini_messages, stream=True,):
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
            groq_api_key = st.text_input("Get your Groq API Key (https://console.groq.com/keys)", type="password")
    
    with api_cols[1]:
        with st.popover("🔐 Google", use_container_width=True):
            google_api_key = st.text_input("Get your Google API Key (https://aistudio.google.com/app/apikey)", type="password")
 
##--- API KEY CHECK ---##
if (groq_api_key == "" or groq_api_key is None or "gsk" not in groq_api_key) and (google_api_key == "" or google_api_key is None or "AIza" not in google_api_key):
    st.warning("Please Add an API Key to proceed.")

####--- LLM SIDEBAR ---###
else:
    with st.sidebar:
        
        available_models = []  + (google_models if google_api_key else []) + (groq_models if groq_api_key else [])
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

        ###---- Groq Models Sidebar Customization----###
        else:
            pass  # will add later

######-----  Main Interface -----#######
    chat_col1, chat_col2 = st.columns([1,6])

    with chat_col1:
        ###--- Audio Recording ---###
        audio_bytes = audio_recorder("Speak",
                                     neutral_color="#f5f8fc",
                                     recording_color="#f81f6f",
                                     icon_name="microphone-lines",
                                     icon_size="3x")

        ###--- Reset Conversation ---###
        st.button(
                "🗑️ Reset",
                use_container_width=True,
                on_click=reset_conversation,
                help="If clicked, conversation will be reset.",
            )

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

        
    with chat_col2:
        message_container = st.container(height=380, border=False)

        for message in st.session_state.messages:
            avatar = "assistant.png" if message["role"] == "assistant" else "user.png"

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
    if prompt:= st.chat_input("Type you question", key="question"):
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
        
        ###----- Generate response -----###
        with message_container.chat_message("assistant", avatar="assistant.png"):

            model2key = {
                        "openai": groq_api_key,
                        "google": google_api_key,
                    }

            st.write_stream(stream_llm_response(
                        model_params=model_params, 
                        model_type=model_type, 
                        api_key=model2key[model_type]
                    )
                )


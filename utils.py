import streamlit as st
from streamlit_vertical_slider import vertical_slider
from langchain_core.prompts import ChatPromptTemplate
import speech_recognition as sr
import tempfile

@st.dialog("Confirm Selection 👇", width="large")
def visualize_display_page(selection_dict):
    """
    Visualize the answers and selected
    Args:
        st (streamlit): streamlit object
        selection_dict (dict): dictionary with the selected answers
    """
    # get the name of the file

    txt = st.text_area(
        "File and Timestamp",
        value=selection_dict.get("file_and_answer"),
        key="file_and_answer",
        height=70,
    )
    txt3 = st.text_area(
        "Prompt sent to Gemini",
        value=selection_dict.get("prompt"),
        key="prompt",
    )
    txt2 = st.text_area(
        "Response Gemini",
        height=300,
        key="respuesta_chat",
        value=selection_dict.get("respuesta_chat"),
    )
    if st.button("Accept", key="accept_inside_select_answer"):
        st.rerun()

def about():
    about_text = """This AI-powered Streamlit app allows users to interact with various LLMs through
    multiple media inputs, including text, images, audio, voice, video, PDF, Docx, and links.
    Users can choose between a Chatbot, Agents, or a summarizer model, customize voice responses,
    and reset the conversation as needed. The app processes and responds to queries in real-time,
    offering an intuitive and versatile experience."""
    return about_text

def temperature_slider():
    temperature = vertical_slider(
        label = "Temperature",  #Optional
        key = "vert_01" ,
        height = 100, #Optional - Defaults to 300#Optional - Defaults to "circle"
        step = 1, #Optional - Defaults to 1
        default_value=5,#Optional - Defaults to 0
        min_value= 0, # Defaults to 0
        max_value= 10, # Defaults to 10
        track_color = "blue",
        thumb_shape="square", #Optional - Defaults to #D3D3D3
        slider_color = 'lighgray', #Optional - Defaults to #29B5E8
        thumb_color= "orange", #Optional - Defaults to #11567f
        value_always_visible = False ,#Optional - Defaults to False
    )
    return temperature


def set_safety_settings():
    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

    return safety_settings

def speech_to_text(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as recording:
        recording.write(audio_bytes)
        temp_file_path = recording.name
        
    r = sr.Recognizer()
    with sr.AudioFile(temp_file_path) as source:
        recorded_voice = r.record(source)

        try:
            text = r.recognize_google(recorded_voice, language="en")
            return text
        except sr.UnknownValueError as e:
            st.error(e)
        except sr.RequestError as e:
            print("could not request result from google speech recognition service: {0}".format(e))

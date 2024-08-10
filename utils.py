import streamlit as st
import speech_recognition as sr
import tempfile

def about():
    about_text = """This AI-powered Streamlit app allows users to interact with various LLMs through
    multiple media inputs, including text, images, audio, voice, video, PDF, Docx, and links.
    Users can choose between a Chatbot, Agents, or a summarizer model, customize voice responses,
    and reset the conversation as needed. The app processes and responds to queries in real-time,
    offering an intuitive and versatile experience."""
    return about_text


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

def convert_speech_to_text(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as recording:
        recording.write(audio_bytes)
        temp_file_path = recording.name
        
    r = sr.Recognizer()
    with sr.AudioFile(temp_file_path) as source:
        recorded_voice = r.record(source)

        try:
            text = r.recognize_google(recorded_voice, language="en")
            return text
        except:
            st.error("Could not recognize speech", icon="❌")

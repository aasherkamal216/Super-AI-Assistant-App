import streamlit as st
import asyncio
import edge_tts
import io
import tempfile
import os

VOICES = ['en-US-GuyNeural','en-US-JennyNeural',"hi-IN-SwaraNeural", "en-PH-JamesNeural"]

st.title("Text-to-Speech with Edge TTS")

text_input = st.text_area("Enter the text you want to convert to speech:", "Hello World")
voice_selection = st.selectbox("Select a voice:", VOICES)

async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        await communicate.save(temp_file.name)
        temp_file_path = temp_file.name
    
    with open(temp_file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    
    os.unlink(temp_file_path)  # Delete the temporary file
    return audio_data

if st.button("Generate and Play Speech"):
    if text_input:
        with st.spinner("Generating speech..."):
            audio_data = asyncio.run(generate_speech(text_input, voice_selection))
            
            # Play the audio
            st.audio(audio_data, format="audio/mp3")
            st.success("Speech generated successfully!")
    else:
        st.warning("Please enter some text to convert to speech.")
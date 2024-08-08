import streamlit as st
from streamlit_vertical_slider import vertical_slider

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
    about_text = """Welcome to the Super GPT Assistant App. This app is created by Aasher Kamal.
"""
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
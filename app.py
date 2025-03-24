
import streamlit as st
from io import StringIO
from dotenv import load_dotenv

import os
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types



st.set_page_config(page_title='Gemini Vision Chatbot', 
                    page_icon = "images/gemini_avatar.png",
                    initial_sidebar_state = 'auto')


background_color = "#252740"

avatars = {
    "assistant" : "images/gemini_avatar.png",
    "user": "images/user_avatar.png"
}

st.markdown("<h2 style='text-align: center; color: #3184a0;'>Gemini Vision Chatbot</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.image("images/gemini_avatar.png")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?", "image": None}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"], 
                         avatar=avatars[message["role"]]):
        st.write(message["content"])
        if message["role"] == "assistant" and message["image"]:
            st.image(message["image"])


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]
    
st.sidebar.button("Clear Chat History", on_click=clear_chat_history)
with st.sidebar:
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image_bytes =Image.open(uploaded_file)
        if "image" not in st.session_state:
            st.session_state.image = image_bytes
        st.image(image_bytes, caption="Uploaded Image", use_column_width=True)


def run_query(input_text):
    """
    Run query. The model is initialized and then queried.
    Args:
        input_text (str): we are just passing to the model the user prompt
    Returns:
        response.text (str): the text of the response
    """
    try:
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        system_prompt = """
        #INSTRUCTIONS
        Generate an image according to the instructions. 
        Specify in the output text the changes made to the image
        #OUTPUT
        A generated image and a short text

        """
        contents = ([system_prompt,input_text], st.session_state.image)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
            )
        )

        if response:
            return response
        
        else:
            return "Error"

    except Exception as ex:
        print(f"Exception: {ex}")
        return "Error"
    

output = st.empty()
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.write(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        with st.spinner("Thinking..."):
            

            response = run_query(prompt)
            placeholder = st.empty()
            full_response = ""
            avatar_image = None
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    for item in part.text:
                        full_response += item
                        placeholder.markdown(full_response, unsafe_allow_html=True)
                        placeholder.markdown(part.text, unsafe_allow_html=True)
                elif part.inline_data is not None:
                    avatar_image = Image.open(BytesIO((part.inline_data.data)))
                    st.image(avatar_image)

    message = {"role": "assistant", 
               "content": part.text,
               "avatar": avatars["assistant"],
               "image": avatar_image}
    st.session_state.messages.append(message)
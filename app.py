import streamlit as st
import cv2
import os
from PIL import Image as PILImage
from google.api_core.client_options import ClientOptions
import google.generativeai as genai
import textwrap
import tempfile

# Configuration for Google Generative AI
genai.configure(
    api_key="AIzaSyB8cWDofkHVWOOFMbiUwr74pAEFnySQAHw",
    transport="rest",
    client_options=ClientOptions(
        api_endpoint=os.getenv("GOOGLE_API_BASE"),
    ),
)

save_dir = 'images'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if ret:
        filename = os.path.join(save_dir, 'image.jpg')
        cv2.imwrite(filename, frame)
        return filename
    else:
        st.error("Error: Failed to capture image.")
        return None

def call_LMM(image_path: str, prompt: str) -> str:
    img = PILImage.open(image_path)
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([prompt, img], stream=False)
    if response and response.text:
        return response.text
    else:
        return "Error: No valid response received from the model."

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# Initialize session state variables
if 'image_path' not in st.session_state:
    st.session_state.image_path = None
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""

st.title("Webcam/Image Upload and AI Processing")
st.write("Choose whether you want to upload an image from your device or use your webcam to take a picture.")

# Option for the user to choose image source
option = st.radio("Select Image Source:", ('Upload Image', 'Use Webcam'))

if option == 'Upload Image':
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_path = os.path.join(save_dir, uploaded_file.name)
        with open(image_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.image_path = image_path
        st.image(st.session_state.image_path, caption='Uploaded Image', use_column_width=True)
elif option == 'Use Webcam':
    st.write("Click on the button below to capture an image:")
    if st.button("Click Image"):
        image_path = capture_image()
        if image_path:
            st.session_state.image_path = image_path
            st.image(st.session_state.image_path, caption='Captured Image', use_column_width=True)

if st.session_state.image_path:
    st.session_state.prompt = st.text_area("Enter the prompt for the AI:", st.session_state.prompt)
    if st.button("Process Image"):
        st.write("Processing the image with Google Generative AI...")
        st.session_state.response_text = call_LMM(st.session_state.image_path, st.session_state.prompt)
        st.markdown(to_markdown(st.session_state.response_text))

if st.session_state.response_text:
    st.markdown(to_markdown(st.session_state.response_text))

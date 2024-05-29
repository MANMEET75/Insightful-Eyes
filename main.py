from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
import cv2
import os
from PIL import Image as PILImage
from google.api_core.client_options import ClientOptions
import google.generativeai as genai
import textwrap
import tempfile
from io import BytesIO
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
        return None
    ret, frame = cap.read()
    cap.release()
    if ret:
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes()
    else:
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

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    query_param1 = request.query_params.get('phone')
    print("parameter1",query_param1)
    query_param2 = request.query_params.get('timestamp')
    print("parameter2",query_param2)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ImageOverview")
async def process_image(image_file: UploadFile = File(...), prompt: str = Form(...)):
    image_path = None
    image_source="upload"
    if image_source == 'upload':
        contents = await image_file.read()
        with open(os.path.join(save_dir, image_file.filename), "wb") as f:
            f.write(contents)
        image_path = os.path.join(save_dir, image_file.filename)
    
    
    response_text = None
    if image_path:
        response_text = call_LMM(image_path,prompt)
    
    if response_text:
        return {"response_text": to_markdown(response_text)}
    else:
        return {"error": "Failed to process image."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

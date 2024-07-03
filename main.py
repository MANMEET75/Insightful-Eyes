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

from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from jwt import PyJWTError
from typing import Optional
import os
import cv2
from PIL import Image as PILImage
from google.api_core.client_options import ClientOptions
import google.generativeai as genai
import textwrap
from io import BytesIO
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta

# Configuration for Google Generative AI
genai.configure(
    api_key="AIzaSyDMPRBQUZO05p7DuGUIDAzMePDNLYG00cg",
    transport="rest",
    client_options=ClientOptions(
        api_endpoint=os.getenv("GOOGLE_API_BASE"),
    ),
)

save_dir = 'images'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Secret key to sign JWT token
SECRET_KEY = "#3hk@HKJHK@#J@#KJHKJ@#JK%$%@HKJ#@jkw43654344521434231@1212432!"
ALGORITHM = "HS256"

# Token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Example User model
class User(BaseModel):
    username: str
    password: str

# Example fake database
fake_users_db = {
    "fakeuser": {
        "username": "fakeuser",
        "password": "fakepassword",
    }
}

# Function to authenticate user
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and password == user["password"]:
        return user

# Function to create JWT token with expiration
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to verify JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# Token renewal mechanism
async def renew_token():
    while True:
        await asyncio.sleep(60 * 60)  # Sleep for 60 minutes
        # Regenerate token here
        print("Regenerating token...")
        pass  # Replace with actual logic to regenerate the token

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Token route
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_jwt_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Secured route requiring JWT token
@app.post("/ImageOverview", response_model=dict)
async def process_image(
    image_file: UploadFile = File(...),
    prompt: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    image_path = None
    image_source = "upload"
    if image_source == 'upload':
        contents = await image_file.read()
        with open(os.path.join(save_dir, image_file.filename), "wb") as f:
            f.write(contents)
        image_path = os.path.join(save_dir, image_file.filename)

    response_text = None
    if image_path:
        response_text = call_LMM(image_path, prompt)

    if response_text:
        return {"response_text": to_markdown(response_text)}
    else:
        return {"error": "Failed to process image."}

# Start token renewal in a separate task
import asyncio
asyncio.create_task(renew_token())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
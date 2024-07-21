import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI , HTTPException , status
from models import UserCreateRequest, UserUpdateRequest
from dotenv import load_dotenv

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
import logging

logger = logging.getLogger(__name__)



load_dotenv()
GOOGLE_APPLICATION_CREDENTIALS_JSON = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if not GOOGLE_APPLICATION_CREDENTIALS_JSON:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set.")

try:   
    credentials_dict = json.loads(GOOGLE_APPLICATION_CREDENTIALS_JSON)  
    cred = credentials.Certificate(credentials_dict)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()

except json.JSONDecodeError:
    raise ValueError("Invalid JSON format in GOOGLE_APPLICATION_CREDENTIALS_JSON.")
except Exception as e:
    raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")


app = FastAPI()


@app.get("/")
async def root():
    return {"Hello":"Krishna singh ji"}  


# Api for creating user
@app.post("/api/v1/users")
async def create_user(user: UserCreateRequest):
    try:
        user_data = user.dict()
        logger.debug(f"Received user data: {user_data}")
        
        existing_users = db.collection('users').where('email', '==', user_data.get('email')).get()
        if existing_users:
            logger.debug("User with this email already exists.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists. Please use a different email."
            )
        
        user_ref = db.collection('users').document()
        user_data['id'] = user_ref.id
        user_ref.set(user_data)
        
        logger.debug(f"User created with ID: {user_ref.id}")
        return user_data
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )



# Api for getting users details
@app.get("/api/v1/users")
async def get_users():
    try:
        users_ref = db.collection('users')
        users = users_ref.stream()
        user_list = [user.to_dict() for user in users]
        return user_list
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving users. Please try again later."
        )



# Api for updating  user's details
@app.put("/api/v1/users/{user_id}")
async def update_user(user_update: UserUpdateRequest, user_id: str):
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} does not exist."
        )

 
    update_data = {}
    for k, v in user_update.dict().items(): 
        if v is not None:
            update_data[k] = v


    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )

    try:
        user_ref.update(update_data)
        updated_user = user_ref.get().to_dict()
        return updated_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating the user. Details: {str(e)}"
        )

    

# Api for deleting user
@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id:str):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        raise HTTPException(
            status_code=404,
            detail=f"user with id: {user_id} does not exist"
        )
    
    try:
        user_ref.delete()
        return {"details": "User deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while deleting the user. Details: {str(e)}"
        )
   


# API for sending an email
@app.post("/api/v1/send_invite")
async def send_invite():
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD") 
    recipients = ["imkrsnna@gmail.com"]
    subject = "Invitation to Review Unified API Documentation"


    try:
        with open('templates/email_template.html', 'r') as file:
            html_template = file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="HTML template file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading HTML template: {e}")


    msg = MIMEMultipart()
    msg['From'] = formataddr(('Krishna Singh', sender_email))
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    # Attach HTML body
    msg.attach(MIMEText(html_template, 'html'))

   
    screenshot_path = './resources/firestore_Snaps_db/image1.png'  
    try:
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot_path))
            msg.attach(img)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Screenshot file not found: {screenshot_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error attaching the screenshot: {e}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return {"detail": "Email sent successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {e}"
        )
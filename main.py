import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI , HTTPException , status
from models import UserCreateRequest, UserUpdateRequest
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
import logging

'''
    @author Krishna Singh

    @date: 20/09/2024

    This FastAPI application provides several endpoints for user management and email functionality:

    - GET /: A simple root endpoint that confirms the API is up and running.

    - POST /api/v1/users: Creates a new user in the Firestore database. The user data is validated to ensure no duplicate email addresses exist.

    - GET /api/v1/users: Retrieves a list of all users from the Firestore database.

    - GET /api/v1/users/{user_id}: Retrieves a specific user from the Firestore database by user ID.

    - PUT /api/v1/users/{user_id}: Updates an existing user's details in the Firestore database. It ensures that only provided fields are updated and handles cases where no valid fields are supplied.

    - DELETE /api/v1/users/{user_id}: Deletes a user from the Firestore database by user ID.

    - POST /api/v1/send_invite: Sends an invitation email to specified recipients. The email includes an HTML template and an attachment (screenshot). The sender's email credentials are used to authenticate and send the email.

'''



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
    return {
         "Welcome to the Aviato Consulting Unified API! The API is up and running, and it's ready to handle user management for our projects. You can use this API to create, retrieve, update, and delete users as well as send invitations.",
       
    }


# Api for getting users details
@app.get("/api/v1/users", status_code=status.HTTP_200_OK)
async def get_users():
    try:
        users_ref = db.collection('users')
        users = users_ref.stream()
        user_list = [user.to_dict() for user in users]
        return user_list
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving users. Please try again later."
        )


# Api for getting a single user's details
@app.get("/api/v1/users/{user_id}",status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {user_id} does not exist."
            )
        
        return user_doc.to_dict()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while retrieving the user. Details: {str(e)}"
        )
    

# Api for creating user
@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequest):
    try:
        user_data = user.dict()
        logger.debug(f"Received user data: {user_data}")

        try:
            validate_email(user_data.get('email'))
        except EmailNotValidError as e:
            logger.debug(f"Invalid email format: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format. Please provide a valid email address."
            )

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
        return {"id": user_ref.id, **user_data}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )



# Api for updating user's details
@app.put("/api/v1/users/{user_id}", status_code=status.HTTP_200_OK)
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
        

    if 'email' in update_data:
        new_email = update_data['email']

        try:
            validate_email(new_email)
        except EmailNotValidError as e:
            logger.debug(f"Invalid email format: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format. Please provide a valid email address."
            )
        
        existing_users = db.collection('users').where('email', '==', new_email).get()

        if existing_users:
            if all(user.id != user_id for user in existing_users):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email address already exists. Please use a different email."
                )

    try:
        user_ref.update(update_data)
        updated_user = user_ref.get().to_dict()
        return updated_user

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    
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
        return {"User deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while deleting the user. Details: {str(e)}"
        )
   

# API for sending an email
@app.post("/api/v1/send_invite",status_code=status.HTTP_200_OK)
async def send_invite():
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD") 
    recipients = ["imkrsnna@gmail.com","krishna.singh@bbd.co.za","tejassonone01@gmail.com"]
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
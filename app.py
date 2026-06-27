import shutil
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
import os
from rag import (
    ask_question,
    store_document_in_chroma,
    clear_chroma_collection
)
from pdf_reader import extract_text_from_pdf
from database import engine, Base, get_db
from models import User
from schemas import (
    UserSignup,
    UserLogin,
    UserResponse,
    ChatRequest
)
from auth import (
    hash_password,
    verify_password,
    create_access_token
)

# -----------------------------------
# Create Tables
# -----------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------
# FastAPI App
# -----------------------------------
app = FastAPI(
    title="Domain Knowledge Co-Pilot API",
    version="1.0.0"
)


# -----------------------------------
# Home Route
# -----------------------------------
@app.get("/")
def home():
    return {
        "message": "Backend Running Successfully 🚀"
    }


# -----------------------------------
# Signup API
# -----------------------------------
@app.post(
    "/signup",
    response_model=UserResponse
)
def signup(
    user: UserSignup,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -----------------------------------
# Login API
# -----------------------------------
@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        user.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        {
            "user_id": existing_user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "name": existing_user.full_name,
            "email": existing_user.email
        }
    }
# -----------------------------------
# Upload Folder
# -----------------------------------
UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# -----------------------------------
# Upload PDF API
# -----------------------------------
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):
    # Check PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # File path
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # Save PDF
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Extract text
    extracted_text = extract_text_from_pdf(
        file_path
    )

    # Store in ChromaDB
    total_chunks = store_document_in_chroma(
        extracted_text,
        file.filename
    )

    return {
        "message": "PDF uploaded successfully",
        "file_name": file.filename,
        "chunks_created": total_chunks,
        "text_preview": extracted_text[:500]
    }

# -----------------------------------
# NOTE: Startup cleanup disabled
# -----------------------------------
# Uncomment below if you want to clear uploads and Chroma on every startup
# if os.path.exists(UPLOAD_FOLDER):
#     shutil.rmtree(UPLOAD_FOLDER)
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# clear_chroma_collection()


# -----------------------------------
# Chat API
# -----------------------------------
@app.post("/chat")
def chat(
    chat_request: ChatRequest
):
    response = ask_question(
        chat_request.question,
        chat_request.chat_history
    )

    return {
    "question": chat_request.question,
    "answer": response["answer"],
    "citation": response["citation"]
}
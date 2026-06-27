from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# -----------------------------
# User Schemas
# -----------------------------
class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# Document Schemas
# -----------------------------
class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# Chat Schemas
# -----------------------------
class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[list] = []


class ChatResponse(BaseModel):
    question: str
    answer: str
    citation: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    citation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
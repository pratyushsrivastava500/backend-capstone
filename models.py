from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# -----------------------------
# User Model
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    documents = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete"
    )

    chats = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete"
    )


# -----------------------------
# Document Model
# -----------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # Relationships
    owner = relationship(
        "User",
        back_populates="documents"
    )

    chats = relationship(
        "ChatHistory",
        back_populates="document",
        cascade="all, delete"
    )


# -----------------------------
# Chat History Model
# -----------------------------
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citation = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id")
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="chats"
    )

    document = relationship(
        "Document",
        back_populates="chats"
    )
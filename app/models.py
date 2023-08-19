from pydantic import BaseModel
from database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)
    name = Column(String)
    city = Column(String, index=True)

    announcement = relationship("Announcement", back_populates="user")
    comment = relationship("Comment", back_populates="user")


class UserRequest(BaseModel):
    username: str
    phone: str
    password: str
    name: str
    city: str


class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    name: str
    city: str


class UserUpdate(BaseModel):
    phone: str
    name: str
    city: str


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    price = Column(Integer, index=True)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_count = Column(Integer, default=0)

    user = relationship("User", back_populates="announcement")
    comment = relationship("Comment", back_populates="announcement")


class AnnouncementRequest(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class AnnouncementResponse(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: int
    comment_count: int


class AnnouncementUpdate(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    ads_id = Column(Integer, ForeignKey("announcements.id"))

    user = relationship("User", back_populates="comment")
    announcement = relationship("Announcement", back_populates="comment")


class CommentRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: str
    author_id: int


class CommentUpdate(BaseModel):
    content: str
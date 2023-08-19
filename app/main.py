from typing import Dict, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException, Form, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from jose import jwt
from repositories import UsersRepository, AnnouncementsRepository, CommentsRepository
from models import User, UserRequest, UserResponse, UserUpdate, \
                   Announcement, AnnouncementRequest, AnnouncementResponse, AnnouncementUpdate, \
                   Comment, CommentRequest, CommentResponse, CommentUpdate
from database import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)
app = FastAPI()

comments_repository = CommentsRepository()
announcements_repository = AnnouncementsRepository()
users_repository = UsersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_jwt(id: int) -> str:
    body = {"id": id}
    token = jwt.encode(body, "WolterWhite", "HS256")
    return token


def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "WolterWhite", "HS256")
    return data["id"]


@app.post("/auth/users/", status_code=200)
def post_signup(user: UserRequest, db: Session = Depends(get_db)):
    try:
        new_user = User(username=user.username,
                        phone=user.phone,
                        password=user.password,
                        name=user.name,
                        city=user.city)
        users_repository.save(db, new_user)
    except KeyError:
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User registered successfully"}


@app.post("/auth/users/login", status_code=200, response_model=Dict[str, str])
def post_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user_db = users_repository.get_user_by_username(db, form_data.username)
    if user_db is None or user_db.password != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_jwt(user_db.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.patch("/auth/users/me", status_code=200, response_model=bool)
def patch_profile(
        upd_data: UserUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    if user_id:
        upd_user = users_repository.update(db, user_id, upd_data)
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return upd_user


@app.get("/auth/users/me", status_code=200, response_model=UserResponse)
def get_profile(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    user_db = users_repository.get_user_by_id(db, user_id)
    user = UserResponse(id=user_db.id,
                        username=user_db.username,
                        phone=user_db.phone,
                        name=user_db.name,
                        city=user_db.city)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/shanyraks/", status_code=200)
def post_add_ads(announcement: AnnouncementRequest,
                 db: Session = Depends(get_db),
                 token: str = Depends(oauth2_scheme)
                 ):
    try:
        user_id = decode_jwt(token)
        user_db = users_repository.get_user_by_id(db, user_id)
        new_ads = Announcement(
                type=announcement.type,
                price=announcement.price,
                address=announcement.address,
                area=announcement.area,
                rooms_count=announcement.rooms_count,
                description=announcement.description,
        )
        user_db.announcement.append(new_ads)
        announcements_repository.save(db, new_ads)
    except KeyError:
        raise HTTPException(status_code=400, detail="Announcement already exists")

    return {"message": "Announcement registered successfully"}


@app.get("/shanyraks/{id}", status_code=200, response_model=AnnouncementResponse)
def get_announcement(id: int,
                db: Session = Depends(get_db)):
    announcement = announcements_repository.get_announcement_by_id(db, id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return announcement


@app.patch("/shanyraks/{id}")
def patch_announcement(id: int, upd_data: AnnouncementUpdate,
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    try:
        user_id = decode_jwt(token)
        new_data = Announcement(type=upd_data.type,
                                price=upd_data.price,
                                address=upd_data.address,
                                area=upd_data.area,
                                rooms_count=upd_data.rooms_count,
                                description=upd_data.description)
        announcements_repository.update(db, id, new_data, user_id)
        return {"message": "Announcement updated successfully"}
    except:
        raise HTTPException(status_code=404, detail="Non-user announcement")


@app.delete("/shanyraks/{id}")
def delete_announcements(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_id = decode_jwt(token)
        announcements_repository.delete(db, id, user_id)
        return {"message": "Announcement deleted successfully",
                "id": id
                }
    except:
        raise HTTPException(status_code=404, detail="Non-user announcement")


@app.post("/shanyraks/{id}/comments", status_code=200)
def post_add_comment(id: int,
                     comment: CommentRequest,
                     db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)
                    ):
    try:
        user_id = decode_jwt(token)
        if user_id:
            user_db = users_repository.get_user_by_id(db, user_id)
            ads = announcements_repository.get_announcement_by_id(db, id)
            new_comment = Comment(content=comment.content)
            user_db.comment.append(new_comment)
            ads.comment.append(new_comment)
            ads.comment_count = ads.comment_count + 1
            comments_repository.save(db, new_comment)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except KeyError:
        raise HTTPException(status_code=400, detail="Comment already exists")

    return {"message": "Comment registered successfully"}


@app.get("/shanyraks/{id}/comments", status_code=200, response_model=List[CommentResponse])
def get_comments(
            id: int,
            db: Session = Depends(get_db),
            token: str = Depends(oauth2_scheme)
):
    try:
        user_id = decode_jwt(token)
        if user_id:
            ads = announcements_repository.get_announcement_by_id(db, id)
            comments = comments_repository.get_comments_by_ads(ads)
            new_comments = []
            for comment in comments:
                new_comments.append(CommentResponse(id=comment.id,
                                                    content=comment.content,
                                                    created_at=str(comment.created_at),
                                                    author_id=comment.author_id))
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except KeyError:
        raise HTTPException(status_code=400, detail="Comment already exists")

    return new_comments


@app.patch("/shanyraks/{id}/comments/{comment_id}")
def patch_comment(id: int,
                  comment_id: int,
                  upd_data: CommentUpdate,
                  db: Session = Depends(get_db),
                  token: str = Depends(oauth2_scheme)):
    try:
        user_id = decode_jwt(token)
        new_data = Comment(content=upd_data.content)

        comments_repository.update(db, comment_id, id, user_id, new_data)
        return {"message": "Comment updated successfully"}
    except:
        raise HTTPException(status_code=404, detail="Non-user comment")


@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_comment(id: int,
                   comment_id: int,
                   db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    try:
        user_id = decode_jwt(token)
        ads = announcements_repository.get_announcement_by_id(db, id)
        ads.comment_count = ads.comment_count - 1
        comments_repository.delete(db, comment_id, id, user_id)
        return {"message": "Comment deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="Non-user comment")

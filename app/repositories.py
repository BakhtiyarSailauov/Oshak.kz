from typing import List

from models import User, UserUpdate, \
    Announcement, AnnouncementUpdate, \
    Comment, CommentUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException


class UsersRepository:
    def save(self, db: Session, user: User) -> bool:
        db.add(user)
        db.commit()
        db.refresh(user)
        return True

    def update(self, db: Session, user_id: int, upd_data: UserUpdate) -> bool:
        user = self.get_user_by_id(db, user_id)

        if upd_data.phone.lower() != "string" and upd_data.phone is not None:
            user.phone = upd_data.phone
        if upd_data.name.lower() != "string" and upd_data.name is not None:
            user.name = upd_data.name
        if upd_data.city.lower() != "string" and upd_data.city is not None:
            user.city = upd_data.city

        db.commit()
        db.refresh(user)
        return True

    def get_user_by_username(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, db:Session, id: int) -> User:
        return db.query(User).filter(User.id == id).first()

    def get_users(self, db: Session) -> List[User]:
        return db.query(User).all()


class AnnouncementsRepository:
    def save(self, db: Session, ads: Announcement) -> bool:
        db.add(ads)
        db.commit()
        db.refresh(ads)
        return True

    def update(self, db: Session, id: int, upd_data: AnnouncementUpdate, user_id: int) -> bool:
        announcement = self.get_announcement_by_id(db, id)

        if user_id == announcement.user_id:
            if upd_data.type.lower() != "string" and upd_data.type is not None:
                announcement.type = upd_data.type
            if upd_data.price != 0:
                announcement.price = upd_data.price
            if upd_data.address.lower() != "string" and upd_data.address is not None:
                announcement.address = upd_data.address
            if upd_data.area != 0:
                announcement.area = upd_data.area
            if upd_data.rooms_count != 0:
                announcement.rooms_count = upd_data.rooms_count
            if upd_data.description.lower() != "string" and upd_data.description is not None:
                announcement.description = upd_data.description
        else:
            raise HTTPException(status_code=404, detail="Non-user announcement")

        db.commit()
        db.refresh(announcement)
        return True

    def delete(self, db: Session, id: int, user_id: int):
        announcement = self.get_announcement_by_id(db, id)

        if user_id == announcement.user_id:
            db.delete(announcement)
        else:
            raise HTTPException(status_code=404, detail="Non-user announcement")

        db.commit()

    def get_announcement_by_id(self, db: Session, id: int) -> Announcement:
        return db.query(Announcement).filter(Announcement.id == id).first()


class CommentsRepository:
    def save(self, db: Session, comment: Comment) -> bool:
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return True

    def get_comments_by_ads(self, ads: Announcement) -> List[Comment]:
        return ads.comment

    def get_comment_by_id_and_ads_id(self, db:Session, id: int, ads_id: int) -> Comment:
        return db.query(Comment).filter(Comment.id == id).first()

    def update(self, db: Session, comment_id: int, ads_id: int, user_id: int, upd_data: CommentUpdate) -> bool:
        comment = self.get_comment_by_id_and_ads_id(db, comment_id, ads_id)

        if user_id == comment.author_id:
            if upd_data.content.lower() != "string" and upd_data.content is not None:
                comment.content = upd_data.content
        else:
            raise HTTPException(status_code=404, detail="Non-user announcement")

        db.commit()
        db.refresh(comment)
        return True

    def delete(self, db: Session, comment_id: int, ads_id: int, user_id: int) -> bool:
        comment = self.get_comment_by_id_and_ads_id(db, comment_id, ads_id)

        if user_id == comment.author_id:
            db.delete(comment)
        else:
            raise HTTPException(status_code=404, detail="Non-user announcement")

        db.commit()
        return True
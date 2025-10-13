"""User data model"""

from sqlalchemy import Column, String
from app.core.base.model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return "User: {}".format(self.username)

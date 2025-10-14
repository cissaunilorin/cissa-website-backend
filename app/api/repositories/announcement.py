from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.api.models.announcement import Announcement, Signatory


class AnnouncementRepository(BaseRepository[Announcement]):
    """
    Announcement repository class for CRUD operations on Announcement model.
    This class inherits from BaseRepository and provides specific methods for Announcement model.
    Attributes:
        model (Type[Announcement]): The SQLAlchemy Announcement model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Announcement, db)


class SignatoryRepository(BaseRepository[Signatory]):
    """
    Signatory repository class for CRUD operations on Signatory model.
    This class inherits from BaseRepository and provides specific methods for Signatory model.
    Attributes:
        model (Type[Signatory]): The SQLAlchemy Signatory model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Signatory, db)

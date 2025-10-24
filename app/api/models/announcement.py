from sqlalchemy import Column, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel

announcement_signatories = Table(
    'announcement_signatories',
    BaseTableModel.metadata,
    Column('announcement_id', String, ForeignKey('announcements.id'), primary_key=True),
    Column('signatory_id', String, ForeignKey('signatories.id'), primary_key=True)
)

class Signatory(BaseTableModel):
    __tablename__ = "signatories"

    name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    role = Column(String, nullable=False)
    contact = Column(String, nullable=True)

    announcements = relationship(
        "Announcement",
        secondary=announcement_signatories,
        back_populates="signatories",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "role": self.role,
            "contact": self.contact,
        }
    
    def __str__(self):
        return "Signatory: {}".format(self.name)
    
class Announcement(BaseTableModel):
    __tablename__ = "announcements"

    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    session = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)

    signatories = relationship(
        "Signatory",
        secondary=announcement_signatories,
        back_populates="announcements",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url,
            "category": self.category,
            "body": self.body,
            "session": self.session,
            "published_at": self.published_at,
            "signatories": [signatory.to_dict() for signatory in self.signatories],
        }
    
    def __str__(self):
        return "Announcement: {}".format(self.title)
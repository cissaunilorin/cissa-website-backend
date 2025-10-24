from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import UploadFile

from pydantic import BaseModel, StringConstraints
from app.core.base.schema import BaseResponseModel,PaginatedResponseModel
# create signatory request schema
class SignatoryRequest(BaseModel):
    name: Annotated[str, StringConstraints(max_length=255)]
    alias: Optional[Annotated[str, StringConstraints(max_length=255)]]
    role: Annotated[str, StringConstraints(max_length=100)]
    contact: Optional[Annotated[str, StringConstraints(max_length=55)]]

# create announcement form schema
class AnnouncementForm(BaseModel):
    title: Annotated[str, StringConstraints(max_length=255)]
    image: UploadFile
    category: Annotated[str, StringConstraints(max_length=100)]
    body: str
    session: Annotated[str, StringConstraints(max_length=100)]
    published_at: datetime
    signatories: List[str]

# response schema for signatory
class SignatoryResponseData(BaseModel):
    id: str
    name: str
    alias: Optional[str]
    role: str
    contact: Optional[str]

# response schema for announcement
class AnnouncementResponse(BaseModel):
    id: str
    title: str
    category: str
    body: str
    session: str
    published_at: datetime
    signatories: List[SignatoryResponseData]

class AnnouncementResponseModel(BaseResponseModel):
    data: AnnouncementResponse

class SignatoryResponseModel(BaseResponseModel):
    data: SignatoryResponseData

class AnnouncementsListResponseModel(PaginatedResponseModel):
    pass

class SignatoriesListResponseModel(BaseResponseModel):
    data: List[SignatoryResponseData]

# update 

class AnnouncementUpdateForm(BaseModel):
    title: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    image: Optional[UploadFile] = None
    category: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    body: Optional[str] = None
    session: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    published_at: Optional[datetime] = None
    signatories: Optional[List[str]] = None

class SignatoryUpdateRequest(BaseModel):
    name: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    alias: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    role: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    contact: Optional[Annotated[str, StringConstraints(max_length=55)]] = None

from typing import Annotated, List, Optional

from pydantic import BaseModel, StringConstraints
from app.core.base.schema import BaseResponseModel,PaginatedResponseModel, PaginatedResponse

# create signatory request schema
class SignatoryRequest(BaseModel):
    name: Annotated[str, StringConstraints(max_length=255)]
    alias: Optional[Annotated[str, StringConstraints(max_length=255)]]
    role: Annotated[str, StringConstraints(max_length=100)]
    contact: Optional[Annotated[str, StringConstraints(max_length=55)]]

# create announcement request schema
class AnnouncementRequest(BaseModel):
    title: Annotated[str, StringConstraints(max_length=255)]
    category: Annotated[str, StringConstraints(max_length=100)]
    body: str
    session: Annotated[str, StringConstraints(max_length=100)]
    published_at: Annotated[str, StringConstraints(max_length=100)]
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
    published_at: str
    signatories: List[SignatoryResponseData]

class AnnouncementResponseModel(BaseResponseModel):
    data: AnnouncementResponse

class SignatoryResponseModel(BaseResponseModel):
    data: SignatoryResponseData

class AnnouncementsListResponseModel(PaginatedResponseModel):
    data: PaginatedResponse

class SignatoriesListResponseModel(BaseResponseModel):
    data: List[SignatoryResponseData]

# update 

class AnnouncementUpdateRequest(BaseModel):
    title: Optional[Annotated[str, StringConstraints(max_length=255)]]
    category: Optional[Annotated[str, StringConstraints(max_length=100)]]
    body: Optional[str]
    session: Optional[Annotated[str, StringConstraints(max_length=100)]]
    published_at: Optional[Annotated[str, StringConstraints(max_length=100)]]
    signatories: Optional[List[str]]

class SignatoryUpdateRequest(BaseModel):
    name: Optional[Annotated[str, StringConstraints(max_length=255)]]
    alias: Optional[Annotated[str, StringConstraints(max_length=255)]]
    role: Optional[Annotated[str, StringConstraints(max_length=100)]]
    contact: Optional[Annotated[str, StringConstraints(max_length=55)]]

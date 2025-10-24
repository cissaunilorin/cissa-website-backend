from fastapi import APIRouter, Depends, status, Response, Form
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.core.dependencies.security import get_current_user

from app.api.v1.announcement import schemas
from app.api.services.announcement import AnnouncementService, SignatoryService
from app.api.models.user import User

signatory = APIRouter(prefix="/signatory", tags=["Signatory"])
announcement = APIRouter(prefix="/announcement", tags=["Announcement"])


@signatory.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.SignatoryResponseModel,
    summary="Create a new signatory",
    description="This endpoint creates a new signatory for announcements",
    tags=["Signatory"],
)
def create_signatory(
    schema: schemas.SignatoryRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to create a new signatory

    Args:
        schema (schemas.SignatoryRequest): Signatory creation schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = SignatoryService(db=db)

    signatory = service.create(schema=schema)

    response_data = schemas.SignatoryResponseData(**signatory.to_dict())

    return schemas.SignatoryResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Signatory created successfully",
        data=response_data,
    )


@signatory.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.SignatoriesListResponseModel,
    summary="Get all signatories",
    description="This endpoint retrieves all signatories",
    tags=["Signatory"],
)
def get_all_signatories(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to retrieve all signatories

    Args:
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = SignatoryService(db=db)

    signatories = service.get_all()

    response_data = [
        schemas.SignatoryResponseData(**signatory.to_dict())
        for signatory in signatories
    ]

    return schemas.SignatoriesListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Signatories retrieved successfully",
        data=response_data,
    )


@signatory.put(
    path="/{signatory_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.SignatoryResponseModel,
    summary="Update an existing signatory",
    description="This endpoint updates an existing signatory",
    tags=["Signatory"],
)
def update_signatory(
    signatory_id: str,
    schema: schemas.SignatoryUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to update an existing signatory

    Args:
        signatory_id (str): ID of the signatory to update
        schema (schemas.SignatoryUpdateRequest): Signatory update schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = SignatoryService(db=db)

    signatory = service.update(signatory_id=signatory_id, schema=schema)

    response_data = schemas.SignatoryResponseData(**signatory.to_dict())

    return schemas.SignatoryResponseModel(
        status_code=status.HTTP_200_OK,
        message="Signatory updated successfully",
        data=response_data,
    )


@signatory.delete(
    path="/{signatory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing signatory",
    description="This endpoint deletes an existing signatory",
    tags=["Signatory"],
)
def delete_signatory(
    signatory_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to delete an existing signatory

    Args:
        signatory_id (str): ID of the signatory to delete
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = SignatoryService(db=db)

    service.delete(signatory_id=signatory_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@announcement.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AnnouncementsListResponseModel,
    summary="Get all announcements",
    description="This endpoint retrieves all announcements",
    tags=["Announcement"],
)
def get_all_announcements(
    db: Annotated[Session, Depends(get_db)],
    page: int = 1,
    page_size: int = 10,
):
    """Endpoint to retrieve all announcements

    Args:
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 10.
    """

    service = AnnouncementService(db=db)

    paginated_data = service.list_announcements(page=page, page_size=page_size)

    paginated_data.items = [
        schemas.AnnouncementResponse(**announcement.to_dict())
        for announcement in paginated_data.items
    ]

    return schemas.AnnouncementsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Announcements retrieved successfully",
        data=paginated_data,
    )


@announcement.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.AnnouncementResponseModel,
    summary="Create a new announcement",
    description="This endpoint creates a new announcement",
    tags=["Announcement"],
)
async def create_announcement(
    schema: Annotated[schemas.AnnouncementForm, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to create a new announcement

    Args:
        schema (schemas.AnnouncementRequest): Announcement creation schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = AnnouncementService(db=db)

    announcement = await service.create(schema=schema)

    response_data = schemas.AnnouncementResponse(**announcement.to_dict())

    return schemas.AnnouncementResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Announcement created successfully",
        data=response_data,
    )


@announcement.put(
    path="/{announcement_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AnnouncementResponseModel,
    summary="Update an existing announcement",
    description="This endpoint updates an existing announcement",
    tags=["Announcement"],
)
async def update_announcement(
    announcement_id: str,
    schema: Annotated[schemas.AnnouncementUpdateForm, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to update an existing announcement

    Args:
        announcement_id (str): ID of the announcement to update
        schema (schemas.AnnouncementUpdateRequest): Announcement update schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = AnnouncementService(db=db)

    announcement = await service.update(announcement_id=announcement_id, schema=schema)

    response_data = schemas.AnnouncementResponse(**announcement.to_dict())

    return schemas.AnnouncementResponseModel(
        status_code=status.HTTP_200_OK,
        message="Announcement updated successfully",
        data=response_data,
    )


@announcement.get(
    path="/{announcement_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AnnouncementResponseModel,
    summary="Get an announcement by ID",
    description="This endpoint retrieves an announcement by its ID",
    tags=["Announcement"],
)
def get_announcement_by_id(
    announcement_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    """Endpoint to retrieve an announcement by its ID

    Args:
        announcement_id (str): ID of the announcement to retrieve
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = AnnouncementService(db=db)

    announcement = service.get_by_id(announcement_id=announcement_id)

    response_data = schemas.AnnouncementResponse(**announcement.to_dict())

    return schemas.AnnouncementResponseModel(
        status_code=status.HTTP_200_OK,
        message="Announcement retrieved successfully",
        data=response_data,
    )


@announcement.delete(
    path="/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing announcement",
    description="This endpoint deletes an existing announcement",
    tags=["Announcement"],
)
def delete_announcement(
    announcement_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to delete an existing announcement

    Args:
        announcement_id (str): ID of the announcement to delete
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated user
    """

    service = AnnouncementService(db=db)

    service.delete(announcement_id=announcement_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

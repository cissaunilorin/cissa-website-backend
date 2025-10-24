from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.models.announcement import Announcement, Signatory
from app.api.repositories.announcement import (
    AnnouncementRepository,
    SignatoryRepository,
)
from app.api.v1.announcement import schemas
from app.utils.logger import logger
from app.utils.supabase_storage import (
    upload_image_to_supabase,
    delete_image_from_supabase,
)

from app.core.base.schema import PaginatedResponse


class SignatoryService:
    """
    Signatory service class for handling signatory-related operations.
    This class provides methods for creating, retrieving, updating, and deleting signatories.
    """

    def __init__(self, db: Session):
        self.repository = SignatoryRepository(db)

    def create(self, schema: schemas.SignatoryRequest) -> Signatory:
        """Creates a new signatory
        Args:
            schema (schemas.SignatoryRequest): Signatory creation schema
        Returns:
            Signatory: Signatory object for the newly created signatory
        """
        signatory = Signatory(**schema.model_dump())

        try:
            logger.info(f"Creating signatory with name: {signatory.name}")
            return self.repository.create(signatory)
        except Exception as e:
            logger.error(
                f"Error creating signatory with name: {signatory.name} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the signatory",
            )

    # get a list of all signatories
    def get_all(self) -> list[Signatory]:
        """Retrieves all signatories
        Returns:
            list[Signatory]: List of all signatories
        """
        logger.info("Retrieving all signatories")
        return self.repository.get_all()

    # update
    def update(
        self, signatory_id: str, schema: schemas.SignatoryUpdateRequest
    ) -> Signatory:
        """Updates an existing signatory
        Args:
            signatory_id (str): ID of the signatory to update
            schema (schemas.SignatoryUpdateRequest): Signatory update schema
        Returns:
            Signatory: Updated signatory object
        """
        signatory = self.repository.get(signatory_id)
        if not signatory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signatory not found",
            )

        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(signatory, key, value)

        try:
            logger.info(f"Updating signatory with ID: {signatory_id}")
            return self.repository.update(signatory)
        except Exception as e:
            logger.error(f"Error updating signatory with ID: {signatory_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the signatory",
            )

    def delete(self, signatory_id: str) -> bool:
        """Deletes a signatory
        Args:
            signatory_id (str): ID of the signatory to delete
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        signatory = self.repository.get(signatory_id)
        if not signatory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signatory not found",
            )

        try:
            logger.info(f"Deleting signatory with ID: {signatory_id}")
            return self.repository.delete(signatory_id)
        except Exception as e:
            logger.error(f"Error deleting signatory with ID: {signatory_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the signatory",
            )


class AnnouncementService:
    """
    Announcement service class for handling announcement-related operations.
    This class provides methods for creating, retrieving, updating, and deleting announcements.
    """

    def __init__(self, db: Session):
        self.repository = AnnouncementRepository(db)
        self.signatory_repository = SignatoryRepository(db)

    async def create(self, schema: schemas.AnnouncementForm) -> Announcement:
        """Creates a new announcement
        Args:
            schema (schemas.AnnouncementRequest): Announcement creation schema
        Returns:
            Announcement: Announcement object for the newly created announcement
        """
        # fetch signatories from the database
        signatories = []
        for signatory_id in schema.signatories:
            signatory = self.signatory_repository.get(signatory_id)
            if not signatory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Signatory with ID {signatory_id} not found",
                )
            signatories.append(signatory)

        announcement_data = schema.model_dump(exclude={"signatories", "image"})
        announcement = Announcement(**announcement_data)
        announcement.signatories = signatories

        # create announcement in the database
        try:
            logger.info(f"Creating announcement with title: {announcement.title}")
            new_announcement = self.repository.create(announcement)
        except Exception as e:
            logger.error(
                f"Error creating announcement with title: {announcement.title} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the announcement",
            )

        # upload image to supabase storage
        image_path = f"announcements/{new_announcement.id}.{schema.image.filename.split('.')[-1]}"

        try:
            logger.info(
                f"Uploading image for announcement with title: {new_announcement.title}"
            )
            new_announcement.image_url = await upload_image_to_supabase(
                schema.image, "announcements", image_path
            )
        except Exception as e:
            logger.error(
                f"Error uploading image for announcement with title: {new_announcement.title} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while uploading the announcement image",
            )

        # update announcement with image URL
        try:
            logger.info(
                f"Updating announcement with image URL for title: {new_announcement.title}"
            )
            return self.repository.update(new_announcement)
        except Exception as e:
            logger.error(
                f"Error updating announcement with image URL for title: {new_announcement.title} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the announcement with image URL",
            )

    async def update(
        self, announcement_id: str, schema: schemas.AnnouncementUpdateForm
    ) -> Announcement:
        """Updates an existing announcement
        Args:
            announcement_id (str): ID of the announcement to update
            schema (schemas.AnnouncementUpdateRequest): Announcement update schema
        Returns:
            Announcement: Updated announcement object
        """
        announcement = self.repository.get(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )

        if schema.signatories is not None:
            signatories = []
            for signatory_id in schema.signatories:
                signatory = self.signatory_repository.get(signatory_id)
                if not signatory:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Signatory with ID {signatory_id} not found",
                    )
                signatories.append(signatory)
            announcement.signatories = signatories

        if schema.image is not None:
            image_path = f"announcements/{announcement.id}.{schema.image.filename.split('.')[-1]}"

            try:
                logger.info(
                    f"Updating announcement with image URL for title: {announcement.title}"
                )
                announcement.image_url = await upload_image_to_supabase(
                    schema.image, "announcements", image_path
                )
            except Exception as e:
                logger.error(
                    f"Error uploading image for announcement with title: {announcement.title} - {str(e)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while uploading the announcement image",
                )

        for key, value in schema.model_dump(
            exclude_unset=True, exclude={"signatories", "image"}
        ).items():
            setattr(announcement, key, value)

        try:
            logger.info(f"Updating announcement with ID: {announcement_id}")
            return self.repository.update(announcement)
        except Exception as e:
            logger.error(
                f"Error updating announcement with ID: {announcement_id} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the announcement",
            )

    def delete(self, announcement_id: str) -> bool:
        """Deletes an announcement
        Args:
            announcement_id (str): ID of the announcement to delete
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        announcement = self.repository.get(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )

        if announcement.image_url:
            filename = announcement.image_url.split("/")[-1]
            image_path = f"announcements/{announcement.id}.{filename.split('.')[-1]}"
            try:
                delete_image_from_supabase("announcements", image_path)
            except Exception as e:
                logger.error(
                    f"Error deleting image for announcement with title: {announcement.title} - {str(e)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while deleting the announcement image",
                )

        try:
            logger.info(f"Deleting announcement with ID: {announcement_id}")
            return self.repository.delete(announcement_id)
        except Exception as e:
            logger.error(
                f"Error deleting announcement with ID: {announcement_id} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the announcement",
            )

    def list_announcements(
        self, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse:
        """
        Retrieves a paginated list of announcements

        Args:
            page (int): Page number (default: 1)
            page_size (int): Number of items per page (default: 10)

        Returns:
            PaginatedResponse: Paginated response containing announcements
        """

        query = self.repository.base_query()

        return self.repository.paginate(query, page, page_size)

    def get_by_id(self, announcement_id: str) -> Announcement:
        """Retrieves an announcement by ID
        Args:
            announcement_id (str): ID of the announcement to retrieve
        Returns:
            Announcement: Announcement object
        """
        announcement = self.repository.get(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
        return announcement

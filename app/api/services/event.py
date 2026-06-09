from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Literal

from app.api.models.event import Event
from app.api.repositories.event import EventRepository
from app.api.v1.event import schemas

from app.utils.logger import logger
from app.utils.slug import generate_unique_slug
from app.utils.supabase_storage import (
    upload_image_to_supabase,
    delete_image_from_supabase,
)

from app.core.base.schema import PaginatedResponse


class EventService:
    """
    Event service class for handling business logic related to events.
    This class interacts with the EventRepository to perform CRUD operations.
    """

    def __init__(self, db: Session):
        self.repository = EventRepository(db)

    async def create_event(self, schema: schemas.EventForm) -> Event:
        """Creates a new event.

        Args:
            schema (schemas.EventForm): The form data for creating an event.

        Returns:
            Event: The created Event object.
        """

        event_data = schema.model_dump(exclude={"image"})
        event = Event(**event_data)

        # generate a unique SEO-friendly slug from the title
        event.slug = generate_unique_slug(
            event.title, self.repository.slug_exists
        )

        # create event first
        try:
            new_event = self.repository.create(event)
            logger.info(
                f"Event with title '{new_event.title}' created successfully with ID '{new_event.id}'"
            )
        except Exception as e:
            logger.error(f"Error creating event with title '{event.title}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the event",
            )

        # upload image to supabase storage and get the URL
        image_path = f"events/{new_event.id}.{schema.image.filename.split('.')[-1]}"

        try:
            logger.info(
                f"Uploading image for event with title '{new_event.title}' to Supabase storage at path '{image_path}'"
            )
            new_event.image_url = await upload_image_to_supabase(
                schema.image, "events", image_path
            )
        except Exception as e:
            logger.error(
                f"Error uploading image for event with title '{new_event.title}': {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while uploading the event image",
            )

        # update event with image URL
        try:
            updated_event = self.repository.update(new_event)
            logger.info(
                f"Event with title '{updated_event.title}' updated successfully with image URL"
            )
            return updated_event
        except Exception as e:
            logger.error(
                f"Error updating event with title '{new_event.title}' with image URL: {str(e)}"
            )
            # delete the uploaded image from supabase storage if event update fails
            if new_event.image_url:
                try:
                    delete_image_from_supabase("events", image_path)
                    logger.info(
                        f"Deleted image from Supabase storage at path '{image_path}' due to event update failure"
                    )
                except Exception as delete_error:
                    logger.error(
                        f"Error deleting image from Supabase storage at path '{image_path}': {str(delete_error)}"
                    )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the event with the image URL",
            )

    async def update_event(
        self, event_id: str, schema: schemas.EventUpdateForm
    ) -> Event:
        """Updates an existing event.

        Args:
            event_id (str): The ID of the event to update.
            schema (schemas.EventUpdateForm): The form data for updating the event.

        Returns:
            Event: The updated Event object.
        """
        # get the existing event
        event = self.repository.get(event_id)
        if not event:
            logger.error(f"Event with ID '{event_id}' not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # update event fields
        update_data = schema.model_dump(exclude={"image"}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)

        # handle image update if a new image is provided
        if schema.image:
            image_path = f"events/{event.id}.{schema.image.filename.split('.')[-1]}"

            try:
                logger.info(
                    f"Uploading new image for event with ID '{event_id}' to Supabase storage at path '{image_path}'"
                )
                event.image_url = await upload_image_to_supabase(
                    schema.image, "events", image_path
                )
            except Exception as e:
                logger.error(
                    f"Error uploading new image for event with ID '{event_id}': {str(e)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while uploading the new event image",
                )

        # update the event in the database
        try:
            updated_event = self.repository.update(event)
            logger.info(f"Event with ID '{event_id}' updated successfully")
            return updated_event
        except Exception as e:
            logger.error(f"Error updating event with ID '{event_id}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the event",
            )

    def delete_event(self, event_id: str) -> None:
        """Deletes an event.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            None
        """
        # get the existing event
        event = self.repository.get(event_id)
        if not event:
            logger.error(f"Event with ID '{event_id}' not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # delete the event image from supabase storage if it exists
        if event.image_url:
            image_path = f"events/{event.id}.{event.image_url.split('.')[-1]}"
            try:
                delete_image_from_supabase("events", image_path)
                logger.info(
                    f"Deleted image from Supabase storage at path '{image_path}' for event with ID '{event_id}'"
                )
            except Exception as e:
                logger.error(
                    f"Error deleting image from Supabase storage at path '{image_path}' for event with ID '{event_id}': {str(e)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while deleting the event image",
                )

        # delete the event from the database
        try:
            self.repository.delete(event_id)
            logger.info(f"Event with ID '{event_id}' deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting event with ID '{event_id}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the event",
            )

    def get_event(self, event_id: str) -> Event:
        """Retrieves an event by slug or ID.

        Args:
            event_id (str): The slug or ID of the event to retrieve.

        Returns:
            Event: The retrieved Event object.
        """
        event = self.repository.get_by_slug_or_id(event_id)
        if not event:
            logger.error(f"Event with identifier '{event_id}' not found for retrieval")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        logger.info(f"Event with identifier '{event_id}' retrieved successfully")
        return event 

    def list_events(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        location_type: Optional[Literal["physical", "online"]] = None,
        time_status: Optional[Literal["upcoming", "past"]] = None,
    ) -> PaginatedResponse:
        """Lists events with pagination and optional filters.

        Args:
            page (int): The page number for pagination (default is 1).
            page_size (int): The number of items per page for pagination (default is 10).
            title (Optional[str]): Filter events by title (case-insensitive, partial match).
            location_type (Optional[Literal["physical", "online"]]): Filter events by location type ('physical' or 'online').
            time_status (Optional[Literal["upcoming", "past"]]): Filter events by time status ('upcoming' or 'past').

        Returns:
            PaginatedResponse[Event]: A paginated response containing the list of events and pagination metadata.
        """
        query = self.repository.base_query()

        # apply filters
        if time_status == "past":
            query = self.repository.filter_past_events(query)
        elif time_status == "upcoming":
            query = self.repository.filter_upcoming_events(query)

        if location_type:
            query = self.repository.filter_by_location_type(query, location_type)
        if title:
            query = self.repository.search_by_title(query, title)

        # sort by date:
        #   - upcoming: soonest first (ascending), so the next event is on top
        #   - past / unfiltered: most recent first (descending)
        if time_status == "upcoming":
            query = query.order_by(
                Event.start_date.asc(), Event.start_time.asc()
            )
        else:
            query = query.order_by(
                Event.start_date.desc(), Event.start_time.desc()
            )

        return self.repository.paginate(query, page, page_size)
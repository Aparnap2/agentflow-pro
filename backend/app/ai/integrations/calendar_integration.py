"""
Calendar Integration Module for Sales Agent.

This module provides functionality to interact with various calendar services.
Currently supports Google Calendar with a base interface for other providers.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pytz
import json
from enum import Enum

logger = logging.getLogger(__name__)

class EventStatus(str, Enum):
    """Status of a calendar event."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"

class EventAttendee(BaseModel):
    """Attendee of a calendar event."""
    email: str
    display_name: Optional[str] = None
    organizer: bool = False
    self: bool = False
    response_status: Optional[str] = None  # 'needsAction', 'declined', 'tentative', 'accepted'

class CalendarEvent(BaseModel):
    """Calendar event model."""
    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start: datetime
    end: datetime
    timezone: str = "UTC"
    attendees: List[EventAttendee] = Field(default_factory=list)
    organizer: Optional[EventAttendee] = None
    status: EventStatus = EventStatus.CONFIRMED
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    html_link: Optional[HttpUrl] = None
    conference_data: Optional[Dict[str, Any]] = None
    reminders: Optional[Dict[str, Any]] = None
    extended_properties: Optional[Dict[str, str]] = None
    color_id: Optional[str] = None
    visibility: Optional[str] = None  # 'default', 'public', 'private', 'confidential'
    
    @validator('start', 'end', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except (ValueError, TypeError):
                return v
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

class CalendarIntegration:
    """Base class for calendar integrations."""
    
    def __init__(self, **kwargs):
        """Initialize the calendar integration."""
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new calendar event.
        
        Args:
            event: Event details
            
        Returns:
            Created event with ID and other server-generated fields
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get_event(self, event_id: str, **kwargs) -> Optional[CalendarEvent]:
        """Get an event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            CalendarEvent if found, None otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def update_event(self, event_id: str, event: CalendarEvent, **kwargs) -> CalendarEvent:
        """Update an existing event.
        
        Args:
            event_id: ID of the event to update
            event: Updated event details
            
        Returns:
            Updated event
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def delete_event(self, event_id: str, **kwargs) -> bool:
        """Delete an event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def list_events(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
        **kwargs
    ) -> List[CalendarEvent]:
        """List events in the calendar.
        
        Args:
            time_min: Lower bound for event start time
            time_max: Upper bound for event end time
            max_results: Maximum number of events to return
            
        Returns:
            List of CalendarEvent objects
        """
        raise NotImplementedError("Subclasses must implement this method")

class GoogleCalendarIntegration(CalendarIntegration):
    """Google Calendar integration."""
    
    def __init__(
        self,
        credentials: Union[Dict, str, Credentials],
        calendar_id: str = "primary",
        **kwargs
    ):
        """Initialize Google Calendar integration.
        
        Args:
            credentials: Google OAuth2 credentials (dict, JSON string, or Credentials object)
            calendar_id: Calendar ID (defaults to primary calendar)
        """
        super().__init__(**kwargs)
        
        # Parse credentials if needed
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        
        if isinstance(credentials, dict):
            credentials = Credentials.from_authorized_user_info(credentials)
        
        self.credentials = credentials
        self.calendar_id = calendar_id
        self.service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
    
    def _to_google_event(self, event: CalendarEvent) -> Dict:
        """Convert CalendarEvent to Google Calendar event format."""
        google_event = {
            'summary': event.summary,
            'description': event.description,
            'location': event.location,
            'start': {
                'dateTime': event.start.isoformat(),
                'timeZone': event.timezone
            },
            'end': {
                'dateTime': event.end.isoformat(),
                'timeZone': event.timezone
            },
            'status': event.status.value,
        }
        
        if event.id:
            google_event['id'] = event.id
        
        if event.attendees:
            google_event['attendees'] = [
                {
                    'email': attendee.email,
                    'displayName': attendee.display_name,
                    'organizer': attendee.organizer,
                    'self': attendee.self,
                    'responseStatus': attendee.response_status
                }
                for attendee in event.attendees
            ]
        
        if event.conference_data:
            google_event['conferenceData'] = event.conference_data
        
        if event.reminders:
            google_event['reminders'] = event.reminders
        
        if event.extended_properties:
            google_event['extendedProperties'] = event.extended_properties
        
        if event.color_id:
            google_event['colorId'] = event.color_id
        
        if event.visibility:
            google_event['visibility'] = event.visibility
        
        return google_event
    
    def _from_google_event(self, google_event: Dict) -> CalendarEvent:
        """Convert Google Calendar event to CalendarEvent."""
        start = google_event.get('start', {})
        end = google_event.get('end', {})
        
        # Handle all-day events
        if 'date' in start:
            start_dt = datetime.fromisoformat(start['date'])
            end_dt = datetime.fromisoformat(end['date'])
            timezone = 'UTC'
        else:
            start_dt = datetime.fromisoformat(start['dateTime'])
            end_dt = datetime.fromisoformat(end['dateTime'])
            timezone = start.get('timeZone', 'UTC')
        
        attendees = []
        for attendee in google_event.get('attendees', []):
            attendees.append(EventAttendee(
                email=attendee.get('email'),
                display_name=attendee.get('displayName'),
                organizer=attendee.get('organizer', False),
                self=attendee.get('self', False),
                response_status=attendee.get('responseStatus')
            ))
        
        organizer = None
        if 'organizer' in google_event:
            organizer = EventAttendee(
                email=google_event['organizer'].get('email'),
                display_name=google_event['organizer'].get('displayName'),
                organizer=True
            )
        
        return CalendarEvent(
            id=google_event.get('id'),
            summary=google_event.get('summary', ''),
            description=google_event.get('description'),
            location=google_event.get('location'),
            start=start_dt,
            end=end_dt,
            timezone=timezone,
            attendees=attendees,
            organizer=organizer,
            status=EventStatus(google_event.get('status', 'confirmed')),
            created=datetime.fromisoformat(google_event['created'].replace('Z', '+00:00')) if 'created' in google_event else None,
            updated=datetime.fromisoformat(google_event['updated'].replace('Z', '+00:00')) if 'updated' in google_event else None,
            html_link=google_event.get('htmlLink'),
            conference_data=google_event.get('conferenceData'),
            reminders=google_event.get('reminders'),
            extended_properties=google_event.get('extendedProperties'),
            color_id=google_event.get('colorId'),
            visibility=google_event.get('visibility')
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, HttpError))
    )
    async def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new Google Calendar event."""
        try:
            google_event = self._to_google_event(event)
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=google_event,
                conferenceDataVersion=1 if event.conference_data else 0
            ).execute()
            
            return self._from_google_event(created_event)
            
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create calendar event: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, HttpError))
    )
    async def get_event(self, event_id: str, **kwargs) -> Optional[CalendarEvent]:
        """Get a Google Calendar event by ID."""
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id,
                **kwargs
            ).execute()
            
            return self._from_google_event(event)
            
        except HttpError as e:
            if e.resp.status == 404:
                return None
            self.logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get calendar event: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, HttpError))
    )
    async def update_event(self, event_id: str, event: CalendarEvent, **kwargs) -> CalendarEvent:
        """Update an existing Google Calendar event."""
        try:
            google_event = self._to_google_event(event)
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=google_event,
                **kwargs
            ).execute()
            
            return self._from_google_event(updated_event)
            
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to update calendar event: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, HttpError))
    )
    async def delete_event(self, event_id: str, **kwargs) -> bool:
        """Delete a Google Calendar event."""
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                **kwargs
            ).execute()
            return True
            
        except HttpError as e:
            if e.resp.status == 410:  # Already deleted
                return True
            self.logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete calendar event: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, HttpError))
    )
    async def list_events(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
        **kwargs
    ) -> List[CalendarEvent]:
        """List events from Google Calendar."""
        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min.isoformat() if time_min else now,
                timeMax=time_max.isoformat() if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                **kwargs
            ).execute()
            
            events = events_result.get('items', [])
            
            return [self._from_google_event(event) for event in events]
            
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list calendar events: {e}", exc_info=True)
            raise

# Factory function for creating the appropriate calendar integration
def create_calendar_integration(provider: str, **kwargs) -> CalendarIntegration:
    """Create a calendar integration instance based on the provider.
    
    Args:
        provider: Calendar provider name ('google')
        **kwargs: Provider-specific arguments
        
    Returns:
        An instance of the appropriate calendar integration class
    """
    provider = provider.lower()
    
    if provider == 'google':
        return GoogleCalendarIntegration(**kwargs)
    else:
        raise ValueError(f"Unsupported calendar provider: {provider}")

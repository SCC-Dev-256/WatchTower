from datetime import datetime, timedelta
from typing import List, Optional
from app.core.cablecast_IN_DEVELOPMENT import Show, ScheduleItem, Format, Media, DateScraper, MeetingInfo
from app.core.cablecast_IN_DEVELOPMENT.cablecast_constants import (
    MEDIA_NAME, FORMAT_LOCATION, RUN_DATE_TIME, RUN_BUMP, RUN_LOCK,
    BUG_TEXT, CRAWL_TEXT, CG_EXEMPT, RUN_STATUS
)

class CablecastScheduler:
    """Handles scheduling of city hall meetings in Cablecast"""
    
    def __init__(self, api_client, channel_id: int, storage_server_id: int):
        self.api_client = api_client
        self.channel_id = channel_id
        self.storage_server_id = storage_server_id
        self.default_duration = timedelta(hours=4) # 4 hour default duration
        
    def create_meeting_show(self, meeting_date: datetime, meeting_type: str) -> Show:
        """Creates a new show record for a city meeting
        
        Args:
            meeting_date: Date/time of the meeting
            meeting_type: Type of meeting (e.g. "City Council", "Planning Commission")
            
        Returns:
            Show object for the created show
        """
        # Get format for the channel's storage server
        format_response = self.api_client.get(f"/v1/formats?{FORMAT_LOCATION}={self.storage_server_id}")
        server_format = Format(**format_response.formats[0])
        
        # Create media record
        media_params = {
            MEDIA_NAME: f"{meeting_type} Meeting {meeting_date.strftime('%Y-%m-%d')}",
            "format": server_format.id,
            "location": self.storage_server_id
        }
        media_response = self.api_client.post("/v1/media", json=media_params)
        media = Media(**media_response.media)
        
        # Create show record
        show_params = {
            "title": f"{meeting_type} Meeting",
            "event_date": meeting_date.isoformat(),
            "duration": int(self.default_duration.total_seconds()),
            "custom_fields": {
                "CG Title": f"{meeting_type} Meeting - {meeting_date.strftime('%B %d, %Y')}"
            }
        }
        show_response = self.api_client.post("/v1/shows", json=show_params)
        return Show(**show_response.show)
        
    def schedule_meeting(self, show: Show, start_time: datetime) -> ScheduleItem:
        """Schedules a show into the channel schedule
        
        Args:
            show: Show object to schedule
            start_time: Date/time to schedule the show
            
        Returns:
            ScheduleItem for the scheduled show
        """
        schedule_params = {
            "channel": self.channel_id,
            "show": show.id,
            RUN_DATE_TIME: start_time.isoformat(),
            RUN_BUMP: 0,
            RUN_LOCK: True,
            BUG_TEXT: show.custom_fields["CG Title"],
            CRAWL_TEXT: "",
            CG_EXEMPT: False,
            RUN_STATUS: 0 # Tentative status
        }
        
        schedule_response = self.api_client.post("/v1/scheduleItems", json=schedule_params)
        return ScheduleItem(**schedule_response.scheduleItem)

    def create_and_schedule_meeting(self, meeting_date: datetime, meeting_type: str) -> tuple[Show, ScheduleItem]:
        """Creates and schedules a meeting show
        
        Args:
            meeting_date: Date/time of the meeting
            meeting_type: Type of meeting
            
        Returns:
            Tuple of (Show, ScheduleItem) for the created and scheduled show
        """
        show = self.create_meeting_show(meeting_date, meeting_type)
        schedule_item = self.schedule_meeting(show, meeting_date)
        return show, schedule_item

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.core.cablecast_IN_DEVELOPMENT import SchedulingAssistant, ScheduledEvent, ScheduledAction, DateScraper, MeetingInfo
from app.core.aja.machine_logic.helo_params import HeloParameters
from app.core.aja.machine_logic.helo_commands import recall_preset, set_recording_name, start_recording, stop_recording
from flask_caching import Cache

logger = logging.getLogger(__name__)

class AJACablecastIntegrator:
    """Integrates AJA HELO encoders with Cablecast scheduling and city meeting sources"""
    
    def __init__(self, cache: Cache):
        self.cache = cache
        self.date_scraper = DateScraper(cache)
        self.helo_params = HeloParameters()
        self.scheduling_assistant = SchedulingAssistant(self.helo_params)
        self.encoder_assignments: Dict[str, str] = {}  # Maps city names to encoder IDs
        
    def assign_encoder(self, city_name: str, encoder_id: str):
        """Assign an encoder to a specific city"""
        self.encoder_assignments[city_name] = encoder_id
        
    def sync_city_meetings(self, city_name: str) -> List[ScheduledEvent]:
        """Sync meetings from a city source to the scheduling system"""
        try:
            # Get meetings from city website
            meetings = self.date_scraper.fetch_meetings(city_name)
            
            # Convert meetings to scheduled events
            events = []
            for meeting in meetings:
                event = self._convert_meeting_to_event(meeting, city_name)
                if event:
                    self.scheduling_assistant.add_event(event)
                    events.append(event)
                    
            logger.info(f"Synced {len(events)} events for {city_name}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to sync meetings for {city_name}: {str(e)}")
            return []
            
    def _convert_meeting_to_event(self, meeting: MeetingInfo, city_name: str) -> Optional[ScheduledEvent]:
        """Convert a meeting into a scheduled recording event"""
        try:
            # Calculate end time (default 3 hours if not specified)
            end_time = meeting.date + timedelta(hours=3)
            
            # Generate unique ID
            event_id = f"{city_name}_{meeting.date.strftime('%Y%m%d_%H%M')}"
            
            # Create recording filename
            meeting_date = meeting.date.strftime("%Y%m%d")
            filename = f"{city_name}_{meeting_date}_{meeting.meeting_type}"
            
            return ScheduledEvent(
                id=event_id,
                start_time=meeting.date,
                end_time=end_time,
                action=ScheduledAction.RECORD_AND_STREAM,
                title=meeting.title,
                description=meeting.description
            )
            
        except Exception as e:
            logger.error(f"Failed to convert meeting to event: {str(e)}")
            return None
            
    def prepare_encoder(self, encoder_id: str, event: ScheduledEvent):
        """Prepare encoder for an upcoming recording"""
        try:
            device_url = f"http://{encoder_id}"  # Assuming IP-based URL
            
            # Set recording filename
            meeting_date = event.start_time.strftime("%Y%m%d")
            filename = f"{event.title}_{meeting_date}"
            set_recording_name(device_url, filename)
            
            # Recall appropriate preset (assuming preset 1 for meetings)
            recall_preset(device_url, 1)
            
            logger.info(f"Prepared encoder {encoder_id} for event: {event.title}")
            
        except Exception as e:
            logger.error(f"Failed to prepare encoder {encoder_id}: {str(e)}")
            
    def start_scheduled_recording(self, encoder_id: str, event: ScheduledEvent):
        """Start a scheduled recording on an encoder"""
        try:
            device_url = f"http://{encoder_id}"
            start_recording(device_url)
            logger.info(f"Started recording for event: {event.title} on encoder {encoder_id}")
            
        except Exception as e:
            logger.error(f"Failed to start recording on encoder {encoder_id}: {str(e)}")
            
    def stop_scheduled_recording(self, encoder_id: str, event: ScheduledEvent):
        """Stop a scheduled recording on an encoder"""
        try:
            device_url = f"http://{encoder_id}"
            stop_recording(device_url)
            logger.info(f"Stopped recording for event: {event.title} on encoder {encoder_id}")
            
        except Exception as e:
            logger.error(f"Failed to stop recording on encoder {encoder_id}: {str(e)}")
            
    def monitor_upcoming_events(self):
        """Monitor and handle upcoming scheduled events"""
        try:
            # Get events in next hour
            upcoming = self.scheduling_assistant.get_upcoming_events(hours=1)
            
            for event in upcoming:
                # Extract city name from event ID
                city_name = event.id.split('_')[0]
                
                # Get assigned encoder
                encoder_id = self.encoder_assignments.get(city_name)
                if not encoder_id:
                    logger.warning(f"No encoder assigned for {city_name}")
                    continue
                    
                # Calculate time until event
                time_until = event.start_time - datetime.now()
                
                # Prepare encoder 10 minutes before
                if timedelta(minutes=0) <= time_until <= timedelta(minutes=10):
                    self.prepare_encoder(encoder_id, event)
                    
                # Start recording at start time
                if timedelta(minutes=0) <= time_until <= timedelta(minutes=1):
                    self.start_scheduled_recording(encoder_id, event)
                    
                # Stop recording at end time
                if event.end_time <= datetime.now():
                    self.stop_scheduled_recording(encoder_id, event)
                    
        except Exception as e:
            logger.error(f"Error monitoring upcoming events: {str(e)}")

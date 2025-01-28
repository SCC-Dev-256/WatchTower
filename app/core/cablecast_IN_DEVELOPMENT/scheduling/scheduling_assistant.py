from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import icalendar
import requests
from app.core.aja.aja_helo_parameter_service import AJAParameterManager, AJAReplicatorCommands
from app.core.aja.machine_logic.helo_params import HeloParameters, MediaState
from app.core.cablecast_IN_DEVELOPMENT.scheduling.date_scraper import DateScraper, MeetingInfo

class ScheduledAction(Enum):
    RECORD = "record"
    STREAM = "stream" 
    RECORD_AND_STREAM = "record_and_stream"

@dataclass
class ScheduledEvent:
    id: str
    start_time: datetime
    end_time: datetime
    action: ScheduledAction
    title: str
    description: Optional[str] = None
    remote_id: Optional[str] = None  # For synced calendar events

class SchedulingAssistant:
    def __init__(self, helo_params: HeloParameters):
        self.helo_params = helo_params
        self.events: List[ScheduledEvent] = []
        self.param_manager = AJAParameterManager()

    def add_event(self, event: ScheduledEvent) -> bool:
        """Add new event after validating for conflicts"""
        if self._check_conflicts(event):
            return False
            
        self.events.append(event)
        self.events.sort(key=lambda x: x.start_time)
        return True

    def remove_event(self, event_id: str) -> bool:
        """Remove event by ID"""
        initial_len = len(self.events)
        self.events = [e for e in self.events if e.id != event_id]
        return len(self.events) < initial_len

    def _check_conflicts(self, new_event: ScheduledEvent) -> bool:
        """Check for scheduling conflicts"""
        for event in self.events:
            if (new_event.start_time < event.end_time and 
                new_event.end_time > event.start_time):
                return True
        return False

    def sync_calendar(self, calendar_url: str):
        """Sync with external calendar"""
        try:
            response = requests.get(calendar_url)
            cal = icalendar.Calendar.from_ical(response.text)
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event = ScheduledEvent(
                        id=str(component.get('uid')),
                        start_time=component.get('dtstart').dt,
                        end_time=component.get('dtend').dt,
                        action=ScheduledAction.RECORD_AND_STREAM,  # Default action
                        title=str(component.get('summary')),
                        description=str(component.get('description')),
                        remote_id=str(component.get('uid'))
                    )
                    self.add_event(event)
        except Exception as e:
            print(f"Calendar sync failed: {str(e)}")

    def execute_event(self, event: ScheduledEvent):
        """Execute scheduled event actions"""
        if event.action in [ScheduledAction.RECORD, ScheduledAction.RECORD_AND_STREAM]:
            self.helo_params.device_parameters.media_state = MediaState.RECORD_STREAM
            # Trigger recording start
            self.param_manager.set_param(AJAReplicatorCommands.START_RECORDING)
            
        if event.action in [ScheduledAction.STREAM, ScheduledAction.RECORD_AND_STREAM]:
            # Trigger streaming start  
            self.param_manager.set_param(AJAReplicatorCommands.START_STREAMING)

    def get_upcoming_events(self, hours: int = 24) -> List[ScheduledEvent]:
        """Get list of upcoming events within specified hours"""
        now = datetime.now()
        future = now + timedelta(hours=hours)
        return [e for e in self.events if now <= e.start_time <= future]

    def check_storage_capacity(self) -> bool:
        """Check if storage capacity is sufficient for upcoming recordings"""
        # Get storage paths and check capacity for each
        storage_paths = self.storage_handler.get_storage_paths_from_config(self.device.id)
        storage_status = self.storage_manager.check_storage_health()

        # Check each storage device
        for storage_type in ['storage1', 'storage2']:
            if storage_type in storage_status:
                status = storage_status[storage_type]
                
                if not status['healthy']:
                    self.logger.warning(f"{storage_type} health check failed")
                    return False

                # Get capacity info
                try:
                    capacity = self.device.get_param(f"eParamID_{storage_type}Capacity")
                    free_space = self.device.get_param(f"eParamID_{storage_type}FreeSpace")
                    
                    if capacity and free_space:
                        used_percent = ((capacity - free_space) / capacity) * 100
                        free_gb = free_space / (1024 * 1024 * 1024)  # Convert to GB
                        
                        self.logger.info(f"{storage_type} status:")
                        self.logger.info(f"Total capacity: {capacity/(1024*1024*1024):.2f} GB")
                        self.logger.info(f"Free space: {free_gb:.2f} GB")
                        self.logger.info(f"Used: {used_percent:.1f}%")

                        if used_percent > 80:
                            self.logger.warning(f"{storage_type} usage above 80%")
                            return False
                            
                        if free_gb < 5:
                            self.logger.warning(f"{storage_type} has less than 5GB remaining")
                            return False

                except Exception as e:
                    self.logger.error(f"Failed to get storage info for {storage_type}: {str(e)}")
                    return False

        return True
        return True

    def get_alerts(self) -> List[str]:
        """Get list of active alerts"""
        alerts = []
        
        if not self.check_storage_capacity():
            alerts.append("Low storage capacity for upcoming recordings")
            
        upcoming = self.get_upcoming_events(1)  # Next hour
        if upcoming:
            alerts.append(f"Upcoming event: {upcoming[0].title} at {upcoming[0].start_time}")
            
        return alerts

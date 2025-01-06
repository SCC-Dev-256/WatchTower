import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MeetingSource(Enum):
    RSS = "rss"
    CALENDAR = "calendar"
    
@dataclass
class MeetingInfo:
    title: str
    date: datetime
    location: Optional[str]
    meeting_type: Optional[str]
    description: Optional[str]
    source_url: str
    source_type: MeetingSource

class DateScraper:
    def __init__(self):
        self.sources = {
            "oakdale": {
                "url": "https://oakdalemn.gov/rss.aspx#agendaCenter",
                "type": MeetingSource.RSS
            },
            "mahtomedi": {
                "url": "https://mahtomedi.gov/rss.aspx#agendaCenter", 
                "type": MeetingSource.RSS
            },
            "white_bear_township": {
                "url": "http://www.ci.white-bear-township.mn.us/rss.aspx#calendar",
                "type": MeetingSource.RSS
            },  
            "birchwood": {
                "url": "https://cityofbirchwood.com/general-city-information/city-council/participating-in-city-council-meetings/",
                "type": MeetingSource.CALENDAR
            },
            "lake_elmo": {
                "url": "https://www.lakeelmo.gov/calendar_app/index.html",
                "type": MeetingSource.CALENDAR
            },
            "white_bear": {
                "url": "https://whitebearlake.org/calendar.php",
                "type": MeetingSource.CALENDAR
            }
        }

    def fetch_meetings(self, source_name: str) -> List[MeetingInfo]:
        """Fetch meetings from a specific source"""
        try:
            source = self.sources.get(source_name)
            if not source:
                logger.error(f"Unknown source: {source_name}")
                return []
                
            if source["type"] == MeetingSource.RSS:
                return self._parse_rss(source["url"])
            else:
                return self._scrape_calendar(source["url"])
                
        except Exception as e:
            logger.error(f"Error fetching meetings from {source_name}: {str(e)}")
            return []

    def _parse_rss(self, url: str) -> List[MeetingInfo]:
        """Parse meetings from RSS feed"""
        meetings = []
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            try:
                date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                meeting = MeetingInfo(
                    title=entry.title,
                    date=date,
                    location=entry.get("location"),
                    meeting_type=self._extract_meeting_type(entry.title),
                    description=entry.get("description"),
                    source_url=url,
                    source_type=MeetingSource.RSS
                )
                meetings.append(meeting)
            except Exception as e:
                logger.warning(f"Failed to parse RSS entry: {str(e)}")
                continue
                
        return meetings

    def _scrape_calendar(self, url: str) -> List[MeetingInfo]:
        """Scrape meetings from calendar webpage"""
        meetings = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common calendar event containers
        events = soup.find_all(['div', 'article'], class_=lambda x: x and 
            ('event' in x.lower() or 'calendar' in x.lower()))
            
        for event in events:
            try:
                # Extract meeting details - adjust selectors based on site structure
                title = event.find(['h3', 'h4', 'div'], class_='title')
                date_elem = event.find(['span', 'div'], class_='date')
                location = event.find(['span', 'div'], class_='location')
                desc = event.find(['div', 'p'], class_='description')
                
                if title and date_elem:
                    # Parse date from text - adjust format as needed
                    date = self._parse_date(date_elem.text.strip())
                    
                    meeting = MeetingInfo(
                        title=title.text.strip(),
                        date=date,
                        location=location.text.strip() if location else None,
                        meeting_type=self._extract_meeting_type(title.text.strip()),
                        description=desc.text.strip() if desc else None,
                        source_url=url,
                        source_type=MeetingSource.CALENDAR
                    )
                    meetings.append(meeting)
            except Exception as e:
                logger.warning(f"Failed to parse calendar event: {str(e)}")
                continue
                
        return meetings

    def _extract_meeting_type(self, title: str) -> Optional[str]:
        """Extract meeting type from title"""
        common_types = ["Council", "Board", "Commission", "Committee"]
        title_lower = title.lower()
        
        for type_ in common_types:
            if type_.lower() in title_lower:
                return type_
        return None

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        # Try common date formats
        formats = [
            "%B %d, %Y %I:%M %p",
            "%Y-%m-%d %H:%M",
            "%m/%d/%Y %I:%M %p"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        raise ValueError(f"Unable to parse date: {date_str}")

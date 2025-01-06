import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import pdfplumber
from dateutil.relativedelta import relativedelta
import re
from dateutil import parser as date_parser
from flask_caching import Cache
from app.services.scheduling.website_db.citysite import CitySiteDB

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
    def __init__(self, cache: Cache):
        self.city_db = CitySiteDB(cache)
        self.logger = logging.getLogger(__name__)
        self.cache = cache

    def fetch_meetings(self, source_name: str) -> List[MeetingInfo]:
        """Fetch meetings from a specific source"""
        try:
            source = self.city_db.get_website(source_name)
            if not source:
                logger.error(f"Unknown source: {source_name}")
                return []
                
            cache_key = f"meetings_{source_name}"
            cached_meetings = self.cache.get(cache_key)
            if cached_meetings:
                return cached_meetings

            if source.source_type == MeetingSource.RSS:
                meetings = self._parse_rss(source.url)
            else:
                meetings = self._scrape_calendar(source.url)

            self.cache.set(cache_key, meetings, timeout=3600)  # Cache for 1 hour
            return meetings
                
        except Exception as e:
            logger.error(f"Error fetching meetings from {source_name}: {str(e)}")
            return []

    def _parse_rss(self, url: str) -> List[MeetingInfo]:
        """Parse meetings from RSS feed"""
        meetings = []
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            try:
                date = date_parser.parse(entry.published)
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
        try:
            return date_parser.parse(date_str)
        except ValueError as e:
            logger.error(f"Unable to parse date: {date_str} - {str(e)}")
            raise

    def fetch_birchwood_meetings(self) -> List[MeetingInfo]:
        """Fetch Birchwood meetings, attempting PDF scraping first, then fallback to pattern generation."""
        try:
            source = self.city_db.get_website("birchwood")
            if not source:
                raise ValueError("Birchwood source not found in database")
                
            meetings = self._scrape_pdf(source.url)

            if not meetings:
                # If no meetings were found in the PDF, generate based on a regular pattern
                start_date = datetime.now().replace(day=2, hour=18, minute=45)  # Example start date
                meetings = self._generate_regular_meetings(start_date, 12, source.url)  # Generate for the next 12 months

            return meetings
        except Exception as e:
            self.logger.error(f"Failed to fetch Birchwood meetings: {str(e)}")
            return []

    def _scrape_pdf(self, url: str) -> List[MeetingInfo]:
        """Scrape meeting dates from a PDF document."""
        meetings = []
        response = requests.get(url)
        with pdfplumber.open(response.content) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Implement logic to parse dates from text
                for line in text.split('\n'):
                    if "meeting" in line.lower():
                        # Extract date and time from the line
                        date_str = self._extract_date_from_text(line)
                        if date_str:
                            date = date_parser.parse(date_str)
                            meeting = MeetingInfo(
                                title="Birchwood Meeting",
                                date=date,
                                location="Birchwood City Hall",
                                meeting_type="Council",
                                description="Monthly council meeting",
                                source_url=url,
                                source_type=MeetingSource.CALENDAR
                            )
                            meetings.append(meeting)
        return meetings

    def _extract_date_from_text(self, text: str) -> str:
        """Extract date string from text."""
        # Use regex to match date patterns
        match = re.search(r'\b\w+ \d{1,2}, \d{4} \d{1,2}:\d{2} [APap][Mm]\b', text)
        return match.group(0) if match else None

    def _generate_regular_meetings(self, start_date: datetime, months: int, source_url: str) -> List[MeetingInfo]:
        """Generate meeting dates based on a regular pattern."""
        meetings = []
        for i in range(months):
            meeting_date = start_date + relativedelta(months=i)
            meeting = MeetingInfo(
                title="Birchwood Regular Meeting",
                date=meeting_date,
                location="Birchwood City Hall",
                meeting_type="Council",
                description="Regular monthly meeting",
                source_url=source_url,
                source_type=MeetingSource.CALENDAR
            )
            meetings.append(meeting)
        return meetings

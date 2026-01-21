"""
Validation utilities for user inputs and queries.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


class DateValidator:
    """Validate and parse date inputs."""
    
    @staticmethod
    def parse_relative_date(text: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Parse relative date expressions like 'last month', 'this year', etc.
        
        Args:
            text: Text containing date expression
            
        Returns:
            Tuple of (start_date, end_date) or None if not parseable
        """
        text = text.lower()
        now = datetime.now()
        
        # Current month
        if 'this month' in text or 'current month' in text:
            start = datetime(now.year, now.month, 1)
            return (start, now)
        
        # Last month
        if 'last month' in text or 'previous month' in text:
            first_day_current = datetime(now.year, now.month, 1)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = datetime(last_day_previous.year, last_day_previous.month, 1)
            return (first_day_previous, last_day_previous)
        
        # This year
        if 'this year' in text or 'current year' in text:
            start = datetime(now.year, 1, 1)
            return (start, now)
        
        # Last year
        if 'last year' in text or 'previous year' in text:
            start = datetime(now.year - 1, 1, 1)
            end = datetime(now.year - 1, 12, 31)
            return (start, end)
        
        # Last N days
        days_match = re.search(r'last (\d+) days?', text)
        if days_match:
            days = int(days_match.group(1))
            start = now - timedelta(days=days)
            return (start, now)
        
        # Last N weeks
        weeks_match = re.search(r'last (\d+) weeks?', text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            start = now - timedelta(weeks=weeks)
            return (start, now)
        
        # Last N months (approximate)
        months_match = re.search(r'last (\d+) months?', text)
        if months_match:
            months = int(months_match.group(1))
            start = now - timedelta(days=months * 30)
            return (start, now)
        
        return None
    
    @staticmethod
    def parse_absolute_date(text: str) -> Optional[datetime]:
        """
        Parse absolute date strings.
        
        Args:
            text: Date string
            
        Returns:
            Datetime object or None
        """
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def validate_date_range(start: datetime, end: datetime) -> bool:
        """
        Validate that date range is logical.
        
        Args:
            start: Start date
            end: End date
            
        Returns:
            True if valid
        """
        if start > end:
            return False
        
        # Check if range is too large (e.g., more than 5 years)
        if (end - start).days > 365 * 5:
            return False
        
        # Check if end date is in the future (more than 1 day)
        if end > datetime.now() + timedelta(days=1):
            return False
        
        return True


class QueryValidator:
    """Validate user queries and inputs."""
    
    @staticmethod
    def is_command(text: str) -> bool:
        """
        Check if text is a command.
        
        Args:
            text: Text to check
            
        Returns:
            True if it's a command
        """
        return text.strip().startswith('/')
    
    @staticmethod
    def extract_command(text: str) -> Tuple[str, str]:
        """
        Extract command and arguments from text.
        
        Args:
            text: Command text
            
        Returns:
            Tuple of (command, arguments)
        """
        parts = text.strip().split(maxsplit=1)
        command = parts[0].lstrip('/')
        args = parts[1] if len(parts) > 1 else ''
        return (command, args)
    
    @staticmethod
    def validate_prediction_days(days: int) -> Tuple[bool, Optional[str]]:
        """
        Validate number of days for prediction.
        
        Args:
            days: Number of days
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if days < 1:
            return (False, "Prediction period must be at least 1 day")
        
        if days > 90:
            return (False, "Prediction period cannot exceed 90 days")
        
        return (True, None)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove any null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length]
        
        # Strip excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def extract_numbers(text: str) -> list:
        """
        Extract all numbers from text.
        
        Args:
            text: Text to parse
            
        Returns:
            List of integers found
        """
        return [int(n) for n in re.findall(r'\d+', text)]
    
    @staticmethod
    def contains_keywords(text: str, keywords: list) -> bool:
        """
        Check if text contains any of the keywords.
        
        Args:
            text: Text to check
            keywords: List of keywords
            
        Returns:
            True if any keyword is found
        """
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

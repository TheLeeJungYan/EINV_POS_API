import re
from datetime import datetime
from .exceptions import ValidationError

class DataValidator:
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_ic_number(ic_number: str) -> bool:
        """Validate IC number format"""
        ic_pattern = r'^\d{6}-\d{2}-\d{4}$'
        return bool(re.match(ic_pattern, ic_number))

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        phone_pattern = r'^\+?[\d\s-]{8,20}$'
        return bool(re.match(phone_pattern, phone))

    @staticmethod
    def validate_postal_code(postal_code: str) -> bool:
        """Validate postal code format"""
        postal_pattern = r'^\d{5}$'
        return bool(re.match(postal_pattern, postal_code))
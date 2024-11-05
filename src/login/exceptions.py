class LoginError(Exception):
    """Base exception for login errors"""
    pass

class AuthorizationError(Exception):
    """Raise exception for login errors"""
    pass

class InternalServerError(Exception):
    """Raised for general internal server errors."""
    pass

class ValidationError(LoginError):
    """Raised when validation fails"""
    pass

class AuthenticationError(LoginError):
    """Raised when authentication fails"""
    pass

class RegistrationError(LoginError):
    """Raised when registration fails"""
    pass

class SecurityError(LoginError):
    """Raised when security-related operations fail"""
    pass
# src/login/security.py

import bcrypt
import hashlib
import base64
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta
from .exceptions import AuthenticationError, SecurityError
import re
from jwt.exceptions import InvalidTokenError

class SecurityManager:
    def __init__(self, 
                 secret_key: str,
                 min_password_length: int = 8,
                 token_expiry: timedelta = timedelta(hours=24),
                 bcrypt_rounds: int = 12):
        """
        Initialize SecurityManager with configurable parameters
        
        Args:
            secret_key: Key for JWT token signing
            min_password_length: Minimum required password length
            token_expiry: Default token expiration time
            bcrypt_rounds: Number of rounds for bcrypt
        """
        self.secret_key = secret_key
        self.MIN_PASSWORD_LENGTH = min_password_length
        self.DEFAULT_TOKEN_EXPIRY = token_expiry
        self.BCRYPT_ROUNDS = bcrypt_rounds
        
        # Regular expressions for password validation
        self.password_patterns = {
            'uppercase': re.compile(r'[A-Z]'),
            'lowercase': re.compile(r'[a-z]'),
            'number': re.compile(r'\d'),
            'special': re.compile(r'[!@#$%^&*(),.?":{}|<>]')
        }

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password meets security requirements
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if len(password) < self.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters long"
            
        checks = {
            'uppercase': "an uppercase letter",
            'lowercase': "a lowercase letter",
            'number': "a number",
            'special': "a special character"
        }
        
        for pattern_name, requirement in checks.items():
            if not self.password_patterns[pattern_name].search(password):
                return False, f"Password must contain at least {requirement}"
                
        return True, "Password meets security requirements"

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt with additional security measures
        
        Args:
            password: Plain text password
            
        Returns:
            str: Base64 encoded hash
            
        Raises:
            SecurityError: If password doesn't meet requirements or hashing fails
        """
        try:
            # Validate password strength
            is_valid, message = self.validate_password_strength(password)
            if not is_valid:
                raise SecurityError(message)
            
            # Add pepper (additional secret) and use SHA-256
            peppered = f"{password}{self.secret_key}"
            sha256_hash = hashlib.sha256(peppered.encode('utf-8')).digest()
            
            # Use bcrypt with configured rounds
            salt = bcrypt.gensalt(rounds=self.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(sha256_hash, salt)
            
            # Return base64 encoded hash
            return base64.b64encode(hashed).decode('utf-8')
            
        except Exception as e:
            raise SecurityError(f"Password hashing failed: {str(e)}")

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            password: Plain text password to verify
            stored_hash: Base64 encoded hash from database
            
        Returns:
            bool: True if password matches
            
        Raises:
            SecurityError: If verification process fails
        """
        try:
            # Add pepper and use SHA-256 (same as in hash_password)
            peppered = f"{password}{self.secret_key}"
            sha256_hash = hashlib.sha256(peppered.encode('utf-8')).digest()
            
            # Decode stored hash from base64
            stored_bytes = base64.b64decode(stored_hash.encode('utf-8'))
            
            # Verify with bcrypt
            return bcrypt.checkpw(sha256_hash, stored_bytes)
            
        except Exception as e:
            raise SecurityError(f"Password verification failed: {str(e)}")

    def create_access_token(self, 
                          data: Dict[str, Any], 
                          expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token with security claims
        
        Args:
            data: Payload data
            expires_delta: Optional custom expiration time
            
        Returns:
            str: JWT token
            
        Raises:
            SecurityError: If token creation fails
        """
        try:
            to_encode = data.copy()
            issued_at = datetime.datetime.now(datetime.timezone.utc)
            expiration = issued_at + (expires_delta or self.DEFAULT_TOKEN_EXPIRY)
            
            # Add security claims
            to_encode.update({
                "exp": expiration,
                "iat": issued_at,
                "type": "access",
                "jti": hashlib.sha256(str(issued_at.timestamp()).encode()).hexdigest()  # Unique token ID
            })
            
            return jwt.encode(
                to_encode,
                self.secret_key,
                algorithm="HS256",
                headers={
                    "kid": "v1",  # Key ID for key rotation
                    "typ": "JWT"
                }
            )
        except Exception as e:
            raise SecurityError(f"Token creation failed: {str(e)}")

    def verify_token(self, token: str, verify_type: bool = True) -> Dict[str, Any]:
        """
        Verify JWT token and its claims
        
        Args:
            token: JWT token to verify
            verify_type: Whether to verify token type claim
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "type", "jti"]
                }
            )
            
            # Verify token type if required
            if verify_type and payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    def refresh_token(self, token: str) -> str:
        """
        Refresh an existing token
        
        Args:
            token: Existing valid token
            
        Returns:
            str: New token
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        try:
            # Verify existing token
            payload = self.verify_token(token)
            
            # Remove old JWT-specific claims
            for claim in ['exp', 'iat', 'jti', 'type']:
                payload.pop(claim, None)
                
            # Create new token with same data
            return self.create_access_token(payload)
            
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
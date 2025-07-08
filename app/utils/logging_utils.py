import logging
import re
from typing import Any, Dict, Optional
from uuid import UUID

class SecureLogger:
    """Secure logger that masks sensitive information."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
     
    @staticmethod
    def mask_uuid(uuid_str: str) -> str:
        """Mask UUID showing only first 8 characters."""
        if not uuid_str:
            return ""
        return f"{str(uuid_str)[:8]}***"
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email showing only first 2 chars and domain."""
        if not email or "@" not in email:
            return "***"
        local, domain = email.split("@", 1)
        return f"{local[:3]}***@{domain}"
    
    @staticmethod
    def mask_token(token: str) -> str:
        """Mask token showing only first 10 characters."""
        if not token:
            return ""
        return f"{token[:10]}***"
    
    @staticmethod
    def mask_password(password: str) -> str:
        """Completely mask password."""
        return "***MASKED***"
    
    @staticmethod
    def mask_message_content(content: str, max_length: int = 50) -> str:
        """Mask long message content."""
        if not content:
            return ""
        if len(content) <= max_length:
            return content
        return f"{content[:max_length]}..."
    
    @staticmethod
    def sanitize_data(data: Any) -> Any:
        """Sanitize data for logging."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in ['password', 'token', 'secret', 'key']):
                    sanitized[key] = "***MASKED***"
                elif 'email' in key_lower:
                    sanitized[key] = SecureLogger.mask_email(str(value))
                elif 'id' in key_lower and isinstance(value, (str, UUID)):
                    sanitized[key] = SecureLogger.mask_uuid(str(value))
                elif 'content' in key_lower and isinstance(value, str):
                    sanitized[key] = SecureLogger.mask_message_content(value)
                else:
                    sanitized[key] = SecureLogger.sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [SecureLogger.sanitize_data(item) for item in data]
        elif isinstance(data, (str, UUID)) and len(str(data)) == 36:  # UUID length
            return SecureLogger.mask_uuid(str(data))
        else:
            return data
    
    def info(self, message: str, **kwargs):
        """Log info message with sanitized data."""
        sanitized_kwargs = self.sanitize_data(kwargs)
        self.logger.info(f"{message} {sanitized_kwargs}" if sanitized_kwargs else message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with sanitized data."""
        sanitized_kwargs = self.sanitize_data(kwargs)
        self.logger.debug(f"{message} {sanitized_kwargs}" if sanitized_kwargs else message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with sanitized data."""
        sanitized_kwargs = self.sanitize_data(kwargs)
        self.logger.warning(f"{message} {sanitized_kwargs}" if sanitized_kwargs else message)
    
    def error(self, message: str, **kwargs):
        """Log error message with sanitized data."""
        sanitized_kwargs = self.sanitize_data(kwargs)
        self.logger.error(f"{message} {sanitized_kwargs}" if sanitized_kwargs else message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with sanitized data."""
        sanitized_kwargs = self.sanitize_data(kwargs)
        self.logger.critical(f"{message} {sanitized_kwargs}" if sanitized_kwargs else message)

def get_secure_logger(name: str) -> SecureLogger:
    """Get a secure logger instance."""
    return SecureLogger(name)

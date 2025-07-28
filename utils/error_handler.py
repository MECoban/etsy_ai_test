"""
Error handling utilities for Etsy AI Assistant
"""
import streamlit as st
import time


class EtsyAIError(Exception):
    """Base exception class for Etsy AI application"""
    def __init__(self, message, error_code=None, context=None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)


class APIError(EtsyAIError):
    """API related errors"""
    pass


class ValidationError(EtsyAIError):
    """Input validation errors"""
    pass


class CacheError(EtsyAIError):
    """Cache related errors"""
    pass


def log_error(error, context=None):
    """Log error with context for debugging"""
    if 'error_log' not in st.session_state:
        st.session_state['error_log'] = []
    
    error_entry = {
        'timestamp': time.time(),
        'error_type': type(error).__name__,
        'message': str(error),
        'context': context or {},
        'stack_trace': None
    }
    
    # Add to error log (keep last 50 errors)
    st.session_state['error_log'].insert(0, error_entry)
    if len(st.session_state['error_log']) > 50:
        st.session_state['error_log'] = st.session_state['error_log'][:50]


def display_error(error, show_details=False):
    """Display user-friendly error messages"""
    error_messages = {
        'quota': {
            'title': '🚫 API Quota Exceeded',
            'message': 'Your OpenAI API quota has been reached. Please check your billing settings.',
            'action': 'Visit OpenAI dashboard to upgrade your plan.'
        },
        'network': {
            'title': '🌐 Connection Error',
            'message': 'Unable to connect to OpenAI services. Please check your internet connection.',
            'action': 'Try again in a few moments.'
        },
        'invalid_input': {
            'title': '⚠️ Invalid Input',
            'message': 'Please check your input and try again.',
            'action': 'Ensure all required fields are filled correctly.'
        },
        'api_key': {
            'title': '🔑 API Key Error',
            'message': 'OpenAI API key is missing or invalid.',
            'action': 'Please check your .env file and ensure OPENAI_API_KEY is set correctly.'
        },
        'generic': {
            'title': '❌ Error Occurred',
            'message': 'An unexpected error occurred.',
            'action': 'Please try again or contact support if the problem persists.'
        }
    }
    
    # Determine error type
    error_type = 'generic'
    error_str = str(error).lower()
    
    if 'quota' in error_str or 'billing' in error_str:
        error_type = 'quota'
    elif 'connection' in error_str or 'network' in error_str:
        error_type = 'network'
    elif 'validation' in error_str or 'invalid' in error_str:
        error_type = 'invalid_input'
    elif 'api_key' in error_str or 'authentication' in error_str:
        error_type = 'api_key'
    
    error_info = error_messages[error_type]
    
    st.error(f"{error_info['title']}\n\n{error_info['message']}")
    st.info(f"💡 **Action:** {error_info['action']}")
    
    if show_details:
        with st.expander("🔍 Technical Details", expanded=False):
            st.code(str(error))


def validate_input(value, validation_type, field_name="Input"):
    """Validate user inputs"""
    if validation_type == 'required':
        if not value or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} is required")
    
    elif validation_type == 'max_length':
        max_len = 1000  # Default max length
        if isinstance(value, str) and len(value) > max_len:
            raise ValidationError(f"{field_name} must be less than {max_len} characters")
    
    elif validation_type == 'min_length':
        min_len = 10
        if isinstance(value, str) and len(value) < min_len:
            raise ValidationError(f"{field_name} must be at least {min_len} characters")
    
    elif validation_type == 'email':
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(f"{field_name} must be a valid email address")
    
    return True


def handle_api_response(response, expected_format='text'):
    """Handle and validate API responses"""
    try:
        if expected_format == 'text':
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            else:
                raise APIError("Invalid response format from API")
        
        elif expected_format == 'image':
            if hasattr(response, 'data') and response.data:
                return response.data[0].url
            else:
                raise APIError("Invalid image response from API")
        
        return response
        
    except Exception as e:
        raise APIError(f"Failed to process API response: {str(e)}")


def create_error_report():
    """Create detailed error report for debugging"""
    if 'error_log' not in st.session_state or not st.session_state['error_log']:
        return "No errors recorded"
    
    recent_errors = st.session_state['error_log'][:10]
    
    report = f"# Error Report\n\n"
    report += f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Total Errors:** {len(st.session_state['error_log'])}\n\n"
    
    for i, error in enumerate(recent_errors):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(error['timestamp']))
        report += f"## Error {i+1}\n"
        report += f"**Time:** {timestamp}\n"
        report += f"**Type:** {error['error_type']}\n"
        report += f"**Message:** {error['message']}\n"
        if error['context']:
            report += f"**Context:** {error['context']}\n"
        report += "\n---\n\n"
    
    return report 
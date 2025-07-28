"""
Utils package for Etsy AI Assistant
Centralized utility functions and helpers
"""

# Import all utility modules
from .cache_utils import (
    generate_cache_key,
    get_from_cache,
    save_to_cache,
    clear_cache,
    get_cache_stats
)

from .rate_limiter import (
    RateLimiter,
    rate_limiter,
    throttled_api_call,
    get_rate_limit_status
)

from .error_handler import (
    EtsyAIError,
    APIError,
    ValidationError,
    CacheError,
    log_error,
    display_error,
    validate_input,
    handle_api_response,
    create_error_report
)

from .analytics import (
    init_analytics,
    track_api_call,
    track_feature_usage,
    get_analytics_summary,
    export_analytics_report,
    get_session_duration,
    get_feature_usage_stats,
    get_recent_api_calls
)

from .session_helpers import (
    init_session_state,
    get_form_data,
    set_form_data,
    save_generated_content,
    get_generated_content,
    should_regenerate,
    add_to_history,
    search_history,
    toggle_favorite,
    add_tag_to_entry,
    get_content_types_from_history,
    format_timestamp,
    clear_session_data
)

from .api_client import (
    get_openai_client,
    call_openai,
    generate_image,
    enhance_image
)

# Export all for easy imports
__all__ = [
    # Cache utils
    'generate_cache_key', 'get_from_cache', 'save_to_cache', 'clear_cache', 'get_cache_stats',
    
    # Rate limiter
    'RateLimiter', 'rate_limiter', 'throttled_api_call', 'get_rate_limit_status',
    
    # Error handling
    'EtsyAIError', 'APIError', 'ValidationError', 'CacheError',
    'log_error', 'display_error', 'validate_input', 'handle_api_response', 'create_error_report',
    
    # Analytics
    'init_analytics', 'track_api_call', 'track_feature_usage', 'get_analytics_summary',
    'export_analytics_report', 'get_session_duration', 'get_feature_usage_stats', 'get_recent_api_calls',
    
    # Session helpers
    'init_session_state', 'get_form_data', 'set_form_data', 'save_generated_content',
    'get_generated_content', 'should_regenerate', 'add_to_history', 'search_history',
    'toggle_favorite', 'add_tag_to_entry', 'get_content_types_from_history', 'format_timestamp',
    'clear_session_data',
    
    # API client
    'get_openai_client', 'call_openai', 'generate_image', 'enhance_image'
] 
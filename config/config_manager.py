"""
Central configuration manager for Etsy AI Assistant
"""
import streamlit as st
from .settings import *
from .translations import TRANSLATIONS, get_translation
from .env_config import load_environment, validate_environment, get_debug_mode


class ConfigManager:
    """Central configuration manager"""
    
    def __init__(self):
        self.debug = get_debug_mode()
        self._initialized = False
    
    def initialize(self):
        """Initialize configuration"""
        if self._initialized:
            return
        
        # Load environment
        load_environment()
        validate_environment()
        
        # Set page config
        st.set_page_config(**PAGE_CONFIG)
        
        self._initialized = True
    
    def get_translation(self, key, language=None):
        """Get translation with fallback"""
        if language is None:
            language = st.session_state.get('language', DEFAULT_LANGUAGE)
        return get_translation(key, language)
    
    def get_supported_languages(self):
        """Get supported languages"""
        return SUPPORTED_LANGUAGES
    
    def get_api_settings(self):
        """Get API configuration"""
        return {
            'model': OPENAI_MODEL,
            'temperature': OPENAI_TEMPERATURE,
            'max_tokens': MAX_TOKENS_DEFAULT
        }
    
    def get_rate_limit_settings(self):
        """Get rate limiting configuration"""
        return {
            'max_requests': RATE_LIMIT_REQUESTS,
            'window_seconds': RATE_LIMIT_WINDOW
        }
    
    def get_cache_settings(self):
        """Get cache configuration"""
        return {
            'expiry_hours': CACHE_EXPIRY_HOURS,
            'max_entries': MAX_CACHE_ENTRIES
        }
    
    def get_validation_settings(self):
        """Get validation configuration"""
        return {
            'min_description_length': MIN_DESCRIPTION_LENGTH,
            'max_description_length': MAX_DESCRIPTION_LENGTH,
            'min_category_length': MIN_CATEGORY_LENGTH,
            'min_audience_length': MIN_AUDIENCE_LENGTH,
            'min_theme_length': MIN_THEME_LENGTH
        }
    
    def get_etsy_settings(self):
        """Get Etsy-specific configuration"""
        return {
            'title_max_chars': ETSY_TITLE_MAX_CHARS,
            'title_min_chars': ETSY_TITLE_MIN_CHARS,
            'max_tags': ETSY_MAX_TAGS,
            'tag_max_chars': ETSY_TAG_MAX_CHARS,
            'image_size': ETSY_IMAGE_SIZE
        }
    
    def get_image_settings(self):
        """Get image generation configuration"""
        return {
            'dalle_sizes': DALLE_IMAGE_SIZES,
            'default_size': DEFAULT_IMAGE_SIZE
        }
    
    def get_batch_settings(self):
        """Get batch operation configuration"""
        return {
            'max_batch_size': MAX_BATCH_SIZE,
            'delay_seconds': BATCH_DELAY_SECONDS
        }
    
    def get_analytics_settings(self):
        """Get analytics configuration"""
        return {
            'max_api_call_history': MAX_API_CALL_HISTORY,
            'max_error_log_entries': MAX_ERROR_LOG_ENTRIES,
            'max_content_history': MAX_CONTENT_HISTORY
        }
    
    def get_feature_names(self):
        """Get feature names for analytics"""
        return FEATURE_NAMES
    
    def get_ui_settings(self):
        """Get UI configuration"""
        return {
            'sidebar_width': SIDEBAR_WIDTH,
            'content_max_chars_preview': CONTENT_MAX_CHARS_PREVIEW
        }
    
    def is_debug_mode(self):
        """Check if debug mode is enabled"""
        return self.debug
    
    def get_all_settings(self):
        """Get all configuration settings"""
        return {
            'app': {
                'title': APP_TITLE,
                'subtitle_en': APP_SUBTITLE_EN,
                'subtitle_tr': APP_SUBTITLE_TR
            },
            'api': self.get_api_settings(),
            'rate_limit': self.get_rate_limit_settings(),
            'cache': self.get_cache_settings(),
            'validation': self.get_validation_settings(),
            'etsy': self.get_etsy_settings(),
            'image': self.get_image_settings(),
            'batch': self.get_batch_settings(),
            'analytics': self.get_analytics_settings(),
            'ui': self.get_ui_settings(),
            'debug': self.is_debug_mode()
        }


# Global configuration manager instance
config = ConfigManager() 
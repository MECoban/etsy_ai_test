"""
Configuration settings for Etsy AI Assistant
"""

# App Settings
APP_TITLE = "🛍️ Etsy AI Listing Assistant"
APP_SUBTITLE_EN = "AI-powered assistance for all 13 steps of Etsy listing creation"
APP_SUBTITLE_TR = "Etsy listeleme oluşturmanın 13 adımının tümü için yapay zeka desteği"

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Etsy AI Listing Assistant",
    "page_icon": "🛍️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# API Settings
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7
MAX_TOKENS_DEFAULT = 800

# Rate Limiting
RATE_LIMIT_REQUESTS = 30  # requests per minute
RATE_LIMIT_WINDOW = 60    # seconds

# Cache Settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_ENTRIES = 100

# Analytics Settings
MAX_API_CALL_HISTORY = 50
MAX_ERROR_LOG_ENTRIES = 50
MAX_CONTENT_HISTORY = 100

# Validation Settings
MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 1000
MIN_CATEGORY_LENGTH = 3
MIN_AUDIENCE_LENGTH = 5
MIN_THEME_LENGTH = 3

# UI Settings
SIDEBAR_WIDTH = 400
CONTENT_MAX_CHARS_PREVIEW = 200

# Language Settings
DEFAULT_LANGUAGE = 'tr'
SUPPORTED_LANGUAGES = ['tr', 'en']

# File Settings
MAX_UPLOAD_SIZE_MB = 200
SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg']

# Etsy Specific Settings
ETSY_TITLE_MAX_CHARS = 140
ETSY_TITLE_MIN_CHARS = 130
ETSY_MAX_TAGS = 13
ETSY_TAG_MAX_CHARS = 20
ETSY_IMAGE_SIZE = "2000x2000"

# Image Generation Settings
DALLE_IMAGE_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
DEFAULT_IMAGE_SIZE = "1024x1024"

# Batch Operation Settings
MAX_BATCH_SIZE = 20
BATCH_DELAY_SECONDS = 1

# Feature Names for Analytics
FEATURE_NAMES = {
    'design_prompt': 'Design Prompt Generation',
    'title_generation': 'Title Generation', 
    'tag_generation': 'Tag Generation',
    'description_generation': 'Description Generation',
    'image_generation': 'Image Generation',
    'mockup_generation': 'Mockup Generation',
    'image_enhancement': 'Image Enhancement',
    'batch_operations': 'Batch Operations',
    'template_usage': 'Template Usage',
    'project_save': 'Project Save',
    'project_load': 'Project Load'
} 
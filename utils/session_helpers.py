"""
Session state helper functions for Etsy AI Assistant
"""
import streamlit as st
import time


def init_session_state():
    """Initialize all session state variables in one place"""
    defaults = {
        'language': 'tr',
        'api_cache': {},
        'cache_stats': {'hits': 0, 'misses': 0},
        'generated_content': {},  # Store generated content by type
        'form_data': {},  # Cache form inputs
        'ui_state': {
            'active_tab': 0,
            'last_generation_time': None,
            'generation_in_progress': False
        },
        'content_history': [],
        'saved_projects': {},
        'custom_templates': {},
        'analytics': {
            'session_start': time.time(),
            'page_views': 0,
            'api_calls': [],
            'feature_usage': {},
            'performance_metrics': []
        },
        'error_log': [],
        'rate_limit_requests': []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_form_data(key, default=""):
    """Get form data with caching"""
    return st.session_state['form_data'].get(key, default)


def set_form_data(key, value):
    """Set form data with change detection"""
    if st.session_state['form_data'].get(key) != value:
        st.session_state['form_data'][key] = value
        return True  # Value changed
    return False  # No change


def save_generated_content(content_type, content, metadata=None):
    """Save generated content with metadata"""
    st.session_state['generated_content'][content_type] = {
        'content': content,
        'timestamp': time.time(),
        'metadata': metadata or {}
    }


def get_generated_content(content_type):
    """Get previously generated content"""
    return st.session_state['generated_content'].get(content_type)


def should_regenerate(content_type, max_age_minutes=30):
    """Check if content should be regenerated based on age"""
    content = get_generated_content(content_type)
    if not content:
        return True
    
    age_minutes = (time.time() - content['timestamp']) / 60
    return age_minutes > max_age_minutes


def add_to_history(content_type, content, prompt_used=None, metadata=None):
    """Add content to history with enhanced metadata"""
    if 'content_history' not in st.session_state:
        st.session_state['content_history'] = []
    
    history_entry = {
        'id': f"{content_type}_{int(time.time())}",
        'content_type': content_type,
        'content': content,
        'prompt_used': prompt_used,
        'timestamp': time.time(),
        'metadata': metadata or {},
        'favorited': False,
        'tags': []
    }
    
    # Add to beginning of list (newest first)
    st.session_state['content_history'].insert(0, history_entry)
    
    # Keep only last 100 items to prevent memory issues
    if len(st.session_state['content_history']) > 100:
        st.session_state['content_history'] = st.session_state['content_history'][:100]


def search_history(query):
    """Search through history"""
    if 'content_history' not in st.session_state:
        return []
    
    query = query.lower()
    results = []
    
    for entry in st.session_state['content_history']:
        # Search in content, content_type, and tags
        if (query in entry.get('content', '').lower() or 
            query in entry.get('content_type', '').lower() or
            query in ' '.join(entry.get('tags', [])).lower()):
            results.append(entry)
    
    return results


def toggle_favorite(entry_id):
    """Toggle favorite status of a history entry"""
    if 'content_history' not in st.session_state:
        return False
    
    for entry in st.session_state['content_history']:
        if entry['id'] == entry_id:
            entry['favorited'] = not entry.get('favorited', False)
            return True
    
    return False


def add_tag_to_entry(entry_id, tag):
    """Add tag to history entry"""
    if 'content_history' not in st.session_state:
        return False
    
    for entry in st.session_state['content_history']:
        if entry['id'] == entry_id:
            if 'tags' not in entry:
                entry['tags'] = []
            if tag not in entry['tags']:
                entry['tags'].append(tag)
            return True
    
    return False


def get_content_types_from_history():
    """Get all unique content types from history"""
    if 'content_history' not in st.session_state:
        return []
    
    types = set()
    for entry in st.session_state['content_history']:
        types.add(entry.get('content_type', 'Unknown'))
    
    return sorted(list(types))


def format_timestamp(timestamp):
    """Format timestamp for display"""
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))


def clear_session_data():
    """Clear all session data (for logout/reset)"""
    keys_to_keep = ['language']  # Keep language preference
    
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    # Reinitialize
    init_session_state() 
"""
Cache utility functions for Etsy AI Assistant
"""
import streamlit as st
import hashlib
import time


def generate_cache_key(system_prompt, user_prompt, max_tokens, temperature=0.7):
    """Generate a unique cache key for API calls"""
    content = f"{system_prompt}|{user_prompt}|{max_tokens}|{temperature}"
    return hashlib.md5(content.encode()).hexdigest()


def get_from_cache(cache_key):
    """Get response from cache if exists and not expired (24 hours)"""
    if cache_key in st.session_state['api_cache']:
        cached_data = st.session_state['api_cache'][cache_key]
        # Check if cache is still valid (24 hours)
        if time.time() - cached_data['timestamp'] < 86400:  # 24 hours
            st.session_state['cache_stats']['hits'] += 1
            return cached_data['response']
        else:
            # Remove expired cache
            del st.session_state['api_cache'][cache_key]
    return None


def save_to_cache(cache_key, response):
    """Save response to cache with timestamp"""
    st.session_state['api_cache'][cache_key] = {
        'response': response,
        'timestamp': time.time()
    }
    st.session_state['cache_stats']['misses'] += 1


def clear_cache():
    """Clear all cached data"""
    st.session_state['api_cache'] = {}
    st.session_state['cache_stats'] = {'hits': 0, 'misses': 0}


def get_cache_stats():
    """Get cache statistics"""
    cache_hits = st.session_state['cache_stats']['hits']
    cache_misses = st.session_state['cache_stats']['misses']
    total_calls = cache_hits + cache_misses
    
    if total_calls > 0:
        hit_rate = (cache_hits / total_calls) * 100
        return {
            'hit_rate': hit_rate,
            'hits': cache_hits,
            'total_calls': total_calls,
            'cache_size': len(st.session_state['api_cache'])
        }
    
    return {
        'hit_rate': 0,
        'hits': 0,
        'total_calls': 0,
        'cache_size': 0
    } 
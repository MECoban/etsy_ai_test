"""
Analytics and logging utilities for Etsy AI Assistant
"""
import streamlit as st
import time
import json


def init_analytics():
    """Initialize analytics system"""
    if 'analytics' not in st.session_state:
        st.session_state['analytics'] = {
            'session_start': time.time(),
            'page_views': 0,
            'api_calls': [],
            'feature_usage': {},
            'performance_metrics': []
        }


def track_api_call(endpoint, duration, success=True):
    """Track API call performance"""
    if 'analytics' not in st.session_state:
        init_analytics()
    
    call_data = {
        'timestamp': time.time(),
        'endpoint': endpoint,
        'duration': duration,
        'success': success
    }
    st.session_state['analytics']['api_calls'].append(call_data)
    
    # Keep only last 50 API calls
    if len(st.session_state['analytics']['api_calls']) > 50:
        st.session_state['analytics']['api_calls'] = st.session_state['analytics']['api_calls'][-50:]


def track_feature_usage(feature_name):
    """Track feature usage"""
    if 'analytics' not in st.session_state:
        init_analytics()
    
    current_count = st.session_state['analytics']['feature_usage'].get(feature_name, 0)
    st.session_state['analytics']['feature_usage'][feature_name] = current_count + 1


def get_analytics_summary():
    """Get analytics summary"""
    if 'analytics' not in st.session_state:
        return None
    
    analytics_data = st.session_state['analytics']
    api_calls = analytics_data['api_calls']
    
    if not api_calls:
        return {
            'session_duration': (time.time() - analytics_data['session_start']) / 60,
            'total_api_calls': 0,
            'avg_response_time': 0,
            'success_rate': 100,
            'most_used_feature': 'None'
        }
    
    successful_calls = [call for call in api_calls if call['success']]
    durations = [call['duration'] for call in successful_calls]
    
    feature_usage = analytics_data['feature_usage']
    most_used = max(feature_usage.items(), key=lambda x: x[1]) if feature_usage else ('None', 0)
    
    return {
        'session_duration': (time.time() - analytics_data['session_start']) / 60,
        'total_api_calls': len(api_calls),
        'avg_response_time': sum(durations) / len(durations) if durations else 0,
        'success_rate': (len(successful_calls) / len(api_calls)) * 100,
        'most_used_feature': most_used[0]
    }


def export_analytics_report():
    """Export analytics data as JSON"""
    if 'analytics' not in st.session_state:
        return "{}"
    
    analytics_data = st.session_state['analytics'].copy()
    analytics_data['exported_at'] = time.time()
    summary = get_analytics_summary()
    if summary:
        analytics_data['session_duration_minutes'] = summary['session_duration']
    
    return json.dumps(analytics_data, indent=2, ensure_ascii=False)


def get_session_duration():
    """Get current session duration in minutes"""
    if 'analytics' not in st.session_state:
        return 0
    return (time.time() - st.session_state['analytics']['session_start']) / 60


def get_feature_usage_stats():
    """Get feature usage statistics"""
    if 'analytics' not in st.session_state:
        return {}
    
    return st.session_state['analytics']['feature_usage']


def get_recent_api_calls(limit=10):
    """Get recent API calls"""
    if 'analytics' not in st.session_state:
        return []
    
    api_calls = st.session_state['analytics']['api_calls']
    return api_calls[-limit:] if api_calls else [] 
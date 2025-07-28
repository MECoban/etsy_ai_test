"""
Environment configuration management for Etsy AI Assistant
"""
import os
import streamlit as st
from dotenv import load_dotenv


def load_environment():
    """Load environment variables"""
    load_dotenv()


def get_openai_api_key():
    """Get OpenAI API key with validation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("🔑 OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        st.stop()
    return api_key


def get_app_port():
    """Get application port"""
    return int(os.getenv("PORT", 8501))


def get_debug_mode():
    """Get debug mode setting"""
    return os.getenv("DEBUG", "false").lower() == "true"


def get_environment_type():
    """Get environment type (development/production)"""
    return os.getenv("ENVIRONMENT", "development")


def validate_environment():
    """Validate required environment variables"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        st.info("Please create a .env file with the following variables:")
        st.code("\n".join([f"{var}=your_value_here" for var in missing_vars]))
        st.stop()
    
    return True


def get_all_env_vars():
    """Get all relevant environment variables for debugging"""
    env_vars = {
        'OPENAI_API_KEY': '***' if os.getenv("OPENAI_API_KEY") else None,
        'PORT': os.getenv("PORT"),
        'DEBUG': os.getenv("DEBUG"),
        'ENVIRONMENT': os.getenv("ENVIRONMENT"),
    }
    
    return {k: v for k, v in env_vars.items() if v is not None} 
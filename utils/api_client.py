"""
API client utilities for Etsy AI Assistant
"""
import streamlit as st
from openai import OpenAI
import os
import time
from .error_handler import ValidationError, APIError, validate_input, handle_api_response, log_error, display_error
from .cache_utils import generate_cache_key, get_from_cache, save_to_cache
from .rate_limiter import throttled_api_call
from .analytics import track_api_call
from .session_helpers import add_to_history


# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    """Get cached OpenAI client"""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_openai(system_prompt, user_prompt, max_tokens=800, use_cache=True):
    """Enhanced OpenAI API call with comprehensive error handling"""
    try:
        # Input validation
        validate_input(system_prompt, 'required', 'System prompt')
        validate_input(user_prompt, 'required', 'User prompt')
        validate_input(system_prompt, 'max_length', 'System prompt')
        validate_input(user_prompt, 'max_length', 'User prompt')
        
        client = get_openai_client()
        
        if use_cache:
            cache_key = generate_cache_key(system_prompt, user_prompt, max_tokens)
            cached_response = get_from_cache(cache_key)
            if cached_response:
                return cached_response
        
        # API call with retry logic
        def _make_api_call():
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return handle_api_response(response, 'text')
        
        # Use throttled API call with rate limiting and track performance
        start_time = time.time()
        result = throttled_api_call(_make_api_call)
        duration = time.time() - start_time
        
        # Track API call analytics
        track_api_call("openai_chat", duration, success=bool(result))
        
        if use_cache and result:
            save_to_cache(cache_key, result)
        
        # Add to history
        add_to_history(
            content_type="ai_generation",
            content=result,
            prompt_used=f"System: {system_prompt[:100]}...\nUser: {user_prompt[:100]}...",
            metadata={'max_tokens': max_tokens, 'model': 'gpt-3.5-turbo'}
        )
        
        return result
        
    except ValidationError as e:
        log_error(e, {'system_prompt_length': len(system_prompt), 'user_prompt_length': len(user_prompt)})
        display_error(e)
        return None
        
    except APIError as e:
        log_error(e, {'model': 'gpt-3.5-turbo', 'max_tokens': max_tokens})
        display_error(e, show_details=True)
        return None
        
    except Exception as e:
        # Convert generic errors to APIError
        api_error = APIError(f"API call failed: {str(e)}")
        log_error(api_error, {'original_error': str(e), 'error_type': type(e).__name__})
        display_error(api_error, show_details=True)
        return None


def generate_image(prompt, size="1024x1024"):
    """Generate image using DALL-E 2"""
    try:
        client = get_openai_client()
        
        def _make_image_call():
            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                size=size,
                n=1
            )
            return handle_api_response(response, 'image')
        
        start_time = time.time()
        result = throttled_api_call(_make_image_call)
        duration = time.time() - start_time
        
        track_api_call("dalle_image", duration, success=bool(result))
        
        return result
        
    except Exception as e:
        api_error = APIError(f"Image generation failed: {str(e)}")
        log_error(api_error, {'prompt': prompt[:100], 'size': size})
        display_error(api_error, show_details=True)
        return None


def enhance_image(image_buffer, enhancement_prompt):
    """Enhance image using DALL-E 2 edit"""
    try:
        client = get_openai_client()
        
        def _make_edit_call():
            response = client.images.edit(
                model="dall-e-2",
                image=image_buffer,
                prompt=enhancement_prompt,
                size="1024x1024",
                n=1
            )
            return handle_api_response(response, 'image')
        
        start_time = time.time()
        result = throttled_api_call(_make_edit_call)
        duration = time.time() - start_time
        
        track_api_call("dalle_edit", duration, success=bool(result))
        
        return result
        
    except Exception as e:
        api_error = APIError(f"Image enhancement failed: {str(e)}")
        log_error(api_error, {'prompt': enhancement_prompt[:100]})
        display_error(api_error, show_details=True)
        return None 
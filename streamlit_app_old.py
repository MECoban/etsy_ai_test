import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import io
import requests
import hashlib
import json
import time

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Etsy AI Listing Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state with optimized structure
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
        }
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize session state
init_session_state()

# Language translations
translations = {
    "en": {
        "app_title": "🛍️ Etsy AI Listing Assistant",
        "app_subtitle": "AI-powered assistance for all 13 steps of Etsy listing creation",
        "language_selector": "🌍 Language",
        "product_info": "📋 Product Information",
        "product_description": "Product Description",
        "product_desc_placeholder": "Describe your product in detail...",
        "product_category": "Product Category",
        "product_cat_placeholder": "e.g., T-shirt, Jewelry, Home Decor",
        "target_audience": "Target Audience",
        "target_audience_placeholder": "e.g., Women, Men, Kids, Halloween lovers",
        "design_theme": "Design Theme/Style",
        "design_theme_placeholder": "e.g., Vintage, Minimalist, Gothic, Cute",
        "step": "Step",
        "generate": "🚀 Generate",
        "copy": "📋 Copy",
        "generating": "🔄 Generating...",
        "success": "✅ Success!",
        "error": "❌ Error:",
        "api_quota_error": "OpenAI API quota exceeded. Please check your billing.",
        "footer": "Made with ❤️ for Etsy sellers • © 2025"
    },
    "tr": {
        "app_title": "🛍️ Etsy Yapay Zeka Listeleme Asistanı",
        "app_subtitle": "Etsy listeleme oluşturmanın 13 adımının tümü için yapay zeka desteği",
        "language_selector": "🌍 Dil",
        "product_info": "📋 Ürün Bilgileri",
        "product_description": "Ürün Açıklaması",
        "product_desc_placeholder": "Ürününüzü detaylı bir şekilde açıklayın...",
        "product_category": "Ürün Kategorisi",
        "product_cat_placeholder": "örn., T-shirt, Takı, Ev Dekorasyonu",
        "target_audience": "Hedef Kitle",
        "target_audience_placeholder": "örn., Kadınlar, Erkekler, Çocuklar, Halloween severleri",
        "design_theme": "Tasarım Teması/Stili",
        "design_theme_placeholder": "örn., Vintage, Minimalist, Gotik, Sevimli",
        "step": "Adım",
        "generate": "🚀 Oluştur",
        "copy": "📋 Kopyala",
        "generating": "🔄 Oluşturuluyor...",
        "success": "✅ Başarılı!",
        "error": "❌ Hata:",
        "api_quota_error": "OpenAI API kotası aşıldı. Lütfen faturanızı kontrol edin.",
        "footer": "Etsy satıcıları için ❤️ ile yapıldı • © 2025"
    }
}

# Function to get translated text
def t(key):
    return translations[st.session_state['language']].get(key, key)

# Lazy load custom CSS for better performance
def load_custom_css():
    """Load custom CSS only when needed"""
    css_content = """
<style>
    .step-container {
        border: 2px solid #e6e6e6;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .step-header {
        color: #2c3e50;
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 15px;
        padding: 10px;
        background: white;
        border-radius: 10px;
        border-left: 5px solid #3498db;
    }
    .ai-output {
        background: #e8f4fd;
        border: 1px solid #3498db;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #2c3e50 !important;
        font-size: 14px;
        line-height: 1.6;
    }
    .ai-output * {
        color: #2c3e50 !important;
    }
    .tip-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: #856404 !important;
        font-weight: 500;
    }
    .tip-box * {
        color: #856404 !important;
    }
    .tip-box strong {
        color: #665408 !important;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724 !important;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 500;
    }
    
    /* Streamlit Form Elements */
    .stSelectbox > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stSelectbox > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    .stSelectbox > div > div > select {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    .stSelectbox > div > div > div {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    
    /* Text Input */
    .stTextInput > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Text Area */
    .stTextArea > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Number Input */
    .stNumberInput > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Slider */
    .stSlider > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* General text labels */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
    }
    .stMarkdown p {
        color: #ffffff !important;
    }
    .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3498db !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #2980b9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2c3e50 !important;
    }
    
    /* Main text color in dark theme */
    .main .block-container {
        color: #ffffff !important;
    }
    
    /* Dropdown options */
    .stSelectbox > div > div > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* File uploader */
    .stFileUploader > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Warning and error messages */
    .stAlert {
        color: #2c3e50 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
</style>
"""
    return css_content

# Apply CSS with lazy loading
@st.cache_data
def apply_custom_css():
    """Apply custom CSS with caching"""
    return load_custom_css()

# Load CSS
st.markdown(apply_custom_css(), unsafe_allow_html=True)

# Cache utility functions
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

# Session state optimization helpers
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

# Lazy loading helpers
def render_tab_content(tab_index, render_func):
    """Lazy render tab content only when active"""
    if 'active_tabs' not in st.session_state:
        st.session_state['active_tabs'] = set()
    
    # Mark tab as accessed
    st.session_state['active_tabs'].add(tab_index)
    
    # Only render if tab has been accessed
    if tab_index in st.session_state['active_tabs']:
        return render_func()
    else:
        st.info("Tab content will load when accessed...")
        return None

def lazy_component(component_id, render_func, trigger_condition=True):
    """Lazy load component based on condition"""
    if not trigger_condition:
        return None
    
    if f'lazy_{component_id}' not in st.session_state:
        st.session_state[f'lazy_{component_id}'] = True
        
    if st.session_state[f'lazy_{component_id}']:
        return render_func()
    
    return None

def memory_efficient_content_display(content, max_chars=1000):
    """Display content with expand/collapse for memory efficiency"""
    if not content or len(content) <= max_chars:
        return st.markdown(f'<div class="ai-output">{content}</div>', unsafe_allow_html=True)
    
    preview = content[:max_chars] + "..."
    
    with st.expander("📄 View Full Content", expanded=False):
        st.markdown(f'<div class="ai-output">{content}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="ai-output">{preview}</div>', unsafe_allow_html=True)

# Project Management System
def create_project_data():
    """Create project data structure from current session"""
    return {
        'project_name': '',
        'created_at': time.time(),
        'last_modified': time.time(),
        'language': st.session_state.get('language', 'tr'),
        'form_data': st.session_state.get('form_data', {}),
        'generated_content': st.session_state.get('generated_content', {}),
        'metadata': {
            'version': '1.0',
            'app_version': 'streamlit_v1',
            'total_generations': len(st.session_state.get('generated_content', {}))
        }
    }

def save_project(project_name):
    """Save current project to session state"""
    if 'saved_projects' not in st.session_state:
        st.session_state['saved_projects'] = {}
    
    project_data = create_project_data()
    project_data['project_name'] = project_name
    project_data['last_modified'] = time.time()
    
    st.session_state['saved_projects'][project_name] = project_data
    return True

def load_project(project_name):
    """Load project from saved data"""
    if 'saved_projects' not in st.session_state:
        return False
    
    if project_name not in st.session_state['saved_projects']:
        return False
    
    project_data = st.session_state['saved_projects'][project_name]
    
    # Restore form data
    st.session_state['form_data'] = project_data.get('form_data', {})
    
    # Restore generated content
    st.session_state['generated_content'] = project_data.get('generated_content', {})
    
    # Restore language
    st.session_state['language'] = project_data.get('language', 'tr')
    
    return True

def export_project(project_data):
    """Export project data as JSON"""
    return json.dumps(project_data, indent=2, ensure_ascii=False)

def import_project(json_data):
    """Import project data from JSON"""
    try:
        project_data = json.loads(json_data)
        
        # Validate required fields
        required_fields = ['project_name', 'form_data', 'generated_content']
        if not all(field in project_data for field in required_fields):
            return False, "Invalid project format"
        
        # Save to projects
        project_name = project_data['project_name']
        st.session_state['saved_projects'][project_name] = project_data
        
        return True, f"Project '{project_name}' imported successfully"
        
    except json.JSONDecodeError:
        return False, "Invalid JSON format"
    except Exception as e:
        return False, f"Import error: {str(e)}"

def get_project_summary(project_data):
    """Get summary of project content"""
    form_data = project_data.get('form_data', {})
    generated_content = project_data.get('generated_content', {})
    
    summary = {
        'product': form_data.get('product_description', 'N/A')[:50] + '...',
        'category': form_data.get('product_category', 'N/A'),
        'generated_items': len(generated_content),
        'last_modified': time.strftime('%Y-%m-%d %H:%M', 
                                     time.localtime(project_data.get('last_modified', 0)))
    }
    
    return summary

# Template System
def get_default_templates():
    """Get default prompt templates"""
    return {
        'design_prompts': {
            'vintage_t_shirt': {
                'name': 'Vintage T-Shirt Design',
                'category': 'Design',
                'prompt': 'Create a vintage-style t-shirt design featuring {theme} with distressed typography, retro color palette, and worn texture effects. Style: {style}. Target audience: {audience}.',
                'variables': ['theme', 'style', 'audience'],
                'description': 'Perfect for retro and vintage themed designs'
            },
            'minimalist_logo': {
                'name': 'Minimalist Logo Design',
                'category': 'Design',
                'prompt': 'Design a clean, minimalist logo for {business_type} featuring {elements}. Use simple geometric shapes, negative space, and a maximum of 2 colors. Style should be modern and professional.',
                'variables': ['business_type', 'elements'],
                'description': 'Clean and modern logo designs'
            },
            'halloween_graphic': {
                'name': 'Halloween Graphics',
                'category': 'Seasonal',
                'prompt': 'Create a spooky yet family-friendly Halloween design featuring {elements} with {color_scheme} colors. Include decorative borders and playful typography. Target: {target}.',
                'variables': ['elements', 'color_scheme', 'target'],
                'description': 'Seasonal Halloween designs'
            }
        },
        'title_prompts': {
            'seo_optimized': {
                'name': 'SEO Optimized Title',
                'category': 'SEO',
                'prompt': 'Create a high-converting Etsy title (130-140 chars) for {product} targeting {audience}. Include: main keyword, style ({style}), usage occasion, and gift potential. Focus on search volume.',
                'variables': ['product', 'audience', 'style'],
                'description': 'Maximize Etsy search visibility'
            },
            'seasonal_title': {
                'name': 'Seasonal Title',
                'category': 'Seasonal',
                'prompt': 'Create a seasonal Etsy title for {product} perfect for {season}/{holiday}. Include trending seasonal keywords, gift suggestions, and urgency elements. Target: {audience}.',
                'variables': ['product', 'season', 'holiday', 'audience'],
                'description': 'Capitalize on seasonal trends'
            }
        },
        'description_prompts': {
            'story_driven': {
                'name': 'Story-Driven Description',
                'category': 'Description',
                'prompt': 'Write an engaging Etsy product description for {product} that tells a story. Include: emotional connection, use cases, quality details, and call-to-action. Target: {audience}.',
                'variables': ['product', 'audience'],
                'description': 'Build emotional connection with customers'
            },
            'feature_focused': {
                'name': 'Feature-Focused Description',
                'category': 'Description',
                'prompt': 'Create a detailed product description for {product} highlighting key features: {features}. Include technical specs, benefits, and comparison with alternatives.',
                'variables': ['product', 'features'],
                'description': 'Highlight product specifications'
            }
        }
    }

def save_custom_template(category, template_name, template_data):
    """Save a custom template"""
    if 'custom_templates' not in st.session_state:
        st.session_state['custom_templates'] = {}
    
    if category not in st.session_state['custom_templates']:
        st.session_state['custom_templates'][category] = {}
    
    st.session_state['custom_templates'][category][template_name] = template_data
    return True

def get_all_templates():
    """Get both default and custom templates"""
    default_templates = get_default_templates()
    custom_templates = st.session_state.get('custom_templates', {})
    
    # Merge templates
    all_templates = default_templates.copy()
    
    for category, templates in custom_templates.items():
        if category not in all_templates:
            all_templates[category] = {}
        all_templates[category].update(templates)
    
    return all_templates

def apply_template_variables(prompt, variables_dict):
    """Apply variables to template prompt"""
    try:
        return prompt.format(**variables_dict)
    except KeyError as e:
        return f"Error: Missing variable {e}"

def get_template_categories():
    """Get all available template categories"""
    all_templates = get_all_templates()
    categories = set()
    
    for category_group in all_templates.values():
        for template_data in category_group.values():
            categories.add(template_data.get('category', 'Other'))
    
    return sorted(list(categories))

# History System
def get_history_by_type(content_type=None):
    """Get history filtered by content type"""
    all_content = st.session_state.get('generated_content', {})
    
    if content_type:
        return {k: v for k, v in all_content.items() if content_type.lower() in k.lower()}
    
    return all_content

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

# Batch Operations System
def batch_generate_content(prompts_list, content_type, max_tokens=800):
    """Generate multiple content pieces in batch"""
    results = []
    
    for i, prompt_data in enumerate(prompts_list):
        try:
            system_prompt = prompt_data.get('system_prompt', '')
            user_prompt = prompt_data.get('user_prompt', '')
            
            # Show progress
            progress_text = f"Generating {i+1}/{len(prompts_list)}: {content_type}"
            
            result = call_openai(system_prompt, user_prompt, max_tokens)
            
            results.append({
                'index': i,
                'prompt_data': prompt_data,
                'result': result,
                'success': True,
                'error': None
            })
            
        except Exception as e:
            results.append({
                'index': i,
                'prompt_data': prompt_data,
                'result': None,
                'success': False,
                'error': str(e)
            })
    
    return results

def create_batch_prompts(base_prompt, variations):
    """Create batch prompts from base prompt and variations"""
    prompts = []
    
    for variation in variations:
        # Replace variables in base prompt
        modified_prompt = base_prompt
        for key, value in variation.items():
            modified_prompt = modified_prompt.replace(f"{{{key}}}", value)
        
        prompts.append({
            'system_prompt': "Sen bir Etsy uzmanısın.",
            'user_prompt': modified_prompt,
            'variation': variation
        })
    
    return prompts

def batch_title_variations(product_desc, audiences, styles, count_per_combo=2):
    """Generate title variations for different audience/style combinations"""
    variations = []
    
    for audience in audiences:
        for style in styles:
            for i in range(count_per_combo):
                variations.append({
                    'product': product_desc,
                    'audience': audience,
                    'style': style,
                    'variation': f"v{i+1}"
                })
    
    base_prompt = """Create a high-converting Etsy title (130-140 chars) for {product} targeting {audience}. 
    Style: {style}. Include main keywords, occasion, and gift potential. Variation: {variation}."""
    
    return create_batch_prompts(base_prompt, variations)

def batch_tag_variations(product_desc, categories, count=3):
    """Generate multiple tag sets for the same product"""
    variations = []
    
    for category in categories:
        for i in range(count):
            variations.append({
                'product': product_desc,
                'category': category,
                'approach': f"approach_{i+1}"
            })
    
    base_prompt = """Create 13 Etsy tags (max 20 chars each) for {product} in {category} category. 
    Use approach {approach}: 1=high-volume keywords, 2=long-tail keywords, 3=seasonal keywords. 
    Format: tag1,tag2,tag3..."""
    
    return create_batch_prompts(base_prompt, variations)

def export_batch_results(results, filename_prefix):
    """Export batch results to different formats"""
    # Prepare data for export
    export_data = {
        'generated_at': time.time(),
        'total_results': len(results),
        'successful_results': len([r for r in results if r['success']]),
        'results': results
    }
    
    # JSON export
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # CSV-like text export
    csv_lines = ["Index,Success,Result,Error"]
    for result in results:
        csv_lines.append(f"{result['index']},{result['success']},\"{result.get('result', '')}\",\"{result.get('error', '')}\"")
    csv_data = "\n".join(csv_lines)
    
    return {
        'json': json_data,
        'csv': csv_data,
        'filename_base': f"{filename_prefix}_{int(time.time())}"
    }

# Rate Limiting System
class RateLimiter:
    def __init__(self, max_requests=60, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        if 'rate_limit_requests' not in st.session_state:
            st.session_state['rate_limit_requests'] = []
    
    def can_make_request(self):
        """Check if a request can be made within rate limits"""
        now = time.time()
        # Remove old requests outside the window
        st.session_state['rate_limit_requests'] = [
            req_time for req_time in st.session_state['rate_limit_requests'] 
            if now - req_time < self.window_seconds
        ]
        
        return len(st.session_state['rate_limit_requests']) < self.max_requests
    
    def record_request(self):
        """Record a new request"""
        st.session_state['rate_limit_requests'].append(time.time())
    
    def get_wait_time(self):
        """Get how long to wait before next request"""
        if self.can_make_request():
            return 0
        
        oldest_request = min(st.session_state['rate_limit_requests'])
        return self.window_seconds - (time.time() - oldest_request)
    
    def get_remaining_requests(self):
        """Get number of remaining requests in current window"""
        now = time.time()
        recent_requests = [
            req_time for req_time in st.session_state['rate_limit_requests'] 
            if now - req_time < self.window_seconds
        ]
        return max(0, self.max_requests - len(recent_requests))

# Initialize rate limiter
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute

def throttled_api_call(func, *args, **kwargs):
    """Make API call with rate limiting"""
    if not rate_limiter.can_make_request():
        wait_time = rate_limiter.get_wait_time()
        
        # Show rate limit warning
        st.warning(f"⏱️ Rate limit reached. Please wait {wait_time:.1f} seconds before next request.")
        
        # If wait time is reasonable, wait and proceed
        if wait_time <= 5:  # Only wait if less than 5 seconds
            time.sleep(wait_time)
        else:
            raise APIError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds.")
    
    # Record the request
    rate_limiter.record_request()
    
    # Make the actual API call
    return func(*args, **kwargs)

def get_rate_limit_status():
    """Get current rate limit status"""
    remaining = rate_limiter.get_remaining_requests()
    wait_time = rate_limiter.get_wait_time()
    
    return {
        'remaining_requests': remaining,
        'max_requests': rate_limiter.max_requests,
        'wait_time': wait_time,
        'percentage_used': ((rate_limiter.max_requests - remaining) / rate_limiter.max_requests) * 100
    }

# Analytics and Logging System
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

# Initialize analytics
init_analytics()

# Error Handling System
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

def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with retry logic"""
    max_retries = kwargs.pop('max_retries', 3)
    retry_delay = kwargs.pop('retry_delay', 1)
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        
        except Exception as e:
            log_error(e, {'function': func.__name__, 'attempt': attempt + 1})
            
            if attempt == max_retries - 1:  # Last attempt
                raise e
            
            # Check if it's a retryable error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['quota', 'billing', 'authentication']):
                # Don't retry quota/auth errors
                raise e
            
            # Wait before retry
            time.sleep(retry_delay * (attempt + 1))
    
    return None

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

# AI Generation Functions
def call_openai(system_prompt, user_prompt, max_tokens=800, use_cache=True):
    """Enhanced OpenAI API call with comprehensive error handling"""
    try:
        # Input validation
        validate_input(system_prompt, 'required', 'System prompt')
        validate_input(user_prompt, 'required', 'User prompt')
        validate_input(system_prompt, 'max_length', 'System prompt')
        validate_input(user_prompt, 'max_length', 'User prompt')
        
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

# Sidebar for product information
with st.sidebar:
    language = st.selectbox(
        t("language_selector"), 
        ["Türkçe", "English"], 
        index=0 if st.session_state['language'] == 'tr' else 1
    )
    st.session_state['language'] = 'tr' if language == "Türkçe" else 'en'
    
    st.markdown("---")
    st.header(t("product_info"))
    
    # Optimized form inputs with session state caching and validation
    st.markdown("### " + t("product_info"))
    
    # Product description with validation
    product_description = st.text_area(
        t("product_description"),
        value=get_form_data("product_description"),
        placeholder=t("product_desc_placeholder"),
        height=120,
        key="product_desc_input",
        on_change=lambda: set_form_data("product_description", st.session_state.product_desc_input),
        help="Minimum 10 characters, maximum 1000 characters"
    )
    
    # Real-time validation for product description
    if product_description:
        char_count = len(product_description)
        if char_count < 10:
            st.warning(f"⚠️ Too short: {char_count}/10 minimum characters")
        elif char_count > 1000:
            st.error(f"❌ Too long: {char_count}/1000 maximum characters")
        else:
            st.success(f"✅ Good length: {char_count}/1000 characters")
    
    # Product category with validation
    product_category = st.text_input(
        t("product_category"),
        value=get_form_data("product_category"),
        placeholder=t("product_cat_placeholder"),
        key="product_cat_input",
        on_change=lambda: set_form_data("product_category", st.session_state.product_cat_input),
        help="Required field - describe your product category"
    )
    
    # Validation for product category
    if product_category and len(product_category) < 3:
        st.warning("⚠️ Category should be at least 3 characters")
    
    # Target audience with validation
    target_audience = st.text_input(
        t("target_audience"),
        value=get_form_data("target_audience"),
        placeholder=t("target_audience_placeholder"),
        key="target_audience_input",
        on_change=lambda: set_form_data("target_audience", st.session_state.target_audience_input),
        help="Who is your target customer? (e.g., women 25-35, kids, professionals)"
    )
    
    # Validation for target audience
    if target_audience:
        if len(target_audience) < 5:
            st.warning("⚠️ Be more specific about your target audience")
        else:
            # Check for common audience keywords
            audience_keywords = ['women', 'men', 'kids', 'teens', 'adults', 'professionals', 'students', 'parents']
            if any(keyword in target_audience.lower() for keyword in audience_keywords):
                st.success("✅ Good audience definition")
            else:
                st.info("💡 Consider adding age group or demographic details")
    
    # Design theme with validation
    design_theme = st.text_input(
        t("design_theme"),
        value=get_form_data("design_theme"),
        placeholder=t("design_theme_placeholder"),
        key="design_theme_input",
        on_change=lambda: set_form_data("design_theme", st.session_state.design_theme_input),
        help="Design style or theme (e.g., vintage, modern, minimalist, cute, gothic)"
    )
    
    # Validation for design theme
    if design_theme:
        theme_keywords = ['vintage', 'modern', 'minimalist', 'cute', 'gothic', 'retro', 'elegant', 'bold', 'simple']
        if any(keyword in design_theme.lower() for keyword in theme_keywords):
            st.success("✅ Recognized design style")
        elif len(design_theme) < 3:
            st.warning("⚠️ Theme should be more descriptive")
    
    # Form completion indicator
    st.markdown("---")
    st.markdown("📊 **Form Completion**")
    
    required_fields = [
        ("Product Description", product_description, 10),
        ("Product Category", product_category, 3),
        ("Target Audience", target_audience, 5),
        ("Design Theme", design_theme, 3)
    ]
    
    completed_fields = 0
    for field_name, field_value, min_length in required_fields:
        if field_value and len(field_value.strip()) >= min_length:
            completed_fields += 1
            st.markdown(f"✅ {field_name}")
        else:
            st.markdown(f"❌ {field_name}")
    
    completion_percentage = (completed_fields / len(required_fields)) * 100
    st.progress(completion_percentage / 100)
    st.markdown(f"**{completion_percentage:.0f}% Complete** ({completed_fields}/{len(required_fields)} fields)")
    
    if completion_percentage == 100:
        st.success("🎉 All required fields completed!")
    elif completion_percentage >= 75:
        st.info("🔄 Almost there! Complete remaining fields for best results.")
    elif completion_percentage >= 50:
        st.warning("⚠️ Fill more fields for better AI results.")
    else:
        st.error("❌ Please complete the basic information first.")
    
    # Cache statistics
    st.markdown("---")
    st.markdown("📊 **Cache Stats**")
    cache_hits = st.session_state['cache_stats']['hits']
    cache_misses = st.session_state['cache_stats']['misses']
    total_calls = cache_hits + cache_misses
    
    if total_calls > 0:
        hit_rate = (cache_hits / total_calls) * 100
        st.metric("Cache Hit Rate", f"{hit_rate:.1f}%", f"{cache_hits}/{total_calls}")
        st.metric("Cache Size", len(st.session_state['api_cache']))
    else:
        st.info("No API calls yet")
    
    # Cache management
    if st.button("🗑️ Clear Cache"):
        st.session_state['api_cache'] = {}
        st.session_state['cache_stats'] = {'hits': 0, 'misses': 0}
        st.success("Cache cleared!")
        st.rerun()
    
    # Rate Limit Status
    st.markdown("---")
    st.markdown("⏱️ **Rate Limits**")
    
    rate_status = get_rate_limit_status()
    
    # Progress bar for rate limit usage
    st.progress(rate_status['percentage_used'] / 100)
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Remaining", f"{rate_status['remaining_requests']}/{rate_status['max_requests']}")
    
    with col2:
        if rate_status['wait_time'] > 0:
            st.metric("Wait Time", f"{rate_status['wait_time']:.1f}s")
        else:
            st.metric("Status", "✅ Ready")
    
    # Color-coded warnings
    if rate_status['remaining_requests'] == 0:
        st.error("🚫 Rate limit reached!")
    elif rate_status['remaining_requests'] <= 5:
        st.warning(f"⚠️ Only {rate_status['remaining_requests']} requests left")
    elif rate_status['remaining_requests'] <= 10:
        st.info(f"ℹ️ {rate_status['remaining_requests']} requests remaining")
    
    # Rate limit tips
    if rate_status['percentage_used'] > 75:
        st.markdown("""
        💡 **Rate Limit Tips:**
        - Use cache to avoid repeat calls
        - Wait between batch operations
                 - Consider spreading work over time
         """)
    
    # Analytics Dashboard
    st.markdown("---")
    st.markdown("📊 **Analytics Dashboard**")
    
    analytics_summary = get_analytics_summary()
    
    if analytics_summary:
        # Session metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Session Time", f"{analytics_summary['session_duration']:.1f} min")
        with col2:
            st.metric("API Calls", analytics_summary['total_api_calls'])
        
        # Performance metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Response", f"{analytics_summary['avg_response_time']:.2f}s")
        with col2:
            st.metric("Success Rate", f"{analytics_summary['success_rate']:.1f}%")
        
        # Most used feature
        if analytics_summary['most_used_feature'] != 'None':
            st.markdown(f"🏆 **Most Used:** {analytics_summary['most_used_feature']}")
        
        # Feature usage breakdown
        if 'analytics' in st.session_state and st.session_state['analytics']['feature_usage']:
            with st.expander("📈 Feature Usage", expanded=False):
                feature_usage = st.session_state['analytics']['feature_usage']
                for feature, count in sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.markdown(f"- {feature}: {count} uses")
        
        # Performance trend (last 10 API calls)
        if st.session_state['analytics']['api_calls']:
            with st.expander("⚡ Performance Trend", expanded=False):
                recent_calls = st.session_state['analytics']['api_calls'][-10:]
                durations = [call['duration'] for call in recent_calls if call['success']]
                
                if durations:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.plot(range(len(durations)), durations, marker='o')
                    ax.set_title('Response Time Trend (Last 10 calls)')
                    ax.set_xlabel('Call Index')
                    ax.set_ylabel('Duration (s)')
                    st.pyplot(fig)
                    plt.close()
        
        # Export analytics
        with st.expander("📤 Export Analytics", expanded=False):
            if st.button("📊 Generate Report", key="generate_analytics_report"):
                analytics_data = st.session_state['analytics'].copy()
                analytics_data['exported_at'] = time.time()
                analytics_data['session_duration_minutes'] = analytics_summary['session_duration']
                
                report_json = json.dumps(analytics_data, indent=2, ensure_ascii=False)
                st.session_state['analytics_report'] = report_json
                st.success("Analytics report generated!")
            
            if 'analytics_report' in st.session_state:
                st.download_button(
                    label="📥 Download Analytics",
                    data=st.session_state['analytics_report'],
                    file_name=f"analytics_report_{int(time.time())}.json",
                    mime="application/json",
                    key="download_analytics"
                )
    else:
        st.info("📊 Analytics will appear as you use the app")
     
     # Project Management Section
    st.markdown("---")
    st.markdown("💾 **Project Management**")
    
    # Initialize saved projects
    if 'saved_projects' not in st.session_state:
        st.session_state['saved_projects'] = {}
    
    # Save current project
    with st.expander("📁 Save Project", expanded=False):
        project_name = st.text_input("Project Name:", 
                                   value=f"Project_{int(time.time())}", 
                                   key="save_project_name")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", key="save_project_btn"):
                if project_name.strip():
                    success = save_project(project_name.strip())
                    if success:
                        st.success(f"✅ Project '{project_name}' saved!")
                        st.rerun()
                else:
                    st.warning("Please enter a project name")
        
        with col2:
            if st.button("📋 Save As Copy", key="save_copy_btn"):
                if project_name.strip():
                    copy_name = f"{project_name}_copy_{int(time.time())}"
                    success = save_project(copy_name)
                    if success:
                        st.success(f"✅ Copy saved as '{copy_name}'!")
                        st.rerun()
    
    # Load existing projects
    if st.session_state['saved_projects']:
        with st.expander("📂 Load Project", expanded=False):
            project_names = list(st.session_state['saved_projects'].keys())
            selected_project = st.selectbox("Select Project:", 
                                          options=project_names,
                                          key="load_project_select")
            
            if selected_project:
                # Show project summary
                project_data = st.session_state['saved_projects'][selected_project]
                summary = get_project_summary(project_data)
                
                st.markdown(f"""
                **📄 Project Info:**
                - Product: {summary['product']}
                - Category: {summary['category']}
                - Generated Items: {summary['generated_items']}
                - Last Modified: {summary['last_modified']}
                """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📂 Load", key="load_project_btn"):
                        success = load_project(selected_project)
                        if success:
                            st.success(f"✅ Project '{selected_project}' loaded!")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key="delete_project_btn"):
                        del st.session_state['saved_projects'][selected_project]
                        st.success(f"🗑️ Project '{selected_project}' deleted!")
                        st.rerun()
                
                with col3:
                    # Export project
                    project_json = export_project(project_data)
                    st.download_button(
                        label="📤 Export",
                        data=project_json,
                        file_name=f"{selected_project}.json",
                        mime="application/json",
                        key="export_project_btn"
                    )
    
    # Import project
    with st.expander("📥 Import Project", expanded=False):
        uploaded_file = st.file_uploader("Upload JSON file:", 
                                       type=['json'],
                                       key="import_project_file")
        
        if uploaded_file is not None:
            try:
                json_data = uploaded_file.read().decode('utf-8')
                success, message = import_project(json_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Alternative: Paste JSON
        st.markdown("**Or paste JSON data:**")
        json_input = st.text_area("Paste JSON:", 
                                height=100,
                                key="import_json_text")
        
        if st.button("📥 Import from Text", key="import_text_btn"):
            if json_input.strip():
                success, message = import_project(json_input.strip())
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Quick stats
    if st.session_state['saved_projects']:
        st.markdown(f"📊 **{len(st.session_state['saved_projects'])} saved projects**")
    
    # Template Library Section
    st.markdown("---")
    st.markdown("📝 **Template Library**")
    
    # Initialize custom templates
    if 'custom_templates' not in st.session_state:
        st.session_state['custom_templates'] = {}
    
    # Template browser
    with st.expander("📚 Browse Templates", expanded=False):
        # Category filter
        categories = get_template_categories()
        selected_category = st.selectbox("Filter by category:", 
                                       options=['All'] + categories,
                                       key="template_category_filter")
        
        all_templates = get_all_templates()
        
        # Display templates
        for group_name, templates in all_templates.items():
            for template_id, template_data in templates.items():
                template_category = template_data.get('category', 'Other')
                
                # Apply category filter
                if selected_category != 'All' and template_category != selected_category:
                    continue
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{template_data['name']}** _{template_category}_")
                        st.markdown(f"📄 {template_data['description']}")
                        
                        # Show variables
                        if template_data.get('variables'):
                            variables_str = ', '.join([f"{{{var}}}" for var in template_data['variables']])
                            st.markdown(f"🔧 Variables: `{variables_str}`")
                    
                    with col2:
                        if st.button("📋 Use", key=f"use_template_{group_name}_{template_id}"):
                            # Store selected template for use
                            st.session_state['selected_template'] = {
                                'group': group_name,
                                'id': template_id,
                                'data': template_data
                            }
                            st.success(f"Template '{template_data['name']}' selected!")
                    
                    st.markdown("---")
    
    # Create custom template
    with st.expander("➕ Create Custom Template", expanded=False):
        template_name = st.text_input("Template Name:", key="new_template_name")
        template_category = st.selectbox("Category:", 
                                       options=categories + ['Custom'],
                                       key="new_template_category")
        template_description = st.text_input("Description:", key="new_template_desc")
        template_prompt = st.text_area("Prompt Template:", 
                                     placeholder="Use {variable_name} for variables",
                                     height=100,
                                     key="new_template_prompt")
        
        # Extract variables from prompt
        import re
        if template_prompt:
            variables = re.findall(r'\{(\w+)\}', template_prompt)
            if variables:
                st.markdown(f"**Variables found:** {', '.join(variables)}")
        
        if st.button("💾 Save Template", key="save_custom_template"):
            if template_name and template_prompt:
                template_data = {
                    'name': template_name,
                    'category': template_category,
                    'prompt': template_prompt,
                    'description': template_description,
                    'variables': variables if template_prompt else [],
                    'custom': True
                }
                
                success = save_custom_template('custom_prompts', template_name.lower().replace(' ', '_'), template_data)
                if success:
                    st.success(f"✅ Template '{template_name}' saved!")
                    st.rerun()
            else:
                st.warning("Please fill in template name and prompt")
    
    # Template usage helper
    if 'selected_template' in st.session_state:
        st.markdown("---")
        st.markdown("🎯 **Selected Template**")
        template_data = st.session_state['selected_template']['data']
        st.markdown(f"**{template_data['name']}**")
        
        # Variable inputs
        if template_data.get('variables'):
            st.markdown("**Fill in variables:**")
            template_vars = {}
            
            for var in template_data['variables']:
                # Try to auto-fill from form data
                default_value = ""
                if var in ['product', 'business_type']:
                    default_value = get_form_data('product_description', '')
                elif var in ['audience', 'target']:
                    default_value = get_form_data('target_audience', '')
                elif var == 'style':
                    default_value = get_form_data('design_theme', '')
                
                template_vars[var] = st.text_input(f"{var.replace('_', ' ').title()}:", 
                                                 value=default_value,
                                                 key=f"template_var_{var}")
            
            # Preview
            if all(template_vars.values()):
                final_prompt = apply_template_variables(template_data['prompt'], template_vars)
                st.markdown("**Preview:**")
                st.text_area("Generated Prompt:", value=final_prompt, height=100, key="template_preview")
                
                if st.button("🚀 Use This Prompt", key="use_generated_prompt"):
                    # Store the final prompt for use in main content
                    st.session_state['ready_prompt'] = final_prompt
                    st.success("✅ Prompt ready to use in main content!")
    
    # Template stats
    total_templates = sum(len(templates) for templates in all_templates.values())
    custom_count = len(st.session_state.get('custom_templates', {}).get('custom_prompts', {}))
    st.markdown(f"📊 **{total_templates} templates** ({custom_count} custom)")
    
    # History Panel Section
    st.markdown("---")
    st.markdown("📜 **History Panel**")
    
    # Initialize history
    if 'content_history' not in st.session_state:
        st.session_state['content_history'] = []
    
    # History browser
    with st.expander("🔍 Browse History", expanded=False):
        if not st.session_state['content_history']:
            st.info("No history yet. Generate some content to see it here!")
        else:
            # Search and filter controls
            col1, col2 = st.columns(2)
            
            with col1:
                search_query = st.text_input("🔍 Search:", key="history_search")
                
            with col2:
                content_types = get_content_types_from_history()
                filter_type = st.selectbox("Filter by type:", 
                                         options=['All'] + content_types,
                                         key="history_filter_type")
            
            # Show favorites toggle
            show_favorites_only = st.checkbox("⭐ Show favorites only", key="show_favorites")
            
            # Get filtered history
            if search_query:
                history_entries = search_history(search_query)
            else:
                history_entries = st.session_state['content_history']
            
            # Apply type filter
            if filter_type != 'All':
                history_entries = [e for e in history_entries if e.get('content_type') == filter_type]
            
            # Apply favorites filter
            if show_favorites_only:
                history_entries = [e for e in history_entries if e.get('favorited', False)]
            
            # Display history entries
            for idx, entry in enumerate(history_entries[:20]):  # Show max 20 entries
                with st.container():
                    # Header row
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        timestamp_str = format_timestamp(entry.get('timestamp', 0))
                        st.markdown(f"**{entry.get('content_type', 'Unknown')}** - {timestamp_str}")
                    
                    with col2:
                        # Favorite button
                        fav_icon = "⭐" if entry.get('favorited', False) else "☆"
                        if st.button(fav_icon, key=f"fav_{entry['id']}"):
                            toggle_favorite(entry['id'])
                            st.rerun()
                    
                    with col3:
                        # Reuse button
                        if st.button("🔄 Reuse", key=f"reuse_{entry['id']}"):
                            # Copy content to clipboard equivalent
                            st.session_state['reused_content'] = entry.get('content', '')
                            st.success("Content ready to reuse!")
                    
                    with col4:
                        # Tags button
                        tags = entry.get('tags', [])
                        tag_display = f"🏷️ {len(tags)}" if tags else "🏷️"
                        if st.button(tag_display, key=f"tags_{entry['id']}"):
                            st.session_state[f'show_tags_{entry["id"]}'] = not st.session_state.get(f'show_tags_{entry["id"]}', False)
                    
                    # Content preview
                    content = entry.get('content', '')
                    if len(content) > 200:
                        preview = content[:200] + "..."
                        with st.expander(f"Preview: {preview}", expanded=False):
                            st.text_area("Full content:", value=content, height=150, key=f"content_{entry['id']}")
                    else:
                        st.text_area("Content:", value=content, height=100, key=f"content_short_{entry['id']}")
                    
                    # Tags section (if expanded)
                    if st.session_state.get(f'show_tags_{entry["id"]}', False):
                        st.markdown("**Tags:**")
                        if tags:
                            for tag in tags:
                                st.markdown(f"- {tag}")
                        
                        # Add new tag
                        new_tag = st.text_input("Add tag:", key=f"new_tag_{entry['id']}")
                        if st.button("➕ Add Tag", key=f"add_tag_{entry['id']}"):
                            if new_tag.strip():
                                add_tag_to_entry(entry['id'], new_tag.strip())
                                st.rerun()
                    
                    # Show prompt used (if available)
                    if entry.get('prompt_used'):
                        with st.expander("🎯 Prompt used", expanded=False):
                            st.text_area("Original prompt:", 
                                       value=entry['prompt_used'], 
                                       height=80, 
                                       key=f"prompt_{entry['id']}")
                    
                    st.markdown("---")
            
            # Show more button if there are more entries
            if len(history_entries) > 20:
                st.markdown(f"**Showing 20 of {len(history_entries)} entries**")
    
    # History management
    with st.expander("🗑️ History Management", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All History", key="clear_history"):
                st.session_state['content_history'] = []
                st.success("History cleared!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Non-Favorites", key="clear_non_favorites"):
                st.session_state['content_history'] = [
                    e for e in st.session_state['content_history'] 
                    if e.get('favorited', False)
                ]
                st.success("Non-favorite entries cleared!")
                st.rerun()
        
        # Export history
        if st.session_state['content_history']:
            history_json = json.dumps(st.session_state['content_history'], indent=2, ensure_ascii=False)
            st.download_button(
                label="📤 Export History",
                data=history_json,
                file_name=f"etsy_ai_history_{int(time.time())}.json",
                mime="application/json",
                key="export_history"
            )
    
    # History stats
    total_entries = len(st.session_state['content_history'])
    favorite_count = sum(1 for e in st.session_state['content_history'] if e.get('favorited', False))
    st.markdown(f"📊 **{total_entries} entries** ({favorite_count} favorites)")
    
    # Reused content display
    if 'reused_content' in st.session_state:
        st.markdown("---")
        st.markdown("🔄 **Ready to Reuse**")
        st.text_area("Content ready for reuse:", 
                   value=st.session_state['reused_content'], 
                   height=100, 
                   key="reused_content_display")
        if st.button("✅ Clear", key="clear_reused"):
            del st.session_state['reused_content']
            st.rerun()
    
    # Batch Operations Section
    st.markdown("---")
    st.markdown("⚡ **Batch Operations**")
    
    with st.expander("🚀 Bulk Content Generation", expanded=False):
        batch_type = st.selectbox("Select batch type:", [
            "Title Variations",
            "Tag Variations", 
            "Description Variations",
            "Custom Batch"
        ], key="batch_type_select")
        
        if batch_type == "Title Variations":
            st.markdown("**Generate multiple title variations**")
            
            # Get product info from form
            product_info = get_form_data('product_description', '')
            
            if not product_info:
                st.warning("Please fill in product description first")
            else:
                # Audience variations
                audiences_input = st.text_input("Target audiences (comma-separated):", 
                                              value="women,men,teens,kids", 
                                              key="batch_audiences")
                
                # Style variations  
                styles_input = st.text_input("Design styles (comma-separated):", 
                                           value="vintage,modern,minimalist,cute", 
                                           key="batch_styles")
                
                count_per_combo = st.slider("Variations per combination:", 1, 5, 2, key="batch_count")
                
                if st.button("🚀 Generate Title Batch", key="generate_title_batch"):
                    if audiences_input and styles_input:
                        audiences = [a.strip() for a in audiences_input.split(',')]
                        styles = [s.strip() for s in styles_input.split(',')]
                        
                        total_count = len(audiences) * len(styles) * count_per_combo
                        st.info(f"Will generate {total_count} titles...")
                        
                        # Create progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        with st.spinner("Generating batch titles..."):
                            prompts = batch_title_variations(product_info, audiences, styles, count_per_combo)
                            
                            # Generate with progress tracking
                            results = []
                            for i, prompt_data in enumerate(prompts):
                                progress = (i + 1) / len(prompts)
                                progress_bar.progress(progress)
                                status_text.text(f"Generating {i+1}/{len(prompts)}")
                                
                                try:
                                    result = call_openai(prompt_data['system_prompt'], prompt_data['user_prompt'])
                                    results.append({
                                        'index': i,
                                        'result': result,
                                        'variation': prompt_data['variation'],
                                        'success': True
                                    })
                                except Exception as e:
                                    results.append({
                                        'index': i,
                                        'result': str(e),
                                        'variation': prompt_data['variation'],
                                        'success': False
                                    })
                            
                            # Store results
                            st.session_state['batch_results'] = results
                            
                            progress_bar.progress(1.0)
                            status_text.text("Complete!")
                            st.success(f"✅ Generated {len(results)} title variations!")
        
        elif batch_type == "Tag Variations":
            st.markdown("**Generate multiple tag sets**")
            
            product_info = get_form_data('product_description', '')
            if not product_info:
                st.warning("Please fill in product description first")
            else:
                categories_input = st.text_input("Categories (comma-separated):", 
                                                value="clothing,gifts,handmade", 
                                                key="batch_categories")
                
                tag_count = st.slider("Tag sets per category:", 1, 5, 3, key="tag_set_count")
                
                if st.button("🏷️ Generate Tag Batch", key="generate_tag_batch"):
                    if categories_input:
                        categories = [c.strip() for c in categories_input.split(',')]
                        
                        with st.spinner("Generating batch tags..."):
                            prompts = batch_tag_variations(product_info, categories, tag_count)
                            results = batch_generate_content(prompts, "tags")
                            
                            st.session_state['batch_results'] = results
                            st.success(f"✅ Generated {len(results)} tag sets!")
        
        elif batch_type == "Custom Batch":
            st.markdown("**Custom batch generation**")
            
            base_prompt = st.text_area("Base prompt template (use {variable} for variables):", 
                                     height=100, 
                                     key="custom_batch_prompt")
            
            variations_text = st.text_area("Variations (JSON format):", 
                                         placeholder='[{"variable": "value1"}, {"variable": "value2"}]',
                                         height=100,
                                         key="custom_batch_variations")
            
            if st.button("🔧 Generate Custom Batch", key="generate_custom_batch"):
                if base_prompt and variations_text:
                    try:
                        variations = json.loads(variations_text)
                        prompts = create_batch_prompts(base_prompt, variations)
                        
                        with st.spinner("Generating custom batch..."):
                            results = batch_generate_content(prompts, "custom")
                            st.session_state['batch_results'] = results
                            st.success(f"✅ Generated {len(results)} custom results!")
                    
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in variations")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Batch Results Display
    if 'batch_results' in st.session_state and st.session_state['batch_results']:
        with st.expander("📊 Batch Results", expanded=True):
            results = st.session_state['batch_results']
            successful = [r for r in results if r.get('success', False)]
            failed = [r for r in results if not r.get('success', False)]
            
            st.markdown(f"**Results: {len(successful)} successful, {len(failed)} failed**")
            
            # Show successful results
            if successful:
                st.markdown("**✅ Successful Results:**")
                for i, result in enumerate(successful[:10]):  # Show max 10
                    st.text_area(f"Result {result['index']+1}:", 
                               value=result['result'], 
                               height=60, 
                               key=f"batch_result_{i}")
                
                if len(successful) > 10:
                    st.info(f"Showing 10 of {len(successful)} results")
            
            # Show failed results
            if failed:
                with st.expander("❌ Failed Results", expanded=False):
                    for result in failed:
                        st.error(f"Result {result['index']+1}: {result['result']}")
            
            # Export options
            st.markdown("**📤 Export Results:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export Text", key="export_batch_text"):
                    text_content = "\n\n".join([f"Result {r['index']+1}:\n{r['result']}" 
                                               for r in successful])
                    st.session_state['batch_export_text'] = text_content
            
            with col2:
                export_data = export_batch_results(results, "batch_results")
                st.download_button(
                    label="📊 Export JSON",
                    data=export_data['json'],
                    file_name=f"{export_data['filename_base']}.json",
                    mime="application/json",
                    key="export_batch_json"
                )
            
            with col3:
                st.download_button(
                    label="📋 Export CSV", 
                    data=export_data['csv'],
                    file_name=f"{export_data['filename_base']}.csv",
                    mime="text/csv",
                    key="export_batch_csv"
                )
            
            # Clear results
            if st.button("🗑️ Clear Batch Results", key="clear_batch_results"):
                del st.session_state['batch_results']
                st.rerun()
    
    # Export text display
    if 'batch_export_text' in st.session_state:
        st.markdown("---")
        st.markdown("📄 **Exported Text**")
        st.text_area("Batch results:", 
                   value=st.session_state['batch_export_text'], 
                   height=200, 
                   key="batch_export_display")
        if st.button("✅ Clear Export", key="clear_batch_export"):
            del st.session_state['batch_export_text']
            st.rerun()
    
    # Error Monitoring Section
    st.markdown("---")
    st.markdown("🚨 **Error Monitoring**")
    
    # Initialize error log
    if 'error_log' not in st.session_state:
        st.session_state['error_log'] = []
    
    error_count = len(st.session_state['error_log'])
    
    if error_count > 0:
        # Recent errors summary
        recent_errors = st.session_state['error_log'][:5]
        error_types = {}
        
        for error in recent_errors:
            error_type = error.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        st.markdown(f"**📊 {error_count} total errors**")
        
        # Error type breakdown
        for error_type, count in error_types.items():
            st.markdown(f"- {error_type}: {count}")
        
        # Error log viewer
        with st.expander("🔍 Error Log", expanded=False):
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                show_count = st.selectbox("Show errors:", [5, 10, 20, "All"], key="error_show_count")
            
            with col2:
                if st.button("🗑️ Clear Log", key="clear_error_log"):
                    st.session_state['error_log'] = []
                    st.success("Error log cleared!")
                    st.rerun()
            
            # Display errors
            display_errors = st.session_state['error_log']
            if show_count != "All":
                display_errors = display_errors[:show_count]
            
            for i, error in enumerate(display_errors):
                timestamp = time.strftime('%H:%M:%S', time.localtime(error['timestamp']))
                
                with st.container():
                    # Error header
                    error_emoji = "🚫" if "quota" in error['message'].lower() else "❌"
                    st.markdown(f"{error_emoji} **{error['error_type']}** - {timestamp}")
                    
                    # Error message
                    st.markdown(f"💬 {error['message'][:100]}{'...' if len(error['message']) > 100 else ''}")
                    
                    # Context (if available)
                    if error.get('context'):
                        with st.expander(f"Context {i+1}", expanded=False):
                            st.json(error['context'])
                    
                    st.markdown("---")
        
        # Error report export
        with st.expander("📤 Export Error Report", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Generate Report", key="generate_error_report"):
                    report = create_error_report()
                    st.session_state['error_report'] = report
                    st.success("Error report generated!")
            
            with col2:
                if 'error_report' in st.session_state:
                    st.download_button(
                        label="📥 Download Report",
                        data=st.session_state['error_report'],
                        file_name=f"error_report_{int(time.time())}.md",
                        mime="text/markdown",
                        key="download_error_report"
                    )
        
        # Error statistics
        st.markdown("**📈 Error Statistics:**")
        
        # Calculate error rates
        if error_count >= 10:
            recent_hour_errors = [e for e in st.session_state['error_log'] 
                                if time.time() - e['timestamp'] < 3600]
            st.metric("Errors (last hour)", len(recent_hour_errors))
        
        # Most common error type
        all_error_types = [e.get('error_type', 'Unknown') for e in st.session_state['error_log']]
        if all_error_types:
            most_common = max(set(all_error_types), key=all_error_types.count)
            st.metric("Most common error", most_common)
    
    else:
        st.success("✅ No errors recorded")
        st.info("Errors will appear here when they occur")
    
    # Error prevention tips
    with st.expander("💡 Error Prevention Tips", expanded=False):
        st.markdown("""
        **🔧 Common Issues & Solutions:**
        
        1. **API Quota Errors**
           - Check your OpenAI billing settings
           - Upgrade your plan if needed
           - Monitor your usage
        
        2. **Connection Errors**
           - Check your internet connection
           - Try again in a few moments
           - Contact support if persistent
        
        3. **Input Validation Errors**
           - Ensure all required fields are filled
           - Check character limits
           - Use appropriate formats
        
        4. **Cache Errors**
           - Clear cache if issues persist
           - Restart the application
           - Check available memory
        """)

# Main header
st.markdown(f"""
<div style="text-align: center; padding: 20px;">
    <h1>{t('app_title')}</h1>
    <p style='font-size: 1.2em; color: #666;'>{t('app_subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# Step definitions
steps_tr = [
    {
        "title": "1. Tasarım Seçimi / Üretimi",
        "description": "T-shirt üzerine basılacak tasarımı ya hazır alır ya da AI ile özel üretirsiniz.",
        "ai_function": "design_creation"
    },
    {
        "title": "2. Tasarımı Baskıya Uygun Hale Getirme",
        "description": "Tasarımın baskı kalitesi ve hizalaması DTG baskıya uygun olmalıdır.",
        "ai_function": "design_optimization"
    },
    {
        "title": "3. Mockup Oluşturma",
        "description": "Tasarım t-shirt üzerinde nasıl görünüyor? Bunu göstermek için mockup hazırlanır.",
        "ai_function": "mockup_creation"
    },
    {
        "title": "4. Ürün Görsellerinin Hazırlanması",
        "description": "Tüm görseller Etsy'nin önerdiği ölçü ve kaliteye uygun olmalı.",
        "ai_function": "image_preparation"
    },
    {
        "title": "5. Ürün Başlığı Yazma",
        "description": "Başlık maksimum aranabilirlik için optimize edilmelidir.",
        "ai_function": "title_creation"
    },
    {
        "title": "6. Etiket (Tag) Ekleme",
        "description": "13 etiket girilebilir, her biri en fazla 20 karakter.",
        "ai_function": "tag_creation"
    },
    {
        "title": "7. Ürün Açıklaması Yazma",
        "description": "İlk satırda başlık yer alır, ardından sabit açıklama yazılır.",
        "ai_function": "description_creation"
    },
    {
        "title": "8. Varyasyonları Ayarlama (Renk & Beden)",
        "description": "Renk ve beden seçenekleri müşteri deneyimi için net olmalı.",
        "ai_function": "variations_setup"
    },
    {
        "title": "9. Fiyatlandırma ve Stratejik İndirim",
        "description": "Satış psikolojisiyle çalışır: indirimli gösterimle gerçek fiyat algısı yaratılır.",
        "ai_function": "pricing_strategy"
    },
    {
        "title": "10. Ürünü Etsy'de Listeleme",
        "description": "Tüm bilgiler hazırsa ürün mağazada aktif edilir.",
        "ai_function": "listing_checklist"
    },
    {
        "title": "11. SEO ve Tanıtım Desteği",
        "description": "İlk günlerde trafik sağlamak için SEO ve tanıtım desteği gerekir.",
        "ai_function": "seo_promotion"
    },
    {
        "title": "12. Analiz, Güncelleme ve Optimize Etme",
        "description": "Zaman içinde performans analiz edip gerekli güncellemeler yapılır.",
        "ai_function": "analytics_optimization"
    },
    {
        "title": "13. Sipariş Akışı & Baskı Yönetimi",
        "description": "Printify gibi üretim partneri kullanıyorsan sipariş otomasyonu ayarlanmalı.",
        "ai_function": "order_management"
    }
]

steps_en = [
    {
        "title": "1. Design Selection / Creation",
        "description": "Choose or create designs for your t-shirt using ready-made designs or AI generation.",
        "ai_function": "design_creation"
    },
    {
        "title": "2. Prepare Design for Printing",
        "description": "Ensure your design is optimized for DTG (Direct-to-Garment) printing.",
        "ai_function": "design_optimization"
    },
    {
        "title": "3. Create Mockups",
        "description": "Show how your design looks on the actual product.",
        "ai_function": "mockup_creation"
    },
    {
        "title": "4. Prepare Product Images",
        "description": "All images should meet Etsy's recommended size and quality standards.",
        "ai_function": "image_preparation"
    },
    {
        "title": "5. Write Product Title",
        "description": "Optimize your title for maximum searchability.",
        "ai_function": "title_creation"
    },
    {
        "title": "6. Add Tags",
        "description": "Use all 13 available tags, each max 20 characters.",
        "ai_function": "tag_creation"
    },
    {
        "title": "7. Write Product Description",
        "description": "Start with title in first line, followed by standard description.",
        "ai_function": "description_creation"
    },
    {
        "title": "8. Set Variations (Color & Size)",
        "description": "Set clear color and size options for better customer experience.",
        "ai_function": "variations_setup"
    },
    {
        "title": "9. Pricing & Strategic Discounts",
        "description": "Use sales psychology: show discounted price to create value perception.",
        "ai_function": "pricing_strategy"
    },
    {
        "title": "10. List Product on Etsy",
        "description": "Once all information is ready, activate the product in your store.",
        "ai_function": "listing_checklist"
    },
    {
        "title": "11. SEO & Promotion Support",
        "description": "Drive initial traffic through SEO and promotional efforts.",
        "ai_function": "seo_promotion"
    },
    {
        "title": "12. Analyze, Update & Optimize",
        "description": "Track performance over time and make necessary updates.",
        "ai_function": "analytics_optimization"
    },
    {
        "title": "13. Order Flow & Print Management",
        "description": "Set up automation if using print-on-demand services like Printify.",
        "ai_function": "order_management"
    }
]

current_steps = steps_tr if st.session_state['language'] == 'tr' else steps_en

# Create tabs for each step
tab_labels = [f"{t('step')} {i+1}" for i in range(13)]
tabs = st.tabs(tab_labels)

# Step 1: Design Creation
with tabs[0]:
    st.markdown('<div class="step-header">🎨 Adım 1: Tasarım Seçimi / Üretimi</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🎨 Step 1: Design Selection / Creation</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        st.markdown("""
        <div class="tip-box">
        💡 <strong>İpucu:</strong> Etsy'den "Digital Download + Commercial Use" filtrelerini kullanarak tasarım alabilir 
        veya AI ile özgün tasarımlar oluşturabilirsiniz.
        </div>
        """, unsafe_allow_html=True)
        
        design_type = st.selectbox("Tasarım türü seçin:", [
            "T-shirt grafik tasarımı",
            "Minimalist logo",
            "Vintage poster",
            "Modern tipografi",
            "İllüstrasyon",
            "Desen/pattern"
        ])
        
        if st.button("AI Tasarım Prompt'ı Oluştur", key="design_prompt_tr"):
            if product_description and design_theme:
                with st.spinner("Tasarım prompt'ı oluşturuluyor..."):
                    try:
                        system_prompt = "Sen profesyonel bir tasarımcısın. Etsy satışı için AI araçlarında (Midjourney, DALLE) kullanılacak detaylı tasarım prompt'ları oluşturuyorsun."
                        user_prompt = f"""
                        Ürün: {product_description}
                        Kategori: {product_category}
                        Hedef Kitle: {target_audience}
                        Tasarım Stili: {design_theme}
                        Tasarım Türü: {design_type}
                        
                        Bu bilgilere göre Midjourney/DALLE için detaylı, profesyonel bir tasarım prompt'ı oluştur. 
                        Prompt İngilizce olmalı ve şu format kullan:
                        
                        1. Ana Prompt (Midjourney/DALLE için)
                        2. Stil Parametreleri
                        3. Kalite Ayarları
                        4. Alternatif Prompt Önerileri (3 adet)
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Lütfen ürün açıklaması ve tasarım teması girin.")
        
        # AI Image Generation Section for Turkish
        st.markdown("---")
        st.markdown('<div class="section-header">🖼️ AI Tasarım Oluştur</div>', unsafe_allow_html=True)
        
        design_prompt_input_tr = st.text_area(
            "Tasarım prompt'ı:",
            placeholder="komik gözlüklü kedi t-shirt tasarımı, minimalist stil",
            height=100,
            key="design_prompt_input_tr"
        )
        
        image_size_tr = st.selectbox(
            "Görsel boyutu:",
            ["1024x1024", "1792x1024", "1024x1792"],
            key="image_size_tr"
        )
        
        if st.button("🎨 Tasarım Oluştur", key="generate_design_step1_tr"):
            if design_prompt_input_tr.strip():
                with st.spinner("Tasarım oluşturuluyor..."):
                    try:
                        response = client.images.generate(
                            model="dall-e-2",
                            prompt=design_prompt_input_tr,
                            size=image_size_tr,
                            n=1,
                        )
                        
                        image_url = response.data[0].url
                        st.image(image_url, caption="Oluşturulan Tasarım")
                        
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ Tasarım başarıyla oluşturuldu!
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download link
                        st.markdown(f"**İndir:** [Tasarımı İndir]({image_url})")
                        
                    except Exception as e:
                        if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                            st.error("🚫 OpenAI API kotanız dolmuş. Lütfen planınızı kontrol edin.")
                        else:
                            st.error(f"Hata: {str(e)}")
            else:
                st.warning("Lütfen bir tasarım prompt'ı girin.")
                
        if st.button("Alternatif Tasarım Prompt'ı Oluştur", key="design_prompt_alt"):
            if product_description and design_theme:
                with st.spinner("Tasarım prompt'ı oluşturuluyor..."):
                    try:
                        system_prompt = "Sen profesyonel bir tasarımcısın. Etsy satışı için AI araçlarında (Midjourney, DALLE) kullanılacak detaylı tasarım prompt'ları oluşturuyorsun."
                        user_prompt = f"""
                        Ürün: {product_description}
                        Kategori: {product_category}
                        Hedef Kitle: {target_audience}
                        Tasarım Stili: {design_theme}
                        Tasarım Türü: {design_type}
                        
                        Bu bilgilere göre Midjourney/DALLE için detaylı, profesyonel bir tasarım prompt'ı oluştur. 
                        Prompt İngilizce olmalı ve şu format kullan:
                        
                        1. Ana Prompt (Midjourney/DALLE için)
                        2. Stil Parametreleri
                        3. Kalite Ayarları
                        4. Alternatif Prompt Önerileri (3 adet)
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Lütfen ürün açıklaması ve tasarım teması girin.")
    
    else:
        st.markdown("""
        <div class="tip-box">
        💡 <strong>Tip:</strong> You can get designs from Etsy using "Digital Download + Commercial Use" filters 
        or create original designs with AI tools like Midjourney, DALLE, or Leonardo.
        </div>
        """, unsafe_allow_html=True)
        
        design_type = st.selectbox("Select design type:", [
            "T-shirt graphic design",
            "Minimalist logo",
            "Vintage poster",
            "Modern typography",
            "Illustration",
            "Pattern design"
        ])
        
        if st.button("Generate AI Design Prompts", key="design_prompt"):
            if product_description and design_theme:
                with st.spinner("Generating design prompts..."):
                    try:
                        system_prompt = "You are a professional designer. You create detailed design prompts for AI tools (Midjourney, DALLE) for Etsy sales."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        Target Audience: {target_audience}
                        Design Style: {design_theme}
                        Design Type: {design_type}
                        
                        Create detailed, professional design prompts for Midjourney/DALLE based on this information:
                        
                        1. Main Prompt (for Midjourney/DALLE)
                        2. Style Parameters
                        3. Quality Settings
                        4. Alternative Prompt Suggestions (3 variations)
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter product description and design theme first.")
                
        # AI Image Generation Section
        st.markdown("---")
        st.markdown('<div class="section-header">🖼️ ' + ('AI Tasarım Oluştur' if st.session_state['language'] == 'tr' else 'Generate AI Design') + '</div>', unsafe_allow_html=True)
        
        design_prompt_input = st.text_area(
            "Tasarım prompt'ı:" if st.session_state['language'] == 'tr' else "Design prompt:",
            placeholder="funny cat wearing sunglasses t-shirt design, minimalist style" if st.session_state['language'] == 'en' else "komik gözlüklü kedi t-shirt tasarımı, minimalist stil",
            height=100
        )
        
        image_size = st.selectbox(
            "Görsel boyutu:" if st.session_state['language'] == 'tr' else "Image size:",
            ["1024x1024", "1792x1024", "1024x1792"]
        )
        
        if st.button("🎨 " + ("Tasarım Oluştur" if st.session_state['language'] == 'tr' else "Generate Design"), key="generate_design_step1"):
            if design_prompt_input.strip():
                with st.spinner("Tasarım oluşturuluyor..." if st.session_state['language'] == 'tr' else "Generating design..."):
                    try:
                        response = client.images.generate(
                            model="dall-e-2",
                            prompt=design_prompt_input,
                            size=image_size,
                            n=1,
                        )
                        
                        image_url = response.data[0].url
                        st.image(image_url, caption="Oluşturulan Tasarım" if st.session_state['language'] == 'tr' else "Generated Design")
                        
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ {'Tasarım başarıyla oluşturuldu!' if st.session_state['language'] == 'tr' else 'Design generated successfully!'}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download link
                        st.markdown(f"**{'İndir:' if st.session_state['language'] == 'tr' else 'Download:'}** [{'Tasarımı İndir' if st.session_state['language'] == 'tr' else 'Download Design'}]({image_url})")
                        
                    except Exception as e:
                        if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                            st.error("🚫 " + ("OpenAI API kotanız dolmuş. Lütfen planınızı kontrol edin." if st.session_state['language'] == 'tr' else "OpenAI API quota exceeded. Please check your plan."))
                        else:
                            st.error(f"{'Hata:' if st.session_state['language'] == 'tr' else 'Error:'} {str(e)}")
            else:
                st.warning("Lütfen bir tasarım prompt'ı girin." if st.session_state['language'] == 'tr' else "Please enter a design prompt.")

# Step 2: Design Optimization
with tabs[1]:
    st.markdown('<div class="step-header">⚙️ Adım 2: Tasarımı Baskıya Uygun Hale Getirme</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">⚙️ Step 2: Prepare Design for Printing</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        st.markdown("""
        <div class="tip-box">
        ✅ <strong>Gereksinimler:</strong><br>
        • Format: PNG (transparan arka plan)<br>
        • Boyut: 4500 x 5400 px<br>
        • Çözünürlük: 300 DPI<br>
        • Ortalanmış ve dengeli yerleştirme
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Baskı Hazırlık Kontrolü Oluştur", key="print_check"):
            with st.spinner("Kontrol listesi oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir baskı uzmanısın. DTG (Direct-to-Garment) baskı için tasarım optimizasyon tavsiyeleri veriyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Kategori: {product_category}
                    
                    Bu ürün için DTG baskıya uygun tasarım hazırlama rehberi oluştur:
                    1. Teknik Spesifikasyonlar
                    2. Renk Ayarları
                    3. Dosya Formatı Önerileri
                    4. Kalite Kontrol Listesi
                    5. Yaygın Hatalar ve Nasıl Kaçınılır
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        ✅ <strong>Requirements:</strong><br>
        • Format: PNG (transparent background)<br>
        • Size: 4500 x 5400 px<br>
        • Resolution: 300 DPI<br>
        • Centered and balanced placement
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Print Preparation Guide", key="print_check"):
            if product_description:
                with st.spinner("Generating preparation guide..."):
                    try:
                        system_prompt = "You are a printing expert. You provide design optimization advice for DTG (Direct-to-Garment) printing."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        
                        Create a comprehensive DTG printing design preparation guide for this product:
                        1. Technical Specifications
                        2. Color Settings
                        3. File Format Recommendations
                        4. Quality Control Checklist
                        5. Common Mistakes and How to Avoid Them
                        6. Best Practices for DTG Printing
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 3: Mockup Creation
with tabs[2]:
    st.markdown('<div class="step-header">📱 Adım 3: Mockup Oluşturma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📱 Step 3: Create Mockups</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        mockup_type = st.selectbox("Mockup türü:", [
            "Düz t-shirt mockup",
            "Model üzerinde mockup",
            "Yaşam tarzı mockup",
            "Stüdyo çekim mockup",
            "Flat lay mockup"
        ])
        
        if st.button("AI Mockup Prompt'ı Oluştur", key="mockup_prompt"):
            with st.spinner("Mockup prompt'ı oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir ürün fotoğrafçısısın. Etsy satışları için profesyonel mockup oluşturma konusunda uzmanısın."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Hedef Kitle: {target_audience}
                    Mockup Türü: {mockup_type}
                    
                    Bu ürün için DALLE ile oluşturulacak profesyonel mockup prompt'ı oluştur:
                    1. Ana görsel prompt
                    2. Aydınlatma ayarları
                    3. Arka plan önerileri
                    4. Çekim açısı önerileri
                    5. 3 farklı alternatif mockup prompt'ı
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        if st.button("AI Mockup Prompt'ı Oluştur", key="mockup_prompt_tr"):
            with st.spinner("Mockup prompt'ı oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir ürün fotoğrafçısısın. Etsy satışları için profesyonel mockup oluşturma konusunda uzmanısın."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Hedef Kitle: {target_audience}
                    Mockup Türü: {mockup_type}
                    
                    Bu ürün için DALLE ile oluşturulacak profesyonel mockup prompt'ı oluştur:
                    1. Ana görsel prompt
                    2. Aydınlatma ayarları
                    3. Arka plan önerileri
                    4. Çekim açısı önerileri
                    5. 3 farklı alternatif mockup prompt'ı
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
        
        # AI Mockup Generation Section for Turkish
        st.markdown("---")
        st.markdown('<div class="section-header">📸 AI Mockup Oluştur</div>', unsafe_allow_html=True)
        
        mockup_prompt_input_tr = st.text_area(
            "Mockup prompt'ı:",
            placeholder="siyah grafik tasarımlı t-shirt giyen genç kadın, yaşam tarzı fotoğrafçılığı, doğal ışık",
            height=100,
            key="mockup_prompt_input_tr"
        )
        
        mockup_size_tr = st.selectbox(
            "Mockup boyutu:",
            ["1024x1024", "1792x1024", "1024x1792"],
            key="mockup_size_tr"
        )
        
        if st.button("📸 Mockup Oluştur", key="generate_mockup_step3_tr"):
            if mockup_prompt_input_tr.strip():
                with st.spinner("Mockup oluşturuluyor..."):
                    try:
                        response = client.images.generate(
                            model="dall-e-2",
                            prompt=mockup_prompt_input_tr,
                            size=mockup_size_tr,
                            n=1,
                        )
                        
                        image_url = response.data[0].url
                        st.image(image_url, caption="Oluşturulan Mockup")
                        
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ Mockup başarıyla oluşturuldu!
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download link
                        st.markdown(f"**İndir:** [Mockup İndir]({image_url})")
                        
                    except Exception as e:
                        if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                            st.error("🚫 OpenAI API kotanız dolmuş. Lütfen planınızı kontrol edin.")
                        else:
                            st.error(f"Hata: {str(e)}")
            else:
                st.warning("Lütfen bir mockup prompt'ı girin.")
                
        st.markdown("""
        <div class="tip-box">
        💡 <strong>İpucu:</strong> En az 2 farklı mockup oluşturun: düz ürün çekimi + yaşam tarzı/model çekimi
        </div>
        """, unsafe_allow_html=True)
        
        mockup_type = st.selectbox("Select mockup type:", [
            "Flat t-shirt mockup",
            "Model wearing mockup",
            "Lifestyle mockup",
            "Studio shot mockup",
            "Flat lay mockup"
        ])
        
        if st.button("Generate AI Mockup Prompts", key="mockup_prompt"):
            if product_description:
                with st.spinner("Generating mockup prompts..."):
                    try:
                        system_prompt = "You are a product photographer expert specializing in creating professional mockups for Etsy sales."
                        user_prompt = f"""
                        Product: {product_description}
                        Target Audience: {target_audience}
                        Mockup Type: {mockup_type}
                        
                        Create professional DALLE prompts for this product mockup:
                        1. Main visual prompt
                        2. Lighting setup recommendations
                        3. Background suggestions
                        4. Camera angle recommendations
                        5. 3 alternative mockup prompt variations
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")
                
        # AI Mockup Generation Section
        st.markdown("---")
        st.markdown('<div class="section-header">📸 ' + ('AI Mockup Oluştur' if st.session_state['language'] == 'tr' else 'Generate AI Mockup') + '</div>', unsafe_allow_html=True)
        
        mockup_prompt_input = st.text_area(
            "Mockup prompt'ı:" if st.session_state['language'] == 'tr' else "Mockup prompt:",
            placeholder="young woman wearing a black t-shirt with graphic design, lifestyle photography, natural lighting" if st.session_state['language'] == 'en' else "siyah grafik tasarımlı t-shirt giyen genç kadın, yaşam tarzı fotoğrafçılığı, doğal ışık",
            height=100,
            key="mockup_prompt_input"
        )
        
        mockup_size = st.selectbox(
            "Mockup boyutu:" if st.session_state['language'] == 'tr' else "Mockup size:",
            ["1024x1024", "1792x1024", "1024x1792"],
            key="mockup_size"
        )
        
        if st.button("📸 " + ("Mockup Oluştur" if st.session_state['language'] == 'tr' else "Generate Mockup"), key="generate_mockup_step3"):
            if mockup_prompt_input.strip():
                with st.spinner("Mockup oluşturuluyor..." if st.session_state['language'] == 'tr' else "Generating mockup..."):
                    try:
                        response = client.images.generate(
                            model="dall-e-2",
                            prompt=mockup_prompt_input,
                            size=mockup_size,
                            n=1,
                        )
                        
                        image_url = response.data[0].url
                        st.image(image_url, caption="Oluşturulan Mockup" if st.session_state['language'] == 'tr' else "Generated Mockup")
                        
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ {'Mockup başarıyla oluşturuldu!' if st.session_state['language'] == 'tr' else 'Mockup generated successfully!'}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download link
                        st.markdown(f"**{'İndir:' if st.session_state['language'] == 'tr' else 'Download:'}** [{'Mockup İndir' if st.session_state['language'] == 'tr' else 'Download Mockup'}]({image_url})")
                        
                    except Exception as e:
                        if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                            st.error("🚫 " + ("OpenAI API kotanız dolmuş. Lütfen planınızı kontrol edin." if st.session_state['language'] == 'tr' else "OpenAI API quota exceeded. Please check your plan."))
                        else:
                            st.error(f"{'Hata:' if st.session_state['language'] == 'tr' else 'Error:'} {str(e)}")
            else:
                st.warning("Lütfen bir mockup prompt'ı girin." if st.session_state['language'] == 'tr' else "Please enter a mockup prompt.")

# Step 4: Image Preparation
with tabs[3]:
    st.markdown('<div class="step-header">🖼️ Adım 4: Ürün Görsellerinin Hazırlanması</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🖼️ Step 4: Prepare Product Images</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("Görsel Optimizasyon Rehberi Oluştur", key="image_guide"):
            with st.spinner("Görsel rehberi oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir e-ticaret görsel uzmanısın. Etsy için ürün görsellerini optimize etme konusunda uzmanısın."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Kategori: {product_category}
                    
                    Bu ürün için Etsy görsel optimizasyon rehberi oluştur:
                    1. Görsel boyut ve format özellikleri (2000x2000px kare format)
                    2. Ana ürün görseli özellikleri
                    3. Ek görseller (mockup, detay, kullanım)
                    4. SEO için alt text önerileri
                    5. Görsel sıralaması stratejisi
                    6. Mobil optimizasyon ipuçları
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        ✅ <strong>Etsy Image Requirements:</strong><br>
        • Size: Square (2000x2000 px or larger)<br>
        • Format: JPEG or PNG<br>
        • Up to 10 images per listing<br>
        • First image is most important for search
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Image Optimization Guide", key="image_guide"):
            if product_description:
                with st.spinner("Generating image guide..."):
                    try:
                        system_prompt = "You are an e-commerce visual expert specializing in Etsy product image optimization."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        
                        Create a comprehensive Etsy image optimization guide for this product:
                        1. Image size and format specifications (2000x2000px square format)
                        2. Main product image characteristics
                        3. Additional images (mockups, details, usage)
                        4. SEO alt text suggestions
                        5. Image sequence strategy
                        6. Mobile optimization tips
                        7. Best practices for Etsy search visibility
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")
                
        # AI Image Enhancement Section for Turkish
        st.markdown("---")
        st.markdown('<div class="section-header">✨ Görsel İyileştirme</div>', unsafe_allow_html=True)
        
        uploaded_image_tr = st.file_uploader(
            "Görseli yükleyin:",
            type=['png', 'jpg', 'jpeg'],
            key="enhance_image_upload_tr"
        )
        
        if uploaded_image_tr is not None:
            st.image(uploaded_image_tr, caption="Orijinal Görsel", width=300)
            
            enhancement_prompt_tr = st.text_area(
                "İyileştirme talimatı:",
                placeholder="bu görseli daha profesyonel yap, parlaklık ve kontrastı artır",
                height=80,
                key="enhancement_prompt_tr"
            )
            
            if st.button("✨ Görseli İyileştir", key="enhance_image_step4_tr"):
                if enhancement_prompt_tr.strip():
                    with st.spinner("Görsel iyileştiriliyor..."):
                        try:
                            # Convert uploaded image to BytesIO
                            image = Image.open(uploaded_image_tr)
                            
                            # Convert to RGB if necessary
                            if image.mode in ('RGBA', 'LA', 'P'):
                                image = image.convert('RGB')
                            
                            # Save to BytesIO
                            img_buffer = io.BytesIO()
                            image.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            response = client.images.edit(
                                model="dall-e-2",
                                image=img_buffer,
                                prompt=enhancement_prompt_tr,
                                size="1024x1024",
                                n=1
                            )
                            
                            enhanced_url = response.data[0].url
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(uploaded_image_tr, caption="Orijinal", width=250)
                            with col2:
                                st.image(enhanced_url, caption="İyileştirilmiş", width=250)
                            
                            st.markdown(f"""
                            <div class="success-box">
                            ✅ Görsel başarıyla iyileştirildi!
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download link
                            st.markdown(f"**İndir:** [İyileştirilmiş Görseli İndir]({enhanced_url})")
                            
                        except Exception as e:
                            if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                                st.error("🚫 OpenAI API kotanız dolmuş. Lütfen planınızı kontrol edin.")
                            else:
                                st.error(f"Hata: {str(e)}")
                else:
                    st.warning("Lütfen iyileştirme talimatı girin.")
                    
        st.markdown("""
        <div class="tip-box">
        ✅ <strong>Etsy Görsel Gereksinimleri:</strong><br>
        • Boyut: Kare (2000x2000 px veya daha büyük)<br>
        • Format: JPEG veya PNG<br>
        • Listeleme başına 10 görsele kadar<br>
        • İlk görsel arama için en önemli
        </div>
        """, unsafe_allow_html=True)

# Step 5: Title Creation
with tabs[4]:
    st.markdown('<div class="step-header">📝 Adım 5: Ürün Başlığı Yazma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📝 Step 5: Write Product Title</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        num_titles = st.slider("Kaç başlık oluşturulsun?", 1, 10, 5)
        
        if st.button("SEO Optimized Başlıklar Oluştur", key="titles"):
            if product_description:
                with st.spinner("Başlıklar oluşturuluyor..."):
                    try:
                        system_prompt = "Sen bir Etsy SEO uzmanısın. 130-140 karakter arası, yüksek dönüşüm sağlayan başlıklar oluşturuyorsun."
                        user_prompt = f"""
                        Ürün: {product_description}
                        Kategori: {product_category}
                        Hedef Kitle: {target_audience}
                        Stil: {design_theme}
                        
                        {num_titles} adet SEO optimized Etsy başlığı oluştur:
                        - Her başlık 130-140 karakter arası
                        - Anahtar kelimeler + tema + hedef kitle + ürün türü
                        - Yüksek arama hacimli kelimeler kullan
                        - Her başlığın sonunda karakter sayısını belirt
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Lütfen ürün açıklaması girin.")
    else:
        st.markdown("""
        <div class="tip-box">
        📝 <strong>Title Requirements:</strong><br>
        • Length: 130-140 characters<br>
        • Include: keywords + theme + target audience + product type<br>
        • Example: "Witchy Halloween Shirt For Women Retro Vintage Cute Spooky T-Shirt Gift For Her Fall Graphic"
        </div>
        """, unsafe_allow_html=True)
        
        num_titles = st.slider("How many titles to generate?", 1, 10, 5)
        
        if st.button("Generate SEO Optimized Titles", key="titles"):
            if product_description:
                with st.spinner("Generating titles..."):
                    try:
                        system_prompt = "You are an Etsy SEO expert. You create high-converting titles between 130-140 characters that maximize search visibility."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        Target Audience: {target_audience}
                        Style: {design_theme}
                        
                        Create {num_titles} SEO optimized Etsy titles:
                        - Each title 130-140 characters
                        - Keywords + theme + target audience + product type
                        - Use high search volume keywords
                        - Include character count at the end of each title
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 6: Tag Creation
with tabs[5]:
    st.markdown('<div class="step-header">🏷️ Adım 6: Etiket (Tag) Ekleme</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🏷️ Step 6: Add Tags</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("13 Etsy Etiketi Oluştur", key="tags"):
            if product_description:
                with st.spinner("Etiketler oluşturuluyor..."):
                    try:
                        system_prompt = "Sen bir Etsy SEO uzmanısın. Her biri maksimum 20 karakter olan, yüksek arama hacimli etiketler oluşturuyorsun."
                        user_prompt = f"""
                        Ürün: {product_description}
                        Kategori: {product_category}
                        Hedef Kitle: {target_audience}
                        Stil: {design_theme}
                        
                        13 adet Etsy etiketi oluştur:
                        - Her etiket maksimum 20 karakter
                        - Virgülle ayrılmış tek satır format
                        - Yüksek arama hacimli kelimeler
                        - Long-tail ve short-tail karışımı
                        - Seasonally relevant etiketler ekle
                        
                        Format: etiket1,etiket2,etiket3...
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Lütfen ürün açıklaması girin.")
    else:
        st.markdown("""
        <div class="tip-box">
        🏷️ <strong>Tag Requirements:</strong><br>
        • 13 tags available<br>
        • Max 20 characters each<br>
        • Comma-separated format<br>
        • Mix of long-tail and short-tail keywords
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate 13 Etsy Tags", key="tags"):
            if product_description:
                with st.spinner("Generating tags..."):
                    try:
                        system_prompt = "You are an Etsy SEO expert. You create high search volume tags, each maximum 20 characters."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        Target Audience: {target_audience}
                        Style: {design_theme}
                        
                        Create 13 Etsy tags:
                        - Each tag maximum 20 characters
                        - Comma-separated single line format
                        - High search volume keywords
                        - Mix of long-tail and short-tail keywords
                        - Include seasonally relevant tags
                        
                        Format: tag1,tag2,tag3...
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 7: Description Creation
with tabs[6]:
    st.markdown('<div class="step-header">📄 Adım 7: Ürün Açıklaması Yazma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📄 Step 7: Write Product Description</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        material = st.text_input("Malzeme:", placeholder="örn., %100 Pamuk")
        print_method = st.selectbox("Baskı Yöntemi:", ["DTG (Direct-to-Garment)", "Screen Print", "Heat Transfer", "Vinyl"])
        
        if st.button("Ürün Açıklaması Oluştur", key="description"):
            if product_description:
                with st.spinner("Açıklama oluşturuluyor..."):
                    try:
                        system_prompt = "Sen bir Etsy copywriter uzmanısın. Satış odaklı, ikna edici ürün açıklamaları yazıyorsun."
                        user_prompt = f"""
                        Ürün: {product_description}
                        Hedef Kitle: {target_audience}
                        Malzeme: {material}
                        Baskı Yöntemi: {print_method}
                        
                        Etsy için profesyonel ürün açıklaması oluştur:
                        1. Bold başlık (ürün adı)
                        2. Ürün hikayesi ve faydaları
                        3. Teknik özellikler
                        4. Bakım talimatları
                        5. Etkinlik/kullanım önerileri
                        6. Satın alma teşviki
                        
                        Format: Markdown kullan, emojiler ekle
                        """
                        
                        result = call_openai(system_prompt, user_prompt, 1000)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Lütfen ürün açıklaması girin.")
    else:
        st.markdown("""
        <div class="tip-box">
        📄 <strong>Description Format:</strong><br>
        • Start with bold product title<br>
        • Include product story and benefits<br>
        • Add technical specifications<br>
        • Care instructions and usage suggestions
        </div>
        """, unsafe_allow_html=True)
        
        material = st.text_input("Material:", placeholder="e.g., 100% Cotton")
        print_method = st.selectbox("Print Method:", ["DTG (Direct-to-Garment)", "Screen Print", "Heat Transfer", "Vinyl"])
        
        if st.button("Generate Product Description", key="description"):
            if product_description:
                with st.spinner("Generating description..."):
                    try:
                        system_prompt = "You are an Etsy copywriting expert. You write sales-focused, persuasive product descriptions."
                        user_prompt = f"""
                        Product: {product_description}
                        Target Audience: {target_audience}
                        Material: {material}
                        Print Method: {print_method}
                        
                        Create a professional Etsy product description:
                        1. Bold title (product name)
                        2. Product story and benefits
                        3. Technical specifications
                        4. Care instructions
                        5. Event/usage suggestions
                        6. Purchase incentive
                        
                        Format: Use Markdown, include emojis
                        """
                        
                        result = call_openai(system_prompt, user_prompt, 1000)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 8: Variations Setup
with tabs[7]:
    st.markdown('<div class="step-header">🎨 Adım 8: Varyasyonları Ayarlama</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🎨 Step 8: Set Variations</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("Renk ve Beden Varyasyonları Öner", key="variations"):
            with st.spinner("Varyasyonlar oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir e-ticaret uzmanısın. Etsy için optimal renk ve beden varyasyonları öneriyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Hedef Kitle: {target_audience}
                    Tasarım Stili: {design_theme}
                    
                    Bu ürün için Etsy varyasyon stratejisi oluştur:
                    1. Önerilen renkler (en popüler 5-8 renk)
                    2. Beden aralığı (S-3XL arası)
                    3. Her varyasyonun satış potansiyeli
                    4. Stok yönetimi önerileri
                    5. Fiyat farklılaştırma stratejisi
                    6. Hangi varyasyonlardan başlanması gerektiği
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        🎨 <strong>Variation Options:</strong><br>
        • Colors: Black, White, Heather Gray, Navy, etc.<br>
        • Sizes: S, M, L, XL, 2XL, 3XL<br>
        • Enable "Product with variations" in Etsy<br>
        • Set stock and price for each variation
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Color & Size Variation Strategy", key="variations"):
            if product_description:
                with st.spinner("Generating variations..."):
                    try:
                        system_prompt = "You are an e-commerce expert. You recommend optimal color and size variations for Etsy."
                        user_prompt = f"""
                        Product: {product_description}
                        Target Audience: {target_audience}
                        Design Style: {design_theme}
                        
                        Create an Etsy variation strategy for this product:
                        1. Recommended colors (top 5-8 popular colors)
                        2. Size range (S-3XL)
                        3. Sales potential for each variation
                        4. Inventory management recommendations
                        5. Price differentiation strategy
                        6. Which variations to start with
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 9: Pricing Strategy
with tabs[8]:
    st.markdown('<div class="step-header">💰 Adım 9: Fiyatlandırma Stratejisi</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">💰 Step 9: Pricing Strategy</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        cost_price = st.number_input("Maliyet Fiyatı (USD):", min_value=0.0, value=10.0, step=0.5)
        target_margin = st.slider("Hedef Kar Marjı (%):", 10, 200, 60)
        
        if st.button("Fiyatlandırma Stratejisi Oluştur", key="pricing"):
            with st.spinner("Fiyat stratejisi oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir e-ticaret fiyatlandırma uzmanısın. Etsy için satış psikolojisi kullanarak optimal fiyat stratejileri oluşturuyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Hedef Kitle: {target_audience}
                    Maliyet: ${cost_price}
                    Hedef Kar Marjı: %{target_margin}
                    
                    Etsy için stratejik fiyatlandırma planı oluştur:
                    1. Önerilen liste fiyatı
                    2. Gerçek satış fiyatı
                    3. İndirim stratejisi (%40 OFF görünümü)
                    4. Sezonsal fiyat ayarlamaları
                    5. Rakip analizi önerileri
                    6. Fiyat test stratejileri
                    7. Bundle/paket satış önerileri
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        💰 <strong>Pricing Psychology:</strong><br>
        • Set higher list price, then create discount campaigns<br>
        • Example: List at $39.95, run 40% off to sell at $23.95<br>
        • Use time-limited campaigns for urgency<br>
        • "Sale ends in X hours" creates urgency
        </div>
        """, unsafe_allow_html=True)
        
        cost_price = st.number_input("Cost Price (USD):", min_value=0.0, value=10.0, step=0.5)
        target_margin = st.slider("Target Profit Margin (%):", 10, 200, 60)
        
        if st.button("Generate Pricing Strategy", key="pricing"):
            if product_description:
                with st.spinner("Generating pricing strategy..."):
                    try:
                        system_prompt = "You are an e-commerce pricing expert. You create optimal pricing strategies for Etsy using sales psychology."
                        user_prompt = f"""
                        Product: {product_description}
                        Target Audience: {target_audience}
                        Cost: ${cost_price}
                        Target Margin: {target_margin}%
                        
                        Create a strategic pricing plan for Etsy:
                        1. Recommended list price
                        2. Actual selling price
                        3. Discount strategy (40% OFF appearance)
                        4. Seasonal price adjustments
                        5. Competitor analysis recommendations
                        6. Price testing strategies
                        7. Bundle/package deal suggestions
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 10: Listing Checklist
with tabs[9]:
    st.markdown('<div class="step-header">✅ Adım 10: Listeleme Kontrol</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">✅ Step 10: Listing Checklist</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("Listeleme Kontrol Listesi Oluştur", key="checklist"):
            with st.spinner("Kontrol listesi oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir Etsy uzmanısın. Ürün listeleme öncesi kapsamlı kontrol listeleri oluşturuyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Kategori: {product_category}
                    
                    Etsy'de yayınlama öncesi kapsamlı kontrol listesi oluştur:
                    1. Görsel kontrolleri (10 madde)
                    2. Metin kontrolleri (başlık, açıklama, etiketler)
                    3. Fiyat ve varyasyon kontrolleri
                    4. SEO optimizasyon kontrolleri
                    5. Yasal/telif kontrolleri
                    6. Kargo ve iade politikaları
                    7. Son kontrol maddeleri
                    
                    Her maddeyi checkbox formatında sun.
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        ✅ <strong>Pre-Launch Checklist:</strong><br>
        • All images uploaded and optimized<br>
        • Title within 130-140 characters<br>
        • All 13 tags used<br>
        • Complete product description<br>
        • Pricing and variations set<br>
        • Shipping and return policies configured
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Complete Listing Checklist", key="checklist"):
            if product_description:
                with st.spinner("Generating checklist..."):
                    try:
                        system_prompt = "You are an Etsy expert. You create comprehensive pre-listing checklists."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        
                        Create a comprehensive pre-launch checklist for Etsy:
                        1. Image controls (10 items)
                        2. Text controls (title, description, tags)
                        3. Price and variation controls
                        4. SEO optimization controls
                        5. Legal/copyright controls
                        6. Shipping and return policies
                        7. Final control items
                        
                        Present each item in checkbox format.
                        """
                        
                        result = call_openai(system_prompt, user_prompt)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 11: SEO & Promotion
with tabs[10]:
    st.markdown('<div class="step-header">📈 Adım 11: SEO ve Tanıtım</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📈 Step 11: SEO & Promotion</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        budget = st.number_input("Günlük Reklam Bütçesi (USD):", min_value=1.0, value=5.0, step=1.0)
        
        if st.button("Tanıtım Stratejisi Oluştur", key="promotion"):
            with st.spinner("Tanıtım planı oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir dijital pazarlama uzmanısın. Etsy ürünleri için kapsamlı tanıtım stratejileri oluşturuyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Hedef Kitle: {target_audience}
                    Günlük Bütçe: ${budget}
                    
                    30 günlük Etsy tanıtım stratejisi oluştur:
                    1. İlk 7 gün: Lansman stratejisi
                    2. Etsy Ads optimizasyonu
                    3. Pinterest pazarlama planı
                    4. Social media stratejisi
                    5. İçerik pazarlama önerileri
                    6. İnfluencer işbirlikleri
                    7. Email pazarlama
                    8. Seasonal campaign önerileri
                    9. Performans takip metrikleri
                    """
                    
                    result = call_openai(system_prompt, user_prompt, 1200)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        📈 <strong>Promotion Channels:</strong><br>
        • Etsy Ads: Start with $1-2 daily budget<br>
        • Pinterest: Share product images<br>
        • Social Media: Instagram, Facebook, TikTok<br>
        • Content Marketing: Blog posts, tutorials<br>
        • Email Marketing: Build customer list
        </div>
        """, unsafe_allow_html=True)
        
        budget = st.number_input("Daily Ad Budget (USD):", min_value=1.0, value=5.0, step=1.0)
        
        if st.button("Generate Promotion Strategy", key="promotion"):
            if product_description:
                with st.spinner("Generating promotion plan..."):
                    try:
                        system_prompt = "You are a digital marketing expert. You create comprehensive promotion strategies for Etsy products."
                        user_prompt = f"""
                        Product: {product_description}
                        Target Audience: {target_audience}
                        Daily Budget: ${budget}
                        
                        Create a 30-day Etsy promotion strategy:
                        1. First 7 days: Launch strategy
                        2. Etsy Ads optimization
                        3. Pinterest marketing plan
                        4. Social media strategy
                        5. Content marketing recommendations
                        6. Influencer collaborations
                        7. Email marketing
                        8. Seasonal campaign recommendations
                        9. Performance tracking metrics
                        """
                        
                        result = call_openai(system_prompt, user_prompt, 1200)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 12: Analytics & Optimization
with tabs[11]:
    st.markdown('<div class="step-header">📊 Adım 12: Analiz ve Optimizasyon</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📊 Step 12: Analytics & Optimization</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("Optimizasyon Rehberi Oluştur", key="optimization"):
            with st.spinner("Optimizasyon planı oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir e-ticaret analitik uzmanısın. Etsy ürün performansını analiz edip optimizasyon önerileri sunuyorsun."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Kategori: {product_category}
                    
                    Etsy ürün optimizasyon rehberi oluştur:
                    1. Takip edilmesi gereken metrikler
                    2. Haftalık analiz rutini
                    3. Düşük performans belirtileri
                    4. Başlık optimizasyon stratejileri
                    5. Görsel refresh teknikleri
                    6. Fiyat optimizasyon testleri
                    7. Etiket A/B test önerileri
                    8. Seasonal update planı
                    9. Rekabet analizi yöntemleri
                    10. Conversion rate iyileştirme
                    """
                    
                    result = call_openai(system_prompt, user_prompt, 1200)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        📊 <strong>Key Metrics to Track:</strong><br>
        • Views, Clicks, Conversion Rate<br>
        • Favorites and Cart Additions<br>
        • Search Position for Key Terms<br>
        • Competitor Performance<br>
        • Seasonal Trends
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Optimization Guide", key="optimization"):
            if product_description:
                with st.spinner("Generating optimization plan..."):
                    try:
                        system_prompt = "You are an e-commerce analytics expert. You analyze Etsy product performance and provide optimization recommendations."
                        user_prompt = f"""
                        Product: {product_description}
                        Category: {product_category}
                        
                        Create an Etsy product optimization guide:
                        1. Metrics to track
                        2. Weekly analysis routine
                        3. Low performance indicators
                        4. Title optimization strategies
                        5. Image refresh techniques
                        6. Price optimization tests
                        7. Tag A/B test recommendations
                        8. Seasonal update plan
                        9. Competitor analysis methods
                        10. Conversion rate improvement
                        """
                        
                        result = call_openai(system_prompt, user_prompt, 1200)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Step 13: Order Management
with tabs[12]:
    st.markdown('<div class="step-header">🚚 Adım 13: Sipariş Yönetimi</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🚚 Step 13: Order Management</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        pod_service = st.selectbox("Print-on-Demand Servisi:", [
            "Printify",
            "Printful",
            "Gooten",
            "Lulu xPress",
            "Kendi üretimim"
        ])
        
        if st.button("Sipariş Yönetim Sistemi Kur", key="order_mgmt"):
            with st.spinner("Sipariş sistemi oluşturuluyor..."):
                try:
                    system_prompt = "Sen bir e-ticaret operasyon uzmanısın. Print-on-demand ve sipariş yönetimi sistemleri konusunda uzmanısın."
                    user_prompt = f"""
                    Ürün: {product_description}
                    POD Servisi: {pod_service}
                    
                    Kapsamlı sipariş yönetim sistemi kur:
                    1. {pod_service} entegrasyon adımları
                    2. Otomatik sipariş işleme ayarları
                    3. Kalite kontrol protokolleri
                    4. Müşteri iletişim şablonları
                    5. Kargo takip sistemi
                    6. İade/değişim prosedürleri
                    7. Stok yönetimi
                    8. Müşteri hizmetleri protokolleri
                    9. Problem çözme rehberi
                    10. Performans izleme metrikleri
                    """
                    
                    result = call_openai(system_prompt, user_prompt, 1200)
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown("""
        <div class="tip-box">
        🚚 <strong>Order Management Setup:</strong><br>
        • Connect Etsy to Print-on-Demand service<br>
        • Set up automatic order processing<br>
        • Configure quality control protocols<br>
        • Create customer communication templates<br>
        • Set up tracking and shipping notifications
        </div>
        """, unsafe_allow_html=True)
        
        pod_service = st.selectbox("Print-on-Demand Service:", [
            "Printify",
            "Printful",
            "Gooten",
            "Lulu xPress",
            "Self Production"
        ])
        
        if st.button("Setup Order Management System", key="order_mgmt"):
            if product_description:
                with st.spinner("Setting up order system..."):
                    try:
                        system_prompt = "You are an e-commerce operations expert. You specialize in print-on-demand and order management systems."
                        user_prompt = f"""
                        Product: {product_description}
                        POD Service: {pod_service}
                        
                        Set up a comprehensive order management system:
                        1. {pod_service} integration steps
                        2. Automatic order processing settings
                        3. Quality control protocols
                        4. Customer communication templates
                        5. Shipping tracking system
                        6. Return/exchange procedures
                        7. Inventory management
                        8. Customer service protocols
                        9. Problem resolution guide
                        10. Performance monitoring metrics
                        """
                        
                        result = call_openai(system_prompt, user_prompt, 1200)
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Please enter a product description first.")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666; padding: 20px;'>{t('footer')}</div>", unsafe_allow_html=True) 
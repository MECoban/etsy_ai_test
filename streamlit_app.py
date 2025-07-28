"""
Etsy AI Listing Assistant - Main Application
Refactored to use modular structure
"""

import streamlit as st
from PIL import Image
import io

# Import our modular utilities
from config.config_manager import config
from config.translations import get_translation
from utils import (
    init_session_state, get_form_data, set_form_data,
    call_openai, generate_image, enhance_image,
    get_cache_stats, get_rate_limit_status, get_analytics_summary,
    track_feature_usage, clear_cache
)

# Initialize configuration and session state
config.initialize()
init_session_state()


def t(key):
    """Get translation for current language"""
    return config.get_translation(key)


def load_custom_css():
    """Load custom CSS for the application"""
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
    .stTextInput > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stTextArea > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
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
</style>
"""
    return css_content


@st.cache_data
def apply_custom_css():
    """Apply custom CSS with caching"""
    return load_custom_css()


def render_sidebar():
    """Render the sidebar with form inputs and controls"""
    with st.sidebar:
        # Language selection
        language = st.selectbox(
            t("language_selector"), 
            ["Türkçe", "English"], 
            index=0 if st.session_state['language'] == 'tr' else 1
        )
        st.session_state['language'] = 'tr' if language == "Türkçe" else 'en'
        
        st.markdown("---")
        st.markdown("### " + t("product_info"))
        
        # Form inputs with validation
        product_description = st.text_area(
            t("product_description"),
            value=get_form_data("product_description"),
            placeholder=t("product_desc_placeholder"),
            height=120,
            key="product_desc_input",
            on_change=lambda: set_form_data("product_description", st.session_state.product_desc_input),
            help="Minimum 10 characters, maximum 1000 characters"
        )
        
        # Real-time validation
        if product_description:
            char_count = len(product_description)
            if char_count < 10:
                st.warning(f"⚠️ Too short: {char_count}/10 minimum characters")
            elif char_count > 1000:
                st.error(f"❌ Too long: {char_count}/1000 maximum characters")
            else:
                st.success(f"✅ Good length: {char_count}/1000 characters")
        
        # Other form fields
        product_category = st.text_input(
            t("product_category"),
            value=get_form_data("product_category"),
            placeholder=t("product_cat_placeholder"),
            key="product_cat_input",
            on_change=lambda: set_form_data("product_category", st.session_state.product_cat_input)
        )
        
        target_audience = st.text_input(
            t("target_audience"),
            value=get_form_data("target_audience"),
            placeholder=t("target_audience_placeholder"),
            key="target_audience_input",
            on_change=lambda: set_form_data("target_audience", st.session_state.target_audience_input)
        )
        
        design_theme = st.text_input(
            t("design_theme"),
            value=get_form_data("design_theme"),
            placeholder=t("design_theme_placeholder"),
            key="design_theme_input",
            on_change=lambda: set_form_data("design_theme", st.session_state.design_theme_input)
        )
        
        # Form completion indicator
        st.markdown("---")
        st.markdown("📊 **Form Completion**")
        
        required_fields = [
            ("Product Description", product_description, 10),
            ("Product Category", product_category, 3),
            ("Target Audience", target_audience, 5),
            ("Design Theme", design_theme, 3)
        ]
        
        completed_fields = sum(1 for _, value, min_len in required_fields 
                             if value and len(value.strip()) >= min_len)
        completion_percentage = (completed_fields / len(required_fields)) * 100
        
        st.progress(completion_percentage / 100)
        st.markdown(f"**{completion_percentage:.0f}% Complete** ({completed_fields}/{len(required_fields)} fields)")
        
        # Cache and system stats
        render_system_stats()


def render_system_stats():
    """Render system statistics in sidebar"""
    # Cache statistics
    st.markdown("---")
    st.markdown("📊 **Cache Stats**")
    
    cache_stats = get_cache_stats()
    if cache_stats['total_calls'] > 0:
        st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.1f}%")
        st.metric("Cache Size", cache_stats['cache_size'])
    else:
        st.info("No API calls yet")
    
    if st.button("🗑️ Clear Cache"):
        clear_cache()
        st.success("Cache cleared!")
        st.rerun()
    
    # Rate limit status
    st.markdown("---")
    st.markdown("⏱️ **Rate Limits**")
    
    rate_status = get_rate_limit_status()
    st.progress(rate_status['percentage_used'] / 100)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Remaining", f"{rate_status['remaining_requests']}/{rate_status['max_requests']}")
    with col2:
        if rate_status['wait_time'] > 0:
            st.metric("Wait Time", f"{rate_status['wait_time']:.1f}s")
        else:
            st.metric("Status", "✅ Ready")
    
    # Analytics
    st.markdown("---")
    st.markdown("📊 **Analytics**")
    
    analytics = get_analytics_summary()
    if analytics and analytics['total_api_calls'] > 0:
        st.metric("Session Time", f"{analytics['session_duration']:.1f} min")
        st.metric("API Calls", analytics['total_api_calls'])
        st.metric("Success Rate", f"{analytics['success_rate']:.1f}%")


def render_step_1():
    """Render Step 1: Design Creation"""
    st.markdown('<div class="step-header">🎨 Step 1: Design Selection / Creation</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        st.markdown("""
        <div class="tip-box">
        💡 <strong>İpucu:</strong> AI ile özgün tasarımlar oluşturabilir veya hazır tasarımları kullanabilirsiniz.
        </div>
        """, unsafe_allow_html=True)
        
        design_prompt_input = st.text_area(
            "Tasarım prompt'ı:",
            placeholder="komik gözlüklü kedi t-shirt tasarımı, minimalist stil",
            height=100,
            key="design_prompt_tr"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            image_size = st.selectbox("Görsel boyutu:", ["1024x1024", "1792x1024", "1024x1792"])
        with col2:
            if st.button("🎨 Tasarım Oluştur"):
                if design_prompt_input.strip():
                    track_feature_usage('design_generation')
                    with st.spinner("Tasarım oluşturuluyor..."):
                        image_url = generate_image(design_prompt_input, image_size)
                        if image_url:
                            st.image(image_url, caption="Oluşturulan Tasarım")
                            st.markdown('<div class="success-box">✅ Tasarım başarıyla oluşturuldu!</div>', unsafe_allow_html=True)
                            st.markdown(f"[Tasarımı İndir]({image_url})")
                else:
                    st.warning("Lütfen bir tasarım prompt'ı girin.")
    else:
        st.markdown("""
        <div class="tip-box">
        💡 <strong>Tip:</strong> Create original designs with AI or use ready-made designs.
        </div>
        """, unsafe_allow_html=True)
        
        design_prompt_input = st.text_area(
            "Design prompt:",
            placeholder="funny cat wearing sunglasses t-shirt design, minimalist style",
            height=100,
            key="design_prompt_en"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            image_size = st.selectbox("Image size:", ["1024x1024", "1792x1024", "1024x1792"])
        with col2:
            if st.button("🎨 Generate Design"):
                if design_prompt_input.strip():
                    track_feature_usage('design_generation')
                    with st.spinner("Generating design..."):
                        image_url = generate_image(design_prompt_input, image_size)
                        if image_url:
                            st.image(image_url, caption="Generated Design")
                            st.markdown('<div class="success-box">✅ Design generated successfully!</div>', unsafe_allow_html=True)
                            st.markdown(f"[Download Design]({image_url})")
                else:
                    st.warning("Please enter a design prompt.")


def render_step_5():
    """Render Step 5: Title Creation"""
    st.markdown('<div class="step-header">📝 Step 5: Write Product Title</div>', unsafe_allow_html=True)
    
    product_description = get_form_data("product_description")
    target_audience = get_form_data("target_audience")
    design_theme = get_form_data("design_theme")
    
    if not product_description:
        st.warning("Please fill in product information in the sidebar first.")
        return
    
    num_titles = st.slider("Number of titles to generate:", 1, 10, 5)
    
    if st.button("🚀 Generate SEO Titles"):
        track_feature_usage('title_generation')
        with st.spinner("Generating titles..."):
            system_prompt = "You are an Etsy SEO expert. Create high-converting titles between 130-140 characters."
            user_prompt = f"""
            Product: {product_description}
            Target Audience: {target_audience}
            Style: {design_theme}
            
            Create {num_titles} SEO optimized Etsy titles:
            - Each title 130-140 characters
            - Include keywords, theme, target audience, product type
            - Use high search volume keywords
            - Include character count for each title
            """
            
            result = call_openai(system_prompt, user_prompt)
            if result:
                st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)


def main():
    """Main application function"""
    # Apply CSS
    st.markdown(apply_custom_css(), unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1>{t('app_title')}</h1>
        <p style='font-size: 1.2em; color: #666;'>{t('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for steps
    tab_labels = [f"{t('step')} {i+1}" for i in range(13)]
    tabs = st.tabs(tab_labels)
    
    with tabs[0]:  # Step 1
        render_step_1()
    
    with tabs[4]:  # Step 5  
        render_step_5()
    
    # For now, show placeholder for other steps
    for i in range(13):
        if i not in [0, 4]:  # Skip steps we've implemented
            with tabs[i]:
                st.info(f"Step {i+1} implementation in progress...")
    
    # Footer
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #666; padding: 20px;'>{t('footer')}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main() 
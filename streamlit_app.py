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
    st.markdown('<div class="step-header">🎨 Adım 1: Tasarım Seçimi / Oluşturma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🎨 Step 1: Design Selection / Creation</div>', unsafe_allow_html=True)
    
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


def render_step_2():
    """Render Step 2: Print Preparation"""
    st.markdown('<div class="step-header">🖨️ Adım 2: Baskı Hazırlığı</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🖨️ Step 2: Print Preparation</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        st.markdown("""
        <div class="tip-box">
        💡 <strong>DTG Baskı İpuçları:</strong><br>
        • 300 DPI minimum çözünürlük<br>
        • RGB renk modu (CMYK değil)<br>
        • PNG formatında şeffaf arkaplan<br>
        • Tasarım boyutu: 10-12 inç genişlik
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Baskı Hazırlık Rehberi Oluştur"):
            with st.spinner("Baskı rehberi oluşturuluyor..."):
                system_prompt = "Sen bir DTG (Direct-to-Garment) baskı uzmanısın."
                user_prompt = f"""
                Ürün: {get_form_data('product_description')}
                
                Bu ürün için DTG baskı hazırlık rehberi oluştur:
                1. Dosya formatı ve çözünürlük gereksinimleri
                2. Renk profili ayarları (RGB vs CMYK)
                3. Tasarım boyutlandırma rehberi
                4. Farklı ürün tipleri için baskı alanları
                5. Kalite kontrol listesi
                6. Yaygın baskı hataları ve çözümleri
                """
                
                result = call_openai(system_prompt, user_prompt)
                if result:
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="tip-box">
        💡 <strong>DTG Print Tips:</strong><br>
        • 300 DPI minimum resolution<br>
        • RGB color mode (not CMYK)<br>
        • PNG format with transparent background<br>
        • Design size: 10-12 inches width
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Print Preparation Guide"):
            with st.spinner("Generating print guide..."):
                system_prompt = "You are a DTG (Direct-to-Garment) printing expert."
                user_prompt = f"""
                Product: {get_form_data('product_description')}
                
                Create a comprehensive DTG print preparation guide for this product:
                1. File format and resolution requirements
                2. Color profile settings (RGB vs CMYK)
                3. Design sizing guidelines
                4. Print areas for different product types
                5. Quality control checklist
                6. Common printing issues and solutions
                7. Pre-press optimization tips
                """
                
                result = call_openai(system_prompt, user_prompt)
                if result:
                    st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)


def render_step_3():
    """Render Step 3: Mockup Creation"""
    st.markdown('<div class="step-header">📱 Adım 3: Mockup Oluşturma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📱 Step 3: Mockup Creation</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        mockup_prompt_input = st.text_area(
            "Mockup prompt'ı:",
            placeholder="beyaz t-shirt üzerinde komik kedi tasarımı, stüdyo ışığı, profesyonel ürün fotoğrafı",
            height=100,
            key="mockup_prompt_tr"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            mockup_size = st.selectbox("Mockup boyutu:", ["1024x1024", "1792x1024", "1024x1792"])
        with col2:
            if st.button("📱 Mockup Oluştur"):
                if mockup_prompt_input.strip():
                    track_feature_usage('mockup_generation')
                    with st.spinner("Mockup oluşturuluyor..."):
                        image_url = generate_image(mockup_prompt_input, mockup_size)
                        if image_url:
                            st.image(image_url, caption="Oluşturulan Mockup")
                            st.markdown('<div class="success-box">✅ Mockup başarıyla oluşturuldu!</div>', unsafe_allow_html=True)
                            st.markdown(f"[Mockup İndir]({image_url})")
                else:
                    st.warning("Lütfen bir mockup prompt'ı girin.")
    else:
        mockup_prompt_input = st.text_area(
            "Mockup prompt:",
            placeholder="white t-shirt with funny cat design, studio lighting, professional product photography",
            height=100,
            key="mockup_prompt_en"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            mockup_size = st.selectbox("Mockup size:", ["1024x1024", "1792x1024", "1024x1792"])
        with col2:
            if st.button("📱 Generate Mockup"):
                if mockup_prompt_input.strip():
                    track_feature_usage('mockup_generation')
                    with st.spinner("Generating mockup..."):
                        image_url = generate_image(mockup_prompt_input, mockup_size)
                        if image_url:
                            st.image(image_url, caption="Generated Mockup")
                            st.markdown('<div class="success-box">✅ Mockup generated successfully!</div>', unsafe_allow_html=True)
                            st.markdown(f"[Download Mockup]({image_url})")
                else:
                    st.warning("Please enter a mockup prompt.")


def render_step_4():
    """Render Step 4: Image Preparation"""
    st.markdown('<div class="step-header">🖼️ Adım 4: Ürün Görsellerinin Hazırlanması</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🖼️ Step 4: Prepare Product Images</div>', unsafe_allow_html=True)
    
    if st.session_state['language'] == 'tr':
        if st.button("Görsel Optimizasyon Rehberi Oluştur"):
            product_description = get_form_data("product_description")
            if product_description:
                with st.spinner("Görsel rehberi oluşturuluyor..."):
                    system_prompt = "Sen bir e-ticaret görsel uzmanısın. Etsy için ürün görsellerini optimize etme konusunda uzmanısın."
                    user_prompt = f"""
                    Ürün: {product_description}
                    Kategori: {get_form_data('product_category')}
                    
                    Bu ürün için Etsy görsel optimizasyon rehberi oluştur:
                    1. Görsel boyut ve format özellikleri (2000x2000px kare format)
                    2. Ana ürün görseli özellikleri
                    3. Ek görseller (mockup, detay, kullanım)
                    4. SEO için alt text önerileri
                    5. Görsel sıralaması stratejisi
                    6. Mobil optimizasyon ipuçları
                    """
                    
                    result = call_openai(system_prompt, user_prompt)
                    if result:
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Lütfen önce ürün açıklaması girin.")
                
        # Image enhancement section
        st.markdown("---")
        st.markdown("### ✨ Görsel İyileştirme")
        
        uploaded_image = st.file_uploader(
            "Görseli yükleyin:",
            type=['png', 'jpg', 'jpeg'],
            key="enhance_image_upload"
        )
        
        if uploaded_image and st.button("🚀 Görseli İyileştir"):
            with st.spinner("Görsel iyileştiriliyor..."):
                enhanced_url = enhance_image(uploaded_image)
                if enhanced_url:
                    st.image(enhanced_url, caption="İyileştirilmiş Görsel")
                    st.markdown('<div class="success-box">✅ Görsel başarıyla iyileştirildi!</div>', unsafe_allow_html=True)
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
        
        if st.button("Generate Image Optimization Guide"):
            product_description = get_form_data("product_description")
            if product_description:
                with st.spinner("Generating image guide..."):
                    system_prompt = "You are an e-commerce visual expert specializing in Etsy product image optimization."
                    user_prompt = f"""
                    Product: {product_description}
                    Category: {get_form_data('product_category')}
                    
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
                    if result:
                        st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter a product description first.")


def render_step_5():
    """Render Step 5: Title Creation"""
    st.markdown('<div class="step-header">📝 Adım 5: Ürün Başlığı Yazma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📝 Step 5: Write Product Title</div>', unsafe_allow_html=True)
    
    product_description = get_form_data("product_description")
    target_audience = get_form_data("target_audience")
    design_theme = get_form_data("design_theme")
    
    if not product_description:
        st.warning("Lütfen önce sidebar'dan ürün bilgilerini doldurun." if st.session_state['language'] == 'tr' else "Please fill in product information in the sidebar first.")
        return
    
    num_titles = st.slider("Oluşturulacak başlık sayısı:" if st.session_state['language'] == 'tr' else "Number of titles to generate:", 1, 10, 5)
    
    if st.button("🚀 SEO Başlıkları Oluştur" if st.session_state['language'] == 'tr' else "🚀 Generate SEO Titles"):
        track_feature_usage('title_generation')
        with st.spinner("Başlıklar oluşturuluyor..." if st.session_state['language'] == 'tr' else "Generating titles..."):
            if st.session_state['language'] == 'tr':
                system_prompt = "Sen bir Etsy SEO uzmanısın. Yüksek dönüşüm oranına sahip başlıklar oluşturuyorsun."
                user_prompt = f"""
                Ürün: {product_description}
                Hedef Kitle: {target_audience}
                Tasarım Teması: {design_theme}
                
                {num_titles} adet SEO optimized Etsy başlığı oluştur:
                - Her başlık 130-140 karakter arası
                - Anahtar kelimeler, tema, hedef kitle, ürün tipi içersin
                - Yüksek arama hacimli kelimeler kullan
                - Her başlık için karakter sayısını belirt
                """
            else:
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


def render_step_6():
    """Render Step 6: Tag Creation"""
    st.markdown('<div class="step-header">🏷️ Adım 6: Etiket (Tag) Oluşturma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">🏷️ Step 6: Create Tags</div>', unsafe_allow_html=True)
    
    product_description = get_form_data("product_description")
    if not product_description:
        st.warning("Lütfen önce ürün açıklaması girin." if st.session_state['language'] == 'tr' else "Please enter product description first.")
        return
    
    if st.button("🏷️ 13 Etiket Oluştur" if st.session_state['language'] == 'tr' else "🏷️ Generate 13 Tags"):
        track_feature_usage('tag_generation')
        with st.spinner("Etiketler oluşturuluyor..." if st.session_state['language'] == 'tr' else "Generating tags..."):
            if st.session_state['language'] == 'tr':
                system_prompt = "Sen bir Etsy SEO uzmanısın. En etkili 13 etiketi seçiyorsun."
                user_prompt = f"""
                Ürün: {product_description}
                Kategori: {get_form_data('product_category')}
                Hedef Kitle: {get_form_data('target_audience')}
                
                Bu ürün için tam 13 adet Etsy etiketi oluştur:
                - Her etiket maksimum 20 karakter
                - Yüksek arama hacimli kelimeler kullan
                - Uzun kuyruk anahtar kelimeler ekle
                - Ürün tipi, stil, hedef kitle, malzeme, renk kategorilerinden seç
                - Her etiketin neden seçildiğini kısaca açıkla
                """
            else:
                system_prompt = "You are an Etsy SEO expert. Select the most effective 13 tags."
                user_prompt = f"""
                Product: {product_description}
                Category: {get_form_data('product_category')}
                Target Audience: {get_form_data('target_audience')}
                
                Create exactly 13 Etsy tags for this product:
                - Each tag maximum 20 characters
                - Use high search volume keywords
                - Include long-tail keywords
                - Choose from categories: product type, style, target audience, material, color
                - Briefly explain why each tag was selected
                """
            
            result = call_openai(system_prompt, user_prompt)
            if result:
                st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)


def render_step_7():
    """Render Step 7: Description Writing"""
    st.markdown('<div class="step-header">📄 Adım 7: Ürün Açıklaması Yazma</div>' if st.session_state['language'] == 'tr' else '<div class="step-header">📄 Step 7: Write Product Description</div>', unsafe_allow_html=True)
    
    product_description = get_form_data("product_description")
    if not product_description:
        st.warning("Lütfen önce ürün açıklaması girin." if st.session_state['language'] == 'tr' else "Please enter product description first.")
        return
    
    if st.button("📄 Detaylı Açıklama Oluştur" if st.session_state['language'] == 'tr' else "📄 Generate Detailed Description"):
        track_feature_usage('description_generation')
        with st.spinner("Açıklama yazılıyor..." if st.session_state['language'] == 'tr' else "Writing description..."):
            if st.session_state['language'] == 'tr':
                system_prompt = "Sen bir e-ticaret copywriting uzmanısın. Etsy için dönüşüm odaklı ürün açıklamaları yazıyorsun."
                user_prompt = f"""
                Ürün: {product_description}
                Kategori: {get_form_data('product_category')}
                Hedef Kitle: {get_form_data('target_audience')}
                Tasarım: {get_form_data('design_theme')}
                
                Bu ürün için kapsamlı Etsy açıklaması yaz:
                1. Dikkat çekici açılış cümlesi
                2. Ürün özellikleri ve faydaları
                3. Malzeme ve kalite bilgileri
                4. Boyut ve kullanım rehberi
                5. Hediye önerileri
                6. Kişiselleştirme seçenekleri (varsa)
                7. Kargo ve iade bilgileri
                8. Harekete geçirici sonuç cümlesi
                
                Açıklama 1000-1500 kelime arası olsun ve SEO dostu olsun.
                """
            else:
                system_prompt = "You are an e-commerce copywriting expert. Write conversion-focused product descriptions for Etsy."
                user_prompt = f"""
                Product: {product_description}
                Category: {get_form_data('product_category')}
                Target Audience: {get_form_data('target_audience')}
                Design: {get_form_data('design_theme')}
                
                Write a comprehensive Etsy description for this product:
                1. Attention-grabbing opening statement
                2. Product features and benefits
                3. Material and quality information
                4. Size and usage guide
                5. Gift suggestions
                6. Customization options (if applicable)
                7. Shipping and return information
                8. Call-to-action closing statement
                
                Description should be 1000-1500 words and SEO-friendly.
                """
            
            result = call_openai(system_prompt, user_prompt, max_tokens=1500)
            if result:
                st.markdown(f'<div class="ai-output">{result}</div>', unsafe_allow_html=True)


def render_remaining_steps(step_number):
    """Render placeholder for remaining steps"""
    step_titles = {
        8: "Varyasyon Ayarları" if st.session_state['language'] == 'tr' else "Variation Setup",
        9: "Fiyatlandırma Stratejisi" if st.session_state['language'] == 'tr' else "Pricing Strategy", 
        10: "İlan Kontrol Listesi" if st.session_state['language'] == 'tr' else "Listing Checklist",
        11: "SEO ve Tanıtım" if st.session_state['language'] == 'tr' else "SEO & Promotion",
        12: "Analitik ve Optimizasyon" if st.session_state['language'] == 'tr' else "Analytics & Optimization",
        13: "Sipariş Yönetimi" if st.session_state['language'] == 'tr' else "Order Management"
    }
    
    st.markdown(f'<div class="step-header">Adım {step_number}: {step_titles[step_number]}</div>', unsafe_allow_html=True)
    st.info(f"Adım {step_number} yakında eklenecek..." if st.session_state['language'] == 'tr' else f"Step {step_number} coming soon...")


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
    
    # Render each step
    with tabs[0]:  # Step 1
        render_step_1()
    
    with tabs[1]:  # Step 2
        render_step_2()
        
    with tabs[2]:  # Step 3
        render_step_3()
        
    with tabs[3]:  # Step 4
        render_step_4()
    
    with tabs[4]:  # Step 5  
        render_step_5()
        
    with tabs[5]:  # Step 6
        render_step_6()
        
    with tabs[6]:  # Step 7
        render_step_7()
    
    # Remaining steps (8-13)
    for i in range(7, 13):
        with tabs[i]:
            render_remaining_steps(i + 1)
    
    # Footer
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #666; padding: 20px;'>{t('footer')}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main() 
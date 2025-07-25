import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import io
import requests

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

# Language selection
if 'language' not in st.session_state:
    st.session_state['language'] = 'tr'  # Default to Turkish

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

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)

# AI Generation Functions
def call_openai(system_prompt, user_prompt, max_tokens=800):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        if "quota" in str(e).lower():
            raise Exception(t("api_quota_error"))
        else:
            raise Exception(f"{t('error')} {str(e)}")

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
    
    product_description = st.text_area(
        t("product_description"),
        placeholder=t("product_desc_placeholder"),
        height=120
    )
    
    product_category = st.text_input(
        t("product_category"),
        placeholder=t("product_cat_placeholder")
    )
    
    target_audience = st.text_input(
        t("target_audience"),
        placeholder=t("target_audience_placeholder")
    )
    
    design_theme = st.text_input(
        t("design_theme"),
        placeholder=t("design_theme_placeholder")
    )

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
"""
Language translations for Etsy AI Assistant
"""

TRANSLATIONS = {
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


def get_translation(key, language='tr'):
    """Get translation for a specific key and language"""
    return TRANSLATIONS.get(language, {}).get(key, key)


def get_all_translations(language='tr'):
    """Get all translations for a specific language"""
    return TRANSLATIONS.get(language, {}) 
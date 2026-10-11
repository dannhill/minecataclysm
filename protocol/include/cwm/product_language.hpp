#pragma once
#include <codecvt>
#include <locale>
#include <string>

namespace cwm {
// Product text only: no gameplay rules, item identities or wire structures.
// Set once during process startup; changing language requires a restart.
enum class ProductLanguage { English, Italian };
inline ProductLanguage& product_language_storage() {
    static ProductLanguage value = ProductLanguage::English;
    return value;
}
inline bool set_product_language(const std::string& code) {
    if (code != "en" && code != "it") return false;
    product_language_storage() = code == "it" ? ProductLanguage::Italian : ProductLanguage::English;
    return true;
}
inline const char* tr(const char* english, const char* italian = nullptr) {
    return product_language_storage() == ProductLanguage::Italian && italian && *italian ? italian : english;
}
inline std::string text(const char* english, const char* italian = nullptr) { return tr(english, italian); }
inline std::wstring wide(const char* english, const char* italian = nullptr) {
    return std::wstring_convert<std::codecvt_utf8<wchar_t>>{}.from_bytes(tr(english, italian));
}
} // namespace cwm

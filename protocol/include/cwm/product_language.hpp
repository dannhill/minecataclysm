#pragma once
#include "product_languages_generated.hpp"
#include <codecvt>
#include <locale>
#include <string>

namespace cwm {
// Main-thread presentation preference, acknowledged by the native runtime.
inline std::string &product_language_storage() {
    static std::string value = "en";
    return value;
}
inline bool set_product_language(const std::string &code) {
    if (!product_language(code)) return false;
    product_language_storage() = code;
    return true;
}
inline const char *tr(const char *english, const char *legacy_italian = nullptr) {
    const auto &code = product_language_storage();
    if (const auto *translated = catalog_translation(code, english)) return translated;
    // Existing Italian inline messages remain a migration fallback. New
    // languages and new catalog messages do not require another parameter.
    if (code == "it" && legacy_italian && *legacy_italian) return legacy_italian;
    return english;
}
inline std::string text(const char *english, const char *legacy_italian = nullptr) { return tr(english, legacy_italian); }
inline std::wstring wide(const char *english, const char *legacy_italian = nullptr) {
    return std::wstring_convert<std::codecvt_utf8<wchar_t>>{}.from_bytes(tr(english, legacy_italian));
}
} // namespace cwm

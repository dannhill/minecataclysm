#pragma once
#include "product_languages_generated.hpp"
#include <cstdint>
#include <stdexcept>
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
    // UTF-8 must produce UTF-16 on Windows and UTF-32 on Linux. No process
    // locale changes or deprecated codecvt facets are needed for UI text.
    const auto input = text(english, legacy_italian);
    std::wstring result;
    for (size_t i = 0; i < input.size();) {
        const auto first = static_cast<uint8_t>(input[i++]);
        uint32_t code = first; unsigned remaining = 0;
        if (first >= 0xc2 && first <= 0xdf) { code = first & 0x1f; remaining = 1; }
        else if (first >= 0xe0 && first <= 0xef) { code = first & 0x0f; remaining = 2; }
        else if (first >= 0xf0 && first <= 0xf4) { code = first & 7; remaining = 3; }
        else if (first >= 0x80) throw std::range_error("Invalid product-text UTF-8");
        const unsigned count = remaining;
        while (remaining--) {
            if (i == input.size()) throw std::range_error("Truncated product-text UTF-8");
            const auto next = static_cast<uint8_t>(input[i++]);
            if ((next & 0xc0) != 0x80) throw std::range_error("Invalid product-text UTF-8 continuation");
            code = (code << 6) | (next & 0x3f);
        }
        if ((count == 1 && code < 0x80) || (count == 2 && code < 0x800) ||
            (count == 3 && code < 0x10000) || code > 0x10ffff || (code >= 0xd800 && code <= 0xdfff))
            throw std::range_error("Invalid product-text Unicode scalar");
        if (sizeof(wchar_t) == 2 && code > 0xffff) {
            code -= 0x10000; result += static_cast<wchar_t>(0xd800 + (code >> 10));
            result += static_cast<wchar_t>(0xdc00 + (code & 0x3ff));
        } else result += static_cast<wchar_t>(code);
    }
    return result;
}
} // namespace cwm

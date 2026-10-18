#!/usr/bin/env python3
"""Exercise a third locale through generated C++/Lua/settings, without enabling it."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from generate_product_languages import load_registry, products


class RegistryTest(unittest.TestCase):
    def test_generated_files_match_source_registry(self):
        subprocess.run([sys.executable,str(ROOT/'tools/generate_product_languages.py'),'--check'],check=True)

    def test_new_locale_uses_same_runtime_path_and_falls_back_per_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            registry=root/'languages.json'
            entries=json.loads((ROOT/'localization/languages.json').read_text())
            entries.append(dict(code='fr-CA',name='Français canadien',native_locale='fr',engine_locale='fr',incomplete=True,catalog='fr.json'))
            registry.write_text(json.dumps(entries))
            (root/'en.json').write_text('{}');(root/'it.json').write_text('{}')
            (root/'fr.json').write_text(json.dumps({'Language':'Langue'}))
            generated=products(registry,root)
            for path, content in generated.items():
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
            header=root/'protocol/include/cwm/product_language.hpp'
            header.write_bytes((ROOT/'protocol/include/cwm/product_language.hpp').read_bytes())
            code=root/'check.cpp'
            code.write_text('''#include "cwm/product_language.hpp"
#include <cassert>
#include <iterator>
int main() {
 assert(std::size(cwm::product_languages())==3);
 assert(cwm::set_product_language("fr-CA"));
 assert(cwm::product_language_storage()=="fr-CA");
 assert(cwm::text("Language","Lingua")=="Langue");
 assert(cwm::text("Missing","Italian fallback")=="Missing");
 assert(std::string(cwm::product_language("fr-CA")->engine_locale)=="fr");
 assert(std::string(cwm::product_language("fr-CA")->native_locale)=="fr");
 assert(!cwm::set_product_language("unknown"));
 assert(cwm::product_language_storage()=="fr-CA");
 assert(cwm::set_product_language("en"));
 assert(cwm::text("Language")=="Language");
}''')
            subprocess.run(['c++','-std=c++17','-I'+str(root/'protocol/include'),str(code),'-o',str(root/'check')],check=True)
            subprocess.run([str(root/'check')],check=True)
            self.assertIn('fr-CA',generated[root/'luanti/builtin/settingtypes.txt'])
            self.assertIn('Français canadien (WIP)',generated[root/'luanti/builtin/mainmenu/settings/product_languages.lua'])

    def test_invalid_and_duplicate_codes_are_rejected(self):
        for code in ('../fr','fr\x00','fr,es','en','EN','x'):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'languages.json'
                entries=json.loads((ROOT/'localization/languages.json').read_text())
                entries.append(dict(entries[0],code=code))
                path.write_text(json.dumps(entries))
                with self.assertRaises(ValueError):load_registry(path)


if __name__=='__main__':unittest.main()

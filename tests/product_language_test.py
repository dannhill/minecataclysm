#!/usr/bin/env python3
"""Language precedence, menu persistence and actual launcher argument agreement.

Runs only in a reconstructed workspace; child executables are isolated stubs.
The separate renderer/native verification covers translated game text.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from product_language import configured_language, resolve, save


class ProductLanguageTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="cwm-language-test-")
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name)
        self.config = self.directory / "client.conf"
        self.preferences = self.directory / "user/config/presentation-language.conf"

    def test_system_language_and_legacy_setting_do_not_choose_product_language(self):
        self.config.write_text("language = it\n")
        self.assertEqual(resolve(self.config, self.preferences), "en")

    def test_precedence_and_last_assignment(self):
        self.config.write_text("# cwm_language = en\ncwm_language=it\ncwm_language = en\n")
        self.assertEqual(resolve(self.config, self.preferences), "en")
        self.preferences.parent.mkdir(parents=True)
        self.preferences.write_text("cwm_language = it\n")
        self.assertEqual(resolve(self.config, self.preferences), "it")
        self.assertEqual(resolve(self.config, self.preferences, "en"), "en")

    def test_invalid_stale_settings_fall_back_but_explicit_override_is_rejected(self):
        self.config.write_text("cwm_language = fr\n")
        self.assertEqual(resolve(self.config, self.preferences), "en")
        for value in ("", "fr", "IT", "it_IT"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                resolve(self.config, self.preferences, value)

    def test_unchanged_temporary_override_is_not_saved(self):
        self.config.write_text("cwm_language = it\n")
        self.assertFalse(save(self.config, self.preferences, "it"))
        self.assertFalse(self.preferences.exists())

    def test_menu_change_is_atomic_and_leaves_native_options_untouched(self):
        self.config.write_text("cwm_language = it\n")
        self.preferences.parent.mkdir(parents=True)
        native = self.preferences.parent / "options.json"
        native.write_text('[{"name":"USE_LANG","value":"fr"}]')
        original = native.read_bytes()
        self.assertTrue(save(self.config, self.preferences, "en"))
        self.assertEqual(configured_language(self.preferences), "it")
        self.assertEqual(native.read_bytes(), original)
        self.assertEqual(list(self.preferences.parent.glob(".presentation-language-*")), [])

    def launch(self, requested=None, menu_change=None):
        server = self.directory / "server"
        server.write_text("#!/usr/bin/env python3\n" + '''
import json, os, signal, socket, sys, time
from pathlib import Path
args = sys.argv[1:]
Path(os.environ['LANGUAGE_RECEIPT_SERVER']).write_text(json.dumps(dict(args=args, locale=os.environ.get('CDDA_LOCALE_DIR'))))
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(args[args.index('--socket')+1]); server.listen(1)
signal.signal(signal.SIGTERM, lambda *unused: sys.exit(0))
print('CWM IPC server listening on:', flush=True)
while True: time.sleep(.1)
''')
        client = self.directory / "client"
        client.write_text("#!/usr/bin/env python3\n" + '''
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
config = Path(args[args.index('--config')+1])
Path(os.environ['LANGUAGE_RECEIPT_CLIENT']).write_text(json.dumps(dict(args=args, config=config.read_text())))
if os.environ.get('LANGUAGE_MENU_CHANGE'):
    with config.open('a') as output: output.write('\\ncwm_language = '+os.environ['LANGUAGE_MENU_CHANGE']+'\\n')
''')
        for executable in (server, client):
            executable.chmod(0o755)
        env = dict(os.environ, CDDA_BIN=str(server), LUANTI_BIN=str(client),
                   CDDA_USERDIR=str(self.directory / "user"),
                   LUANTI_WORLD=str(self.directory / "world"), LUANTI_CONFIG=str(self.config),
                   LOG_DIR=str(self.directory / "logs"),
                   LANGUAGE_RECEIPT_SERVER=str(self.directory / "server.json"),
                   LANGUAGE_RECEIPT_CLIENT=str(self.directory / "client.json"))
        env.pop("CDDA_LANGUAGE", None)
        env.pop("LANGUAGE_MENU_CHANGE", None)
        if requested is not None:
            env["CDDA_LANGUAGE"] = requested
        if menu_change:
            env["LANGUAGE_MENU_CHANGE"] = menu_change
        return subprocess.run([str(ROOT / "start.sh")], env=env, text=True,
                              capture_output=True, timeout=10)

    def assert_agreement(self, language):
        server = json.loads((self.directory / "server.json").read_text())
        args = server["args"]
        self.assertEqual(args[args.index("--language")+1], language)
        self.assertEqual(server["locale"], str(ROOT / "cdda/lang/mo"))
        text = json.loads((self.directory / "client.json").read_text())["config"]
        self.assertTrue(text.endswith(f"cwm_language = {language}\nlanguage = {language}\n"))

    def test_normal_launcher_defaults_to_english_for_both_processes(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_agreement("en")
        self.assertFalse(self.preferences.exists())

    def test_launcher_italian_override_is_temporary(self):
        result = self.launch(requested="it")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_agreement("it")
        self.assertFalse(self.preferences.exists())

    def test_launcher_menu_change_survives_restart_in_both_processes(self):
        result = self.launch(menu_change="it")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(configured_language(self.preferences), "it")
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_agreement("it")
        result = self.launch(menu_change="en")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(configured_language(self.preferences), "en")

    def test_invalid_launcher_override_fails_before_world_creation(self):
        result = self.launch(requested="fr")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((self.directory / "user").exists())
        self.assertFalse((self.directory / "world").exists())
        self.assertFalse((self.directory / "server.json").exists())


if __name__ == "__main__":
    unittest.main()

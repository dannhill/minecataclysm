#!/usr/bin/env python3
"""Public demo launcher regression: real arguments and isolated session lifecycle."""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class DemoLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cwm-demo-launcher-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'tools').mkdir()
        self.script = self.root/'tools/launch_liquid_recovery_demo.py'
        shutil.copy2(ROOT/'tools/launch_liquid_recovery_demo.py', self.script)
        self.fixture = self.root/'artifacts/playtest-feedback-20261025/liquid-recovery'
        (self.fixture/'user/config').mkdir(parents=True)
        (self.fixture/'before.json').write_text('{}')
        self.native_options = self.fixture/'user/config/options.json'
        self.native_options.write_text('[{"name":"AUTOSAVE","value":"true"}]')

    def launch(self, *args, sessions=None):
        env = dict(os.environ)
        env.pop('CDDA_DEMO_SESSIONS', None)
        if sessions is not None:env['CDDA_DEMO_SESSIONS'] = str(sessions)
        with patch.dict(os.environ,env,clear=True), patch.object(sys,'argv',[str(self.script),*args]), \
             patch('os.execve') as execute, contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(self.script),run_name='__main__')
        return execute.call_args.args

    def test_public_alias_respects_actual_engine_limit(self):
        _, argv, env = self.launch('--fresh','--info')
        maximum = int(re.search(r'#define PLAYERNAME_SIZE (\d+)',(ROOT/'luanti/src/player.h').read_text()).group(1))-1
        name = argv[argv.index('--name')+1]
        self.assertLessEqual(len(name.encode()), maximum)
        self.assertIn('--info',argv)
        self.assertEqual(env['CDDA_CHARACTER'],'Audit Survivor')
        self.assertEqual(self.native_options.read_text(),'[{"name":"AUTOSAVE","value":"true"}]')

    def test_resume_and_fresh_are_distinct_private_sessions(self):
        _, _, first = self.launch('--fresh')
        _, _, resumed = self.launch()
        _, _, fresh = self.launch('--fresh')
        self.assertEqual(first['CDDA_USERDIR'],resumed['CDDA_USERDIR'])
        self.assertNotEqual(first['CDDA_USERDIR'],fresh['CDDA_USERDIR'])
        self.assertTrue(Path(first['CDDA_USERDIR']).is_dir())

    def test_private_verification_namespace_does_not_replace_user_pointer(self):
        normal = self.root/'artifacts/liquid-recovery-demo'
        normal.mkdir(parents=True)
        (normal/'last-session').write_text('human-session-sentinel')
        directory = self.root/'artifacts/verification-demo'
        _, _, env = self.launch('--fresh',sessions=directory)
        self.assertTrue(Path(env['CDDA_USERDIR']).is_relative_to(directory))
        self.assertEqual((normal/'last-session').read_text(),'human-session-sentinel')
        with self.assertRaises(RuntimeError):self.launch('--fresh',sessions=self.root/'outside-artifacts')

if __name__=='__main__':unittest.main()

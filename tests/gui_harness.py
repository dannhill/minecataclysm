#!/usr/bin/env python3
"""Shared GUI test harness for X11/Luanti + CWM relay integration tests."""
import csv
import json
import os
from pathlib import Path
import queue
import select
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time


def allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as temporary:
        temporary.bind(('127.0.0.1', 0))
        return temporary.getsockname()[1]


def recursive_items(value):
    if isinstance(value, dict):
        if 'typeid' in value:
            yield value
        for child in value.values():
            yield from recursive_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from recursive_items(child)


class GuiSessionHarness:
    """Manages an isolated Luanti + CDDA GUI test session with wire relay and X11 helpers."""

    def __init__(self, workspace: Path, artifacts: Path, fixture: Path | None = None,
                 copy_fixture: bool = True, query_disassemble: bool = True):
        self.ws = workspace.resolve()
        self.out = artifacts.resolve()
        sys.path.insert(0, str(self.ws / 'protocol/python'))
        from CDDA.CWM.CwmMessage import CwmMessage
        self._CwmMessage = CwmMessage

        self.out.mkdir(parents=True, exist_ok=True)
        self.user = self.out / 'user'
        if fixture is not None and copy_fixture:
            shutil.copytree(fixture.resolve(), self.user)
            opts = [
                {'name': 'SAFEMODE', 'value': 'false'},
                {'name': 'AUTOSAFEMODE', 'value': 'false'},
                {'name': 'AUTOSAVE', 'value': 'false'},
            ]
            if query_disassemble:
                opts.append({'name': 'QUERY_DISASSEMBLE', 'value': 'true'})
            (self.user / 'config/options.json').write_text(json.dumps(opts), encoding='utf-8')

        self.checks = {}
        self.injections = queue.Queue()
        self.old_window = subprocess.run(
            ['xdotool', 'getactivewindow'], capture_output=True, text=True
        ).stdout.strip()
        self.trace = self.out / 'camera.csv'
        self.port = allocate_port()
        self.config = self.out / 'client.conf'
        self.config.write_text(
            'screen_w = 1280\nscreen_h = 800\nfullscreen = false\nfps_max = 60\n'
            'vsync = false\nenable_clouds = false\ngui_scaling = 1\n'
            f'port = {self.port}\ncwm_trace_file = {self.trace}\n',
            encoding='utf-8',
        )
        self.env = dict(
            os.environ,
            CDDA_USERDIR=str(self.user),
            CDDA_WORLD='audit_fixture',
            LUANTI_WORLD=str(self.out / 'luanti'),
            LUANTI_CONFIG=str(self.config),
            LOG_DIR=str(self.out / 'logs'),
            CDDA_BIN=str(self.ws / 'cdda/build/src/cdda-server'),
            LUANTI_BIN=str(self.ws / 'luanti/bin/luanti'),
            CDDA_CONTINUOUS='1',
        )
        self.env.pop('CDDA_TERRAIN_DEMO', None)

        self.scratch = tempfile.TemporaryDirectory(prefix='cwm-gui-harness-')
        self.relay_path = Path(self.scratch.name) / 'relay.sock'
        self.native_path = self.out / 'native-socket'
        self.stop = threading.Event()
        self.drop = threading.Event()
        self.shutting_down = threading.Event()
        self.expected_shutdown_errors = []
        self.relay_errors = []
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.listener.bind(str(self.relay_path))
        self.listener.listen(1)
        self.listener.settimeout(0.1)
        self.relay_thread = threading.Thread(target=self._relay_loop, daemon=True)
        self.relay_thread.start()

        self.wrapper = self.out / 'client-relay.py'
        self.wrapper.write_text(
            "#!/usr/bin/env python3\nimport os,sys,re,json\nfrom pathlib import Path\n"
            f"args=sys.argv[1:]\nPath({str(self.out / 'luanti-argv.json')!r}).write_text(json.dumps(args))\n"
            "i=args.index('--config')+1\np=Path(args[i])\ns=p.read_text()\n"
            f"Path({str(self.native_path)!r}).write_text(re.findall(r'^cwm_socket_path = (.+)$',s,re.M)[-1])\n"
            f"p=Path({str(self.out / 'relay-client.conf')!r})\n"
            f"p.write_text(s+{repr(chr(10) + 'cwm_trace_file = ' + str(self.trace) + chr(10))}+'\\ncwm_socket_path = {self.relay_path}\\n')\n"
            "args[i]=str(p)\n"
            f"os.execv({str(self.ws / 'luanti/bin/luanti')!r},[{str(self.ws / 'luanti/bin/luanti')!r},*args])\n",
            encoding='utf-8',
        )
        self.wrapper.chmod(0o755)
        self.env['LUANTI_BIN'] = str(self.wrapper)
        self.proc = None
        self.window = None

    def _relay_loop(self):
        CwmMessage = self._CwmMessage
        try:
            while not self.stop.is_set():
                try:
                    client_socket, _ = self.listener.accept()
                except socket.timeout:
                    continue
                with client_socket, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_socket:
                    server_socket.connect(self.native_path.read_text(encoding='utf-8').strip())
                    native_sequence = 0
                    client_buffer = bytearray()

                    def forward_client(packet):
                        nonlocal native_sequence
                        body = bytearray(packet[4:])
                        message = CwmMessage.GetRootAs(body)
                        native_sequence += 1
                        offset = message._tab.Offset(4)
                        if not offset:
                            raise AssertionError('Client sequence must be explicit')
                        struct.pack_into('<Q', body, message._tab.Pos + offset, native_sequence)
                        frame = struct.pack('>I', len(body)) + body
                        with (self.out / 'client-wire.bin').open('ab') as capture:
                            capture.write(frame)
                        server_socket.sendall(frame)

                    while not self.stop.is_set():
                        if self.drop.is_set():
                            self.drop.clear()
                            break
                        while not self.injections.empty():
                            forward_client(self.injections.get_nowait())
                        readable, _, _ = select.select([client_socket, server_socket], [], [], 0.03)
                        closed = False
                        for source in readable:
                            data = source.recv(1 << 20)
                            if not data:
                                closed = True
                                break
                            if source is client_socket:
                                client_buffer.extend(data)
                                while len(client_buffer) >= 4:
                                    size = struct.unpack('>I', client_buffer[:4])[0]
                                    if len(client_buffer) < size + 4:
                                        break
                                    forward_client(bytes(client_buffer[:size + 4]))
                                    del client_buffer[:size + 4]
                            else:
                                with (self.out / 'server-wire.bin').open('ab') as capture:
                                    capture.write(data)
                                client_socket.sendall(data)
                        if closed:
                            break
        except (ConnectionResetError, BrokenPipeError) as error:
            if self.shutting_down.is_set():
                self.expected_shutdown_errors.append(str(error))
            else:
                self.relay_errors.append(str(error))
        except Exception as error:
            self.relay_errors.append(str(error))

    def check(self, name: str, ok: bool):
        self.checks[name] = bool(ok)
        (self.out / 'checks.json').write_text(json.dumps(self.checks, indent=2) + '\n', encoding='utf-8')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    def rows(self):
        if not self.trace.exists():
            return []
        with self.trace.open(encoding='utf-8') as stream:
            return [r for r in csv.DictReader(stream) if r.get('scene_origin_y') is not None]

    def latest(self):
        return self.rows()[-1]

    def wait(self, predicate, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and (self.proc is None or self.proc.poll() is None):
            data = self.rows()
            if data and predicate(data[-1]):
                return data[-1]
            time.sleep(0.05)
        raise RuntimeError('GUI condition not reached; inspect trace/logs')

    def xdo(self, *argv):
        if os.environ.get('CWM_GUI_NO_WM') == '1' and argv and argv[0] == 'windowactivate':
            argv = ('windowfocus', *argv[1:])
        subprocess.run(['xdotool', *argv], check=True, capture_output=True, timeout=5)

    def tap(self, key: str, sneak: bool = False):
        if sneak:
            self.xdo('keydown', 'Shift_L')
            time.sleep(0.12)
        self.xdo('keydown', '--window', self.window, key)
        time.sleep(0.12)
        self.xdo('keyup', '--window', self.window, key)
        if sneak:
            time.sleep(0.12)
            self.xdo('keyup', 'Shift_L')
        time.sleep(0.3)

    def shot(self, name: str):
        time.sleep(0.6)
        subprocess.run(['import', '-window', self.window, str(self.out / name)], check=True, timeout=10)

    def discover_window(self, timeout: float = 85.0, min_rows: int = 20) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and self.proc.poll() is None:
            descendants = [self.proc.pid]
            for pid in descendants:
                try:
                    descendants.extend(map(int, Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                    if Path(f'/proc/{pid}/comm').read_text().strip() != 'luanti':
                        continue
                except (FileNotFoundError, ProcessLookupError):
                    continue
                found = subprocess.run(
                    ['xdotool', 'search', '--onlyvisible', '--pid', str(pid)],
                    capture_output=True, text=True
                )
                if found.stdout.strip():
                    self.window = found.stdout.splitlines()[0]
            if self.window and len(self.rows()) > min_rows:
                break
            time.sleep(0.2)
        return bool(self.window) and len(self.rows()) > min_rows

    def messages(self, kind: int, direction: str = 'server'):
        wire_file = self.out / f'{direction}-wire.bin'
        if not wire_file.exists():
            return []
        buf = wire_file.read_bytes()
        offset = 0
        found = []
        while offset + 4 <= len(buf):
            n = struct.unpack('>I', buf[offset:offset + 4])[0]
            offset += 4
            if offset + n > len(buf):
                break
            msg = self._CwmMessage.GetRootAs(buf[offset:offset + n])
            offset += n
            if msg.PayloadType() == kind:
                found.append(msg)
        return found

    def close(self):
        self.shutting_down.set()
        if self.proc is not None and self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=45)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait()
        self.stop.set()
        self.relay_thread.join(timeout=3)
        self.listener.close()
        self.scratch.cleanup()
        (self.out / 'relay-errors.json').write_text(json.dumps(self.relay_errors), encoding='utf-8')
        if self.old_window:
            subprocess.run(['xdotool', 'windowactivate', self.old_window], capture_output=True)

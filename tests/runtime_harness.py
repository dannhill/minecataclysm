#!/usr/bin/env python3
"""Shared headless CWM runtime protocol harness for Python integration tests."""
import json
from pathlib import Path
import select
import socket
import struct
import subprocess
import sys
import time


class CheckRecorder:
    def __init__(self, artifacts_dir: Path):
        self.out = artifacts_dir.resolve()
        self.checks = {}

    def __call__(self, name: str, ok: bool):
        self.checks[name] = bool(ok)
        (self.out / 'checks.json').write_text(json.dumps(self.checks, indent=2) + '\n', encoding='utf-8')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)


def parse_payload(msg, module):
    cls = getattr(module, module.__name__.split('.')[-1])
    value = cls()
    value.Init(msg.Payload().Bytes, msg.Payload().Pos)
    return value


def run_pristine_reader(reader: Path, user_dir: Path, data_dir: Path, output_path: Path,
                        log_path: Path, extra_args=(), timeout: int = 180) -> tuple[int, dict | None]:
    command = [
        str(reader.resolve()),
        '--userdir', str(user_dir),
        '--datadir', str(data_dir),
        '--output', str(output_path),
        *extra_args,
    ]
    with log_path.open('w', encoding='utf-8') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode != 0 or not output_path.is_file():
        return result.returncode, None
    return result.returncode, json.loads(output_path.read_text(encoding='utf-8'))


class RuntimeConnection:
    """Headless CWM protocol client over a Unix domain socket."""

    def __init__(self, workspace: Path, socket_path: Path, client_nonce: int = 91,
                 history_list: list | None = None, history_path: Path | None = None):
        sys.path.insert(0, str(workspace.resolve() / 'protocol/python'))
        import flatbuffers
        from session_wire import NativeWire
        from CDDA.CWM import (
            CwmMessage, Payload, HelloRequest, HelloResponse,
            WorldSnapshot, CommandAck, DecisionPrompt
        )
        self._flatbuffers = flatbuffers
        self._CwmMessage = CwmMessage
        self._Payload = Payload
        self._HelloRequest = HelloRequest
        self._HelloResponse = HelloResponse
        self._WorldSnapshot = WorldSnapshot
        self._CommandAck = CommandAck
        self._DecisionPrompt = DecisionPrompt

        self.wire = NativeWire(client_nonce)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(str(socket_path))
        self.buffer = b''
        self.state = None
        self.acks = {}
        self.completed = set()
        self.prompts = []
        self.auto_ack = True
        self.full_state_id = 0
        self.next_id = 1
        self._history = history_list
        self._history_path = history_path

        b = flatbuffers.Builder(64)
        HelloRequest.HelloRequestStart(b)
        self.wire.hello_fields(b)
        self.wire.send(self.sock, b, Payload.Payload.HelloRequest, HelloRequest.HelloRequestEnd(b))
        self.until(lambda: self.state is not None and not (self.state['pause'] & 8))

    def pump(self, wait: float = 0.05):
        if select.select([self.sock], [], [], max(0.0, wait))[0]:
            data = self.sock.recv(1 << 20)
            if not data:
                raise EOFError('Native connection closed')
            self.buffer += data
        while len(self.buffer) >= 4:
            size = struct.unpack('>I', self.buffer[:4])[0]
            if not (0 < size <= 16 * 1024 * 1024):
                raise ValueError('Invalid frame size')
            if len(self.buffer) < size + 4:
                break
            msg = self._CwmMessage.CwmMessage.GetRootAsCwmMessage(self.buffer[4:size + 4])
            self.buffer = self.buffer[size + 4:]
            if self.auto_ack or msg.PayloadType() != self._Payload.Payload.WorldSnapshot:
                self.wire.observe(self.sock, msg)
            ptype = msg.PayloadType()
            if ptype == self._Payload.Payload.HelloResponse:
                self.next_id = parse_payload(msg, self._HelloResponse).NextCommandId()
            elif ptype == self._Payload.Payload.CommandAck:
                a = parse_payload(msg, self._CommandAck)
                self.acks[a.CommandId()] = (a.Accepted(), (a.ErrorMessage() or b'').decode())
            elif ptype == self._Payload.Payload.WorldSnapshot:
                w = parse_payload(msg, self._WorldSnapshot)
                self.wire.revision = w.WorldRevision()
                if w.Full():
                    self.full_state_id = w.StateId()
                origin = w.Origin()
                actors = {}
                for i in range(w.EntitiesLength()):
                    a = w.Entities(i)
                    actors[a.Id()] = dict(
                        id=a.Id(),
                        name=(a.Name() or b'').decode(),
                        kind=a.Type(),
                        pos=[origin.X() + a.Pos().X(), origin.Y() + a.Pos().Y(), a.Pos().Z()],
                        motion=a.MotionSeconds(),
                        perceived=a.Perceived(),
                    )
                clock = w.Clock()
                self.state = dict(
                    time=w.SimulationTimeSeconds(),
                    revision=w.WorldRevision(),
                    pause=clock.PauseReasons() if clock else 0,
                    scale=clock.TimeScale() if clock else 1,
                    realtime=clock.Realtime() if clock else False,
                    actors=actors,
                    origin=[origin.X(), origin.Y(), origin.Z()],
                    completed=w.CompletedCommandId(),
                )
                self.completed.add(w.CompletedCommandId())
                if self._history is not None:
                    self._history.append(dict(wall=time.monotonic(), **self.state))
                    if self._history_path is not None:
                        self._history_path.write_text(
                            json.dumps(self._history, indent=2) + '\n', encoding='utf-8'
                        )
            elif ptype == self._Payload.Payload.DecisionPrompt:
                prompt = parse_payload(msg, self._DecisionPrompt)
                self.prompts.append(dict(
                    id=prompt.DecisionId(),
                    text=prompt.Text().decode(),
                    choices=[prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())],
                ))

    def until(self, predicate, timeout: float = 15.0):
        deadline = time.monotonic() + timeout
        while not predicate():
            if time.monotonic() > deadline:
                raise TimeoutError('Native state condition timed out')
            self.pump(0.05)
        return self.state

    def observe(self, duration: float):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            self.pump(min(0.05, deadline - time.monotonic()))
        return self.state

    def close(self):
        self.sock.close()

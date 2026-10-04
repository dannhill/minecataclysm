"""Shared CWM 2 fixture envelope. Production never uses this test helper."""
import struct
import threading
from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest as Hello, HelloResponse, WorldSnapshot as World, SnapshotAck, WorldReset

class NativeWire:
    def __init__(self, client_id=31):
        self.client_id = client_id
        self.sequence = self.revision = 0
        self.identity = (0,0,0)
        self.lock = threading.RLock()
    def hello_fields(self, b):
        Hello.HelloRequestAddProtocolVersionMajor(b,2)
        Hello.HelloRequestAddProtocolVersionMinor(b,2)
        Hello.HelloRequestAddClientId(b,self.client_id)
    def finish(self, b, kind, value):
        if kind == Payload.Payload.HelloRequest:
            self.sequence = self.revision = 0; self.identity = (0,0,0)
        self.sequence += 1
        return envelope(b,kind,value,self.sequence,self.revision,self.identity)
    def send(self, c, b, kind, value):
        with self.lock:
            body=self.finish(b,kind,value)
            c.sendall(struct.pack('>I',len(body))+body)
    def observe(self, c, msg):
        with self.lock:
            if msg.PayloadType() == Payload.Payload.HelloResponse:
                hello=HelloResponse.HelloResponse(); hello.Init(msg.Payload().Bytes,msg.Payload().Pos)
                if not hello.Accepted(): raise ValueError('Session rejected')
                self.identity=(msg.SessionId(),msg.PlayerId(),msg.ConnectionId())
            if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                world=World.WorldSnapshot(); world.Init(msg.Payload().Bytes,msg.Payload().Pos)
                self.revision=world.WorldRevision()
                if world.Full():
                    import flatbuffers
                    b=flatbuffers.Builder(64)
                    SnapshotAck.SnapshotAckStart(b); SnapshotAck.SnapshotAckAddStateId(b,world.StateId())
                    self.send(c,b,Payload.Payload.SnapshotAck,SnapshotAck.SnapshotAckEnd(b))
        return msg

def envelope(b,kind,value,sequence,revision,identity):
    Msg.CwmMessageStart(b); Msg.CwmMessageAddSequenceNumber(b,sequence)
    Msg.CwmMessageAddWorldRevision(b,revision); Msg.CwmMessageAddPayloadType(b,kind)
    Msg.CwmMessageAddPayload(b,value)
    Msg.CwmMessageAddSessionId(b,identity[0]); Msg.CwmMessageAddPlayerId(b,identity[1]); Msg.CwmMessageAddConnectionId(b,identity[2])
    b.Finish(Msg.CwmMessageEnd(b)); return bytes(b.Output())

class AuthorityWire:
    def __init__(self, connection=1, session=88):
        self.identity=(session,1,connection)
        self.sequence=self.revision=self.resync=0
    def finish(self,b,kind,value):
        self.sequence+=1
        return envelope(b,kind,value,self.sequence,self.revision,self.identity)
    def hello_fields(self,b):
        HelloResponse.HelloResponseAddProtocolVersionMajor(b,2)
        HelloResponse.HelloResponseAddProtocolVersionMinor(b,2)
        HelloResponse.HelloResponseAddNextCommandId(b,1)
    def reset(self,request=0):
        import flatbuffers
        self.resync=request
        b=flatbuffers.Builder(64); WorldReset.WorldResetStart(b); WorldReset.WorldResetAddRequestId(b,request)
        return self.finish(b,Payload.Payload.WorldReset,WorldReset.WorldResetEnd(b))
    def empty_vectors(self,b):
        b.StartVector(4,0,4); return b.EndVector()
    def world_fields(self,b,full,empty,completed=0,revision=None):
        base=self.revision; self.revision=self.revision+1 if revision is None else revision
        World.WorldSnapshotAddWorldRevision(b,self.revision)
        World.WorldSnapshotAddBaseRevision(b,base)
        World.WorldSnapshotAddStateId(b,self.sequence+1)
        World.WorldSnapshotAddFull(b,full)
        World.WorldSnapshotAddResyncId(b,self.resync)
        World.WorldSnapshotAddCompletedCommandId(b,completed)
        World.WorldSnapshotAddFields(b,empty); World.WorldSnapshotAddVehicles(b,empty)

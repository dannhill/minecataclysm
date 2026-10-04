#include "cwm/cwm_session.hpp"
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
// No socket, descriptor, POSIX header or engine dependency in the test backend.
struct MemoryChannel : CwmTransport {
    bool valid{true}; IpcCloseReason reason{IpcCloseReason::None}; IpcWork work;
    std::vector<std::vector<uint8_t>> sent;
    bool is_valid() const override { return valid; }
    bool send_message(const uint8_t* p, size_t n) override { if (!valid) return false; sent.emplace_back(p,p+n); return true; }
    bool poll_and_receive(std::vector<std::vector<uint8_t>>&, int) override { return valid; }
    void close(IpcCloseReason r) override { valid=false; reason=r; }
    IpcCloseReason close_reason() const override { return reason; }
    size_t pending_input_bytes() const override { return 0; }
    size_t queued_output_bytes() const override { return 0; }
    size_t queued_output_frames() const override { return 0; }
    const IpcWork& last_work() const override { return work; }
};
std::vector<uint8_t> reset(uint64_t seq, uint64_t request=0, Identity ids={11,22,33}) {
    MessageBuilder b(seq,5,ids);
    return b.finish_message(Payload::WorldReset, CreateWorldReset(b.builder(),request).Union());
}
std::vector<uint8_t> world(uint64_t seq, bool full=true, uint64_t base=0,
    uint64_t revision=5, uint64_t resync=0, bool malformed=false, Identity ids={11,22,33}, float scale=1.f, uint32_t reasons=0, float motion=.2f, bool realtime=true, bool continuous=false) {
    MessageBuilder b(seq,revision,ids); auto& f=b.builder();
    Vec3f pos(2,3,0); Coord3i origin(0,0,0);
    auto actor=CreateEntityState(f,1,EntityType::PLAYER,0,&pos,0,0,0,0,true,0,motion);
    auto actors=f.CreateVector(std::vector{actor});
    std::vector<CwmBlock> blocks(malformed ? 2 : 256,CwmBlock(0,1,15,0));
    auto chunk=CreateChunkSnapshot(f,0,0,0,16,16,1,f.CreateVectorOfStructs(blocks));
    auto chunks=f.CreateVector(std::vector{chunk});
    auto vehicles=f.CreateVector(std::vector<flatbuffers::Offset<VehicleState>>{});
    auto fields=f.CreateVector(std::vector<flatbuffers::Offset<FieldState>>{});
    auto clock=CreateSimulationState(f,realtime,reasons,scale,continuous);
    auto body=CreateWorldSnapshot(f,revision,&origin,0,full?chunks:0,actors,vehicles,fields,0,false,
        full,base,seq,resync,0,0,0,clock);
    return b.finish_message(Payload::WorldSnapshot,body.Union());
}
bool accept(ClientSession& s, MemoryChannel& c, const std::vector<uint8_t>& bytes) {
    CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
    return s.accept(*GetCwmMessage(bytes.data()),c);
}
std::vector<uint8_t> roster(uint64_t seq, EntityType kind=EntityType::MONSTER,
    bool duplicate_spawn=false, bool contradictory_spawn=false, bool duplicate_remove=false) {
    MessageBuilder b(seq,seq+2,{11,22,33}); auto& f=b.builder();
    Vec3f pos(2,3,0), other(5,3,0); Coord3i origin(0,0,0);
    auto player=CreateEntityState(f,1,EntityType::PLAYER,0,&pos);
    auto actor=CreateEntityState(f,2,kind,0,&pos);
    auto actors=f.CreateVector(std::vector{player,actor});
    auto announced=contradictory_spawn?CreateEntityState(f,2,kind,0,&other):actor;
    auto spawn=CreateEntitySpawned(f,announced);
    auto spawned=f.CreateVector(duplicate_spawn?std::vector{spawn,spawn}:std::vector{spawn});
    auto removal=CreateEntityRemoved(f,9);
    auto removed=f.CreateVector(duplicate_remove?std::vector{removal,removal}:std::vector<flatbuffers::Offset<EntityRemoved>>{});
    auto vehicles=f.CreateVector(std::vector<flatbuffers::Offset<VehicleState>>{});
    auto fields=f.CreateVector(std::vector<flatbuffers::Offset<FieldState>>{});
    auto body=CreateWorldSnapshot(f,seq+2,&origin,0,0,actors,vehicles,fields,0,false,false,
        seq+1,seq,0,0,spawned,removed);
    return b.finish_message(Payload::WorldSnapshot,body.Union());
}
void handshake(ClientSession& s, MemoryChannel& c) {
    CHECK(s.begin(c)); CHECK(!s.ready());
    MessageBuilder b(1,5,{11,22,33}); CHECK(accept(s,c,b.build_hello_response(true,"test","",8)));
    CHECK(s.next_command==8); CHECK(accept(s,c,reset(2)));
    auto bytes=world(3); CHECK(accept(s,c,bytes)); CHECK(!s.ready());
    CHECK(s.commit(*GetCwmMessage(bytes.data())->payload_as_WorldSnapshot(),c)); CHECK(s.ready());
}
int main() {
    int failed=0;
    auto test=[&](const char* name, const std::function<void()>& action) {
        try { action(); std::cout<<"PASS "<<name<<'\n'; }
        catch(const std::exception& e) { ++failed; std::cout<<"FAIL "<<name<<": "<<e.what()<<'\n'; }
    };
    test("memory_backend_full_state_required_before_input",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(c.sent.size()==2); CHECK(GetCwmMessage(c.sent.back().data())->payload_type()==Payload::SnapshotAck);});
    test("sequence_gap_freezes_and_requests_once",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(5,false,5,6))); CHECK(!s.ready()); CHECK(s.resync_count==1); CHECK(!accept(s,c,world(6,false,6,7))); CHECK(s.resync_count==1); CHECK(c.sent.size()==3);});
    test("matching_reset_is_a_sequence_barrier",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(5,false,5,6))); CHECK(!accept(s,c,reset(9,2))); CHECK(accept(s,c,reset(10,1))); auto b=world(11,true,0,8,1); CHECK(accept(s,c,b)); CHECK(s.commit(*GetCwmMessage(b.data())->payload_as_WorldSnapshot(),c)); CHECK(s.ready() && s.revision==8);});
    test("reordered_frame_requires_resync",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(3,false,5,6))); CHECK(!s.ready());});
    test("wrong_delta_base_requires_resync",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(4,false,4,6))); CHECK(!s.ready() && s.revision==5);});
    test("malformed_full_never_commits_revision",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(4,true,5,6,0,true))); CHECK(s.revision==5 && !s.ready());});
    test("wrong_identity_disconnects",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,world(4,false,5,6,0,false,{11,22,34}))); CHECK(!c.valid);});
    test("rejected_hello_never_ready",[]{ClientSession s; MemoryChannel c; CHECK(s.begin(c)); MessageBuilder b(1,0,{11,22,33}); CHECK(!accept(s,c,b.build_hello_response(false,"test"))); CHECK(s.state==SessionState::Rejected && !c.valid);});
    test("fresh_server_discards_previous_world",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(s.begin(c)); MessageBuilder b(1,1,{12,22,1}); CHECK(accept(s,c,b.build_hello_response(true,"test"))); CHECK(s.clear_world && s.revision==0);});
    test("same_session_reconnect_retains_revision",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(s.begin(c)); MessageBuilder b(1,5,{11,22,34}); CHECK(accept(s,c,b.build_hello_response(true,"test","",2))); CHECK(!s.clear_world && s.revision==5 && s.next_command==8);});
    test("duplicate_spawn_metadata_requires_resync",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,roster(4,EntityType::MONSTER,true))); CHECK(!s.ready() && s.revision==5);});
    test("contradictory_spawn_position_requires_resync",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,roster(4,EntityType::MONSTER,false,true))); CHECK(!s.ready() && s.revision==5);});
    test("duplicate_remove_metadata_requires_resync",[]{ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,roster(4,EntityType::MONSTER,false,false,true))); CHECK(!s.ready() && s.revision==5);});
    test("second_player_or_unknown_kind_requires_resync",[]{for(auto kind:{EntityType::PLAYER,static_cast<EntityType>(99)}) {ClientSession s; MemoryChannel c; handshake(s,c); CHECK(!accept(s,c,roster(4,kind))); CHECK(!s.ready());}});
    test("existing_actor_cannot_switch_between_npc_and_monster",[]{ClientSession s; MemoryChannel c; handshake(s,c); auto bytes=roster(4); CHECK(accept(s,c,bytes)); CHECK(s.commit(*GetCwmMessage(bytes.data())->payload_as_WorldSnapshot(),c)); CHECK(!accept(s,c,roster(5,EntityType::NPC))); CHECK(s.revision==6 && !s.ready());});
    test("invalid_clock_or_motion_requires_resync",[]{
        for (float scale : {0.f,5.f,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()}) {
            ClientSession s; MemoryChannel c; handshake(s,c);
            CHECK(!accept(s,c,world(4,false,5,6,0,false,{11,22,33},scale))); CHECK(s.revision==5 && !s.ready());
        }
        for (float motion : {0.f,-1.f,61.f,std::numeric_limits<float>::quiet_NaN()}) {
            ClientSession s; MemoryChannel c; handshake(s,c);
            CHECK(!accept(s,c,world(4,false,5,6,0,false,{11,22,33},1,0,motion))); CHECK(!s.ready());
        }
        ClientSession s; MemoryChannel c; handshake(s,c);
        CHECK(!accept(s,c,world(4,false,5,6,0,false,{11,22,33},1,32))); CHECK(!s.ready());
    });
    test("continuous_clock_requires_realtime_authority",[]{
        ClientSession s; MemoryChannel c; handshake(s,c);
        CHECK(!accept(s,c,world(4,false,5,6,0,false,{11,22,33},4,0,.04f,false,true)));
        CHECK(!s.ready() && s.revision==5);
    });
    test("continuous_clock_and_fractional_position_commit",[]{
        ClientSession s; MemoryChannel c; handshake(s,c);
        auto bytes=world(4,false,5,6,0,false,{11,22,33},4,0,.04f,true,true);
        auto* snapshot=static_cast<WorldSnapshot*>(GetMutableCwmMessage(bytes.data())->mutable_payload());
        snapshot->mutable_entities()->GetMutableObject(0)->mutable_pos()->mutate_x(2.375f);
        CHECK(accept(s,c,bytes));
        CHECK(s.commit(*GetCwmMessage(bytes.data())->payload_as_WorldSnapshot(),c));
        CHECK(s.ready() && s.revision==6);
    });
    test("deduplicate_pending_and_complete",[]{CommandLedger l; CHECK(l.begin(7,1,"move")==CommandLedger::Status::Fresh); CHECK(l.begin(7,1,"move")==CommandLedger::Status::Pending); l.complete({1,true,"",20}); CHECK(l.begin(7,1,"move")==CommandLedger::Status::Complete); l.complete({1,false,"late",30}); CHECK(l.find(1)->outcome.accepted && l.find(1)->outcome.revision==20);});
    test("conflicting_semantics_or_author_rejected",[]{CommandLedger l; l.begin(7,1,"move"); CHECK(l.begin(7,1,"interact")==CommandLedger::Status::Conflict); CHECK(l.begin(8,1,"move")==CommandLedger::Status::Conflict);});
    test("bounded_cache_expiry_never_reexecutes",[]{CommandLedger l(2); for(uint64_t i=1;i<=100;i++){ CHECK(l.begin(7,i,"wait")==CommandLedger::Status::Fresh); l.complete({i,true,"",i}); CHECK(l.size()<=2); } CHECK(l.begin(7,1,"wait")==CommandLedger::Status::Expired); CHECK(l.next_id()==101);});
    test("pending_entries_cannot_be_evicted",[]{CommandLedger l(1); l.begin(7,1,"wait"); CHECK(l.begin(7,2,"wait")==CommandLedger::Status::Expired); CHECK(l.find(1) && l.size()==1);});
    test("invalid_ids_do_not_consume_ledger",[]{CommandLedger l; CHECK(l.begin(0,1,"x")==CommandLedger::Status::Invalid); CHECK(l.begin(1,0,"x")==CommandLedger::Status::Invalid); CHECK(l.next_id()==1);});
    return failed?1:0;
}

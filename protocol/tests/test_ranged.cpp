#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
#include <limits>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> snapshot(int defect) {
    MessageBuilder wire(1,7,{11,22,33}); auto& f=wire.builder();f.ForceDefaults(true);
    auto gun=CreateRangedWeaponStateDirect(f,defect==1?0:12,defect==2?"":"pistol",
        defect==3?-1:3,defect==4?-1:14,defect==5?std::numeric_limits<double>::quiet_NaN():defect==6?-1:6000,"",true);
    auto reload=CreateReloadState(f,defect==7?0:13,defect==8?0:1000,defect==9?-1:defect==10?1001:800);
    auto meal=defect==11?CreateConsumptionState(f,14,1000,800):flatbuffers::Offset<ConsumptionState>{};
    Coord3i origin(0,0,0);
    Vec3f pos(0,0,0);
    auto player=CreateEntityState(f,1,EntityType::PLAYER,0,&pos);
    auto entities=f.CreateVector(std::vector<flatbuffers::Offset<EntityState>>{player});
    auto vehicles=f.CreateVector(std::vector<flatbuffers::Offset<VehicleState>>{});
    auto fields=f.CreateVector(std::vector<flatbuffers::Offset<FieldState>>{});
    WorldSnapshotBuilder world(f);
    world.add_world_revision(2);world.add_origin(&origin);world.add_state_id(1);
    world.add_entities(entities);world.add_vehicles(vehicles);world.add_fields(fields);
    world.add_ranged_weapon(gun);world.add_reload(reload);world.add_consumption(meal);
    return wire.finish_message(Payload::WorldSnapshot,world.Finish().Union());
}
int main() {
    static_assert(int(Payload::CancelCraftingRequest)==36); // Never renumber an existing union arm.
    for (int defect=0;defect<=11;++defect) {
        auto bytes=snapshot(defect);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(defect==0));
    }
    auto bytes=snapshot(0);
    auto* world=static_cast<WorldSnapshot*>(GetMutableCwmMessage(bytes.data())->mutable_payload());
    world->mutable_ranged_weapon()->mutable_name()->Mutate(0,'\0');CHECK(!valid_world(world));
    MessageBuilder wire(2,7,{11,22,33});
    for (auto kind : {RangedAction::AIM,RangedAction::FIRE,RangedAction::RELOAD}) {
        auto request=wire.build_ranged_request(19,12,kind==RangedAction::RELOAD?0:99,kind);
        const auto* r=GetCwmMessage(request.data())->payload_as_RangedRequest();
        CHECK(r && r->command_id()==19 && r->weapon_token()==12 && r->action()==kind);
        CHECK(r->target_entity_id()==(kind==RangedAction::RELOAD?0:99));
    }
    auto cancel=wire.build_cancel_reload(20,13);
    const auto* c=GetCwmMessage(cancel.data())->payload_as_CancelReloadRequest();
    CHECK(c && c->command_id()==20 && c->activity_token()==13);
    std::cout<<"Ranged/reload snapshot limits, exclusive activities, stable wire IDs and requests PASS\n";
}

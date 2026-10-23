#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
std::vector<uint8_t> world(int bad) {
    MessageBuilder wire(1,1,{11,22,33});auto& f=wire.builder();
    const auto liquid=CreateLiquidTransferState(f,bad==1?0:42);
    const auto other=bad==2?CreateCraftingState(f,43,0):flatbuffers::Offset<CraftingState>{};
    Vec3f pos(0,0,0);Coord3i origin(0,0,0);
    std::vector<flatbuffers::Offset<EntityState>> actors{CreateEntityState(f,1,EntityType::PLAYER,0,&pos)};
    std::vector<flatbuffers::Offset<VehicleState>> vehicles;std::vector<flatbuffers::Offset<FieldState>> fields;
    const auto a=f.CreateVector(actors),v=f.CreateVector(vehicles),s=f.CreateVector(fields);
    WorldSnapshotBuilder b(f);b.add_state_id(1);b.add_origin(&origin);b.add_entities(a);b.add_vehicles(v);b.add_fields(s);
    b.add_liquid_transfer(liquid);b.add_crafting(other);return wire.finish_message(Payload::WorldSnapshot,b.Finish().Union());
}
int main(){
    for(int bad=0;bad<3;++bad){auto bytes=world(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(bad==0));}
    MessageBuilder wire(1,1);auto bytes=wire.build_cancel_liquid_transfer(9,42);
    auto* cancel=GetCwmMessage(bytes.data())->payload_as_CancelLiquidTransferRequest();CHECK(cancel && cancel->command_id()==9 && cancel->activity_token()==42);
    bytes=wire.build_item_transfer(10,11,12,0,0,ItemTransferAction::POUR);auto* r=GetCwmMessage(bytes.data())->payload_as_ItemTransferRequest();
    CHECK(r && r->action()==ItemTransferAction::POUR && r->quantity()==0 && !r->destination_id());
    std::cout<<"Liquid work identity, no fabricated progress, typed cancellation and native pouring request PASS\n";
}

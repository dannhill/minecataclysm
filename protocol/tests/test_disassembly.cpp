#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;
using namespace cdda::cwm;
#define CHECK(x) do {if(!(x))throw std::runtime_error(#x);}while(false)
std::vector<uint8_t> world(int bad) {
    MessageBuilder wire(1,1,{11,22,33});auto& f=wire.builder();
    const auto work=CreateDisassemblyStateDirect(f,bad==1?0:42,bad==2?-1:bad==3?10000001:1234,
        bad==4?"":bad==5?nullptr:"Disassembly");
    const auto other=bad==6?CreateCraftingState(f,43,0):flatbuffers::Offset<CraftingState>{};
    Vec3f pos(0,0,0);Coord3i origin(0,0,0);
    std::vector<flatbuffers::Offset<EntityState>> entities{CreateEntityState(f,1,EntityType::PLAYER,0,&pos)};
    std::vector<flatbuffers::Offset<VehicleState>> vehicles;
    std::vector<flatbuffers::Offset<FieldState>> fields;
    const auto e=f.CreateVector(entities);const auto v=f.CreateVector(vehicles);const auto s=f.CreateVector(fields);
    WorldSnapshotBuilder snap(f);snap.add_state_id(1);snap.add_origin(&origin);snap.add_entities(e);
    snap.add_vehicles(v);snap.add_fields(s);snap.add_disassembly(work);snap.add_crafting(other);
    return wire.finish_message(Payload::WorldSnapshot,snap.Finish().Union());
}
std::vector<uint8_t> inventory(int bad) {
    MessageBuilder wire(1,1,{11,22,33});auto& f=wire.builder();
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons;
    for(int n=0;n<(bad==1?7:8);++n) reasons.push_back(f.CreateString(n==7?"":"unavailable"));
    const auto info=bad==2 ? flatbuffers::Offset<DisassemblyInfo>{} :
        CreateDisassemblyInfo(f,bad==3?-1:9000,bad==4?-1:bad==5?10000001:bad==6?1:0,false);
    const auto entry=CreateInventoryEntryDirect(f,1,0,-1,"footrags_faux_fur","Foot wraps","clothing",0,false,false,false,
        100,100,100,0,128,&reasons,0,"","","",false,0,false,0,false,{},info);
    std::vector<flatbuffers::Offset<InventoryEntry>> entries{entry};
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets;
    const auto view=CreateInventoryViewDirect(f,1,1,&entries,&pockets,false,"");
    return wire.finish_message(Payload::InventoryView,view.Union());
}
int main() {
    for(int bad=0;bad<7;++bad) {
        auto bytes=world(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(bad==0));
    }
    for(int bad=0;bad<7;++bad) {
        auto bytes=inventory(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_inventory(GetCwmMessage(bytes.data())->payload_as_InventoryView())==(bad==0));
    }
    MessageBuilder wire(1,1,{11,22,33});
    auto bytes=wire.build_equipment_request(1,2,3,EquipmentAction::DISASSEMBLE);
    CHECK(GetCwmMessage(bytes.data())->payload_as_EquipmentRequest()->action()==EquipmentAction::DISASSEMBLE);
    bytes=wire.build_cancel_disassembly(2,42);
    const auto* cancel=GetCwmMessage(bytes.data())->payload_as_CancelDisassemblyRequest();
    CHECK(cancel && cancel->command_id()==2 && cancel->activity_token()==42);
    std::cout<<"Native disassembly bounds, exclusivity and typed requests PASS\n";
}

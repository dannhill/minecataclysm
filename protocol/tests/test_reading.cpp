#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;
using namespace cdda::cwm;
#define CHECK(x) do {if(!(x))throw std::runtime_error(#x);}while(false)
std::vector<uint8_t> reading_world(int bad) {
    MessageBuilder wire(1,1,{11,22,33});auto& f=wire.builder();
    std::string name=bad==5 ? "" : bad==7 ? std::string(16385,'x') : "Book";
    if(bad==8)name=std::string("Bo\0ok",5);
    const auto title=f.CreateString(name),progress=bad==6 ? flatbuffers::Offset<flatbuffers::String>{} : f.CreateString("");
    const auto reading=CreateReadingState(f,bad==1?0:42,bad==2?0:100,bad==3?-1:bad==4?101:50,title,progress,true);
    const auto other=bad==9 ? CreateConsumptionState(f,43,100,50) : flatbuffers::Offset<ConsumptionState>{};
    Vec3f pos(0,0,0);
    std::vector<flatbuffers::Offset<EntityState>> entities{CreateEntityState(f,1,EntityType::PLAYER,0,&pos)};
    std::vector<flatbuffers::Offset<VehicleState>> vehicles;
    std::vector<flatbuffers::Offset<FieldState>> fields;
    const auto e=f.CreateVector(entities);const auto v=f.CreateVector(vehicles);const auto s=f.CreateVector(fields);
    Coord3i origin(0,0,0);
    WorldSnapshotBuilder world(f);world.add_state_id(1);world.add_origin(&origin);world.add_entities(e);
    world.add_vehicles(v);world.add_fields(s);world.add_reading(reading);world.add_consumption(other);
    return wire.finish_message(Payload::WorldSnapshot,world.Finish().Union());
}
std::vector<uint8_t> book_inventory(int bad) {
    MessageBuilder wire(1,1,{11,22,33});auto& f=wire.builder();
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons;
    for(int n=0;n<(bad==1?7:8);++n)reasons.push_back(f.CreateString(n==6?"":"unavailable"));
    const auto book=bad==2 ? flatbuffers::Offset<BookInfo>{} :
        CreateBookInfoDirect(f,false,bad==3?-1:bad==4?0:100,bad==5?"":"Skim first");
    const auto entry=CreateInventoryEntryDirect(f,1,0,-1,"book","Book","books",0,false,false,false,1,1,1,0,64,&reasons,0,"","","",false,0,false,0,false,book);
    std::vector<flatbuffers::Offset<InventoryEntry>> rows{entry};
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets;
    const auto view=CreateInventoryViewDirect(f,1,1,&rows,&pockets,false,"");
    return wire.finish_message(Payload::InventoryView,view.Union());
}
int main() {
    for(int bad=0;bad<10;++bad) {
        const auto bytes=reading_world(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(bad==0));
    }
    for(int bad=0;bad<6;++bad) {
        const auto bytes=book_inventory(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_inventory(GetCwmMessage(bytes.data())->payload_as_InventoryView())==(bad==0));
    }
    MessageBuilder wire(1,1,{11,22,33});
    auto bytes=wire.build_equipment_request(1,2,3,EquipmentAction::READ);
    CHECK(GetCwmMessage(bytes.data())->payload_as_EquipmentRequest()->action()==EquipmentAction::READ);
    bytes=wire.build_cancel_reading(2,42);
    const auto* cancel=GetCwmMessage(bytes.data())->payload_as_CancelReadingRequest();
    CHECK(cancel && cancel->command_id()==2 && cancel->activity_token()==42);
    std::cout<<"Reading bounds, exclusivity, book knowledge and typed requests PASS\n";
}

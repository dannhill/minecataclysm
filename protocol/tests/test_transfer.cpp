#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> snapshot(int defect) {
    MessageBuilder wire(1,7,{11,22,33});auto& f=wire.builder();
    auto transfer=CreateItemTransferState(f,defect==1?0:12,defect==2?-1:defect==6?0:1000,defect==3?-1:defect==4?1001:0,defect!=7);
    auto meal=defect==5?CreateConsumptionState(f,14,1000,800):flatbuffers::Offset<ConsumptionState>{};
    Coord3i origin(0,0,0);Vec3f pos(0,0,0);
    auto player=CreateEntityState(f,1,EntityType::PLAYER,0,&pos);
    auto entities=f.CreateVector(std::vector<flatbuffers::Offset<EntityState>>{player});
    auto vehicles=f.CreateVector(std::vector<flatbuffers::Offset<VehicleState>>{});
    auto fields=f.CreateVector(std::vector<flatbuffers::Offset<FieldState>>{});
    WorldSnapshotBuilder world(f);world.add_world_revision(2);world.add_origin(&origin);world.add_state_id(1);
    world.add_entities(entities);world.add_vehicles(vehicles);world.add_fields(fields);world.add_item_transfer(transfer);world.add_consumption(meal);
    return wire.finish_message(Payload::WorldSnapshot,world.Finish().Union());
}
std::vector<uint8_t> external_view(int defect) {
    MessageBuilder wire(1,7,{11,22,33});auto& f=wire.builder();
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons(7,f.CreateString("not owned"));
    std::vector<flatbuffers::Offset<InventoryEntry>> entries;
    entries.push_back(CreateInventoryEntryDirect(f,1,0,-1,"rock","rock","tools",0,false,
        defect==3,false,100,100,100,0,0,&reasons,0,"","","",false,defect==4?1:0,false,0,defect!=1));
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets;
    Coord3i coord(100,100,defect==6?1025:0);
    const auto view=CreateInventoryViewDirect(f,1,1,&entries,&pockets,false,"",100,1000,100,1000,
        defect==2?nullptr:&coord,defect==5?"":"locker",500,defect==7?501:400);
    return wire.finish_message(Payload::InventoryView,view.Union());
}
int main(){
    static_assert(int(Payload::CancelReloadRequest)==38);
    static_assert(int(Payload::ItemTransferRequest)==39);
    for(int i=0;i<8;++i){auto bytes=snapshot(i);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(i==0||i==7));}
    MessageBuilder wire(2,7,{11,22,33});auto bytes=wire.build_item_transfer(19,12,3,7,4,ItemTransferAction::INSERT);
    const auto* r=GetCwmMessage(bytes.data())->payload_as_ItemTransferRequest();CHECK(r&&r->command_id()==19&&r->view_id()==12&&r->item_id()==3&&r->quantity()==7&&r->destination_id()==4&&r->action()==ItemTransferAction::INSERT);
    bytes=wire.build_cancel_item_transfer(20,13);CHECK(GetCwmMessage(bytes.data())->payload_as_CancelItemTransferRequest()->activity_token()==13);
    for(auto action : {ItemTransferAction::TAKE_EXTERNAL,ItemTransferAction::DEPOSIT_EXTERNAL}) {
        bytes=wire.build_item_transfer(21,12,3,7,0,action);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(GetCwmMessage(bytes.data())->payload_as_ItemTransferRequest()->action()==action);
    }
    Coord3i external(10001,-20002,1);bytes=wire.build_inventory_query(22,&external);
    const auto* query=GetCwmMessage(bytes.data())->payload_as_InventoryQueryRequest();CHECK(query&&query->query_id()==22&&query->external_coord()->x()==10001&&query->external_coord()->y()==-20002);
    for(int defect=0;defect<8;++defect) {
        bytes=external_view(defect);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_inventory(GetCwmMessage(bytes.data())->payload_as_InventoryView())==(defect==0||defect==1));
    }
    std::cout<<"Transfer bounds, exclusive native activities, stable union IDs and quantities PASS\n";
}

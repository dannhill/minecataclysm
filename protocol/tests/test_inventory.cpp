#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> inventory(int defect) {
    MessageBuilder wire(1,7,{11,22,33}); auto& f = wire.builder();
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons;
    for (int i=0;i<5;++i) reasons.push_back(f.CreateString(i==0?"":"not available"));
    auto owner = CreateInventoryEntryDirect(f,1,0,-1,"backpack_hiking","pack","containers",0,false,true,false,500,3000,600,250,1,&reasons,0,"","");
    auto child = CreateInventoryEntryDirect(f,defect==1?1:2,defect==2?2:1,defect==3?9:0,
        "rock","stone","misc",0,false,false,false,100,100,10,100,defect==4?0:1,&reasons,0,"","");
    auto pocket = CreateInventoryPocketDirect(f,1,0,"main",4000,defect==5?-100:3800,5000,4800,1000,100,false,false,false);
    std::vector<flatbuffers::Offset<InventoryEntry>> entries{owner,child};
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets{pocket};
    if (defect==6) pockets.push_back(pocket);
    auto view = CreateInventoryViewDirect(f,3,defect==7?0:8,&entries,&pockets,false,defect==8?"error":"",600,40000,100,4000);
    return wire.finish_message(Payload::InventoryView,view.Union());
}
int main() {
    for (int defect=0;defect<=8;++defect) {
        const auto bytes=inventory(defect);
        CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_inventory(GetCwmMessage(bytes.data())->payload_as_InventoryView()) == (defect==0 || defect==5));
    }
    for (int defect=0;defect<5;++defect) {
        auto bytes=inventory(0);
        auto* source=static_cast<InventoryView*>(GetMutableCwmMessage(bytes.data())->mutable_payload());
        auto* entry=source->mutable_entries()->GetMutableObject(0);
        if (defect==1) entry->mutate_consume_moves(-1);
        if (defect==2) entry->mutate_actions(128);
        if (defect==3) entry->mutate_actions(17);
        if (defect==4) entry->mutable_reasons()->GetMutableObject(4)->Mutate(0,'\0');
        CHECK(valid_inventory(source)==(defect==0));
    }
    MessageBuilder wire(10,7,{11,22,33});
    auto query=wire.build_inventory_query(42);
    CHECK(GetCwmMessage(query.data())->payload_as_InventoryQueryRequest()->query_id()==42);
    auto request=wire.build_equipment_request(99,8,2,EquipmentAction::TAKEOFF);
    const auto* action=GetCwmMessage(request.data())->payload_as_EquipmentRequest();
    CHECK(action && action->command_id()==99 && action->view_id()==8 && action->item_id()==2 && action->action()==EquipmentAction::TAKEOFF);
    auto cancel = wire.build_cancel_consumption(100, 50);
    CHECK(GetCwmMessage(cancel.data())->payload_as_CancelConsumptionRequest()->activity_token() == 50);
    CHECK(GetCwmMessage(cancel.data())->payload_as_CancelConsumptionRequest()->command_id() == 100);
    std::cout << "Inventory bounds, ancestry, pocket links, action masks and request roundtrips PASS\n";
}

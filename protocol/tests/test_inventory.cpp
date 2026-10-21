#include "cwm/cwm_session.hpp"
#include "cwm/product_language.hpp"
#include <stdexcept>
#include <iostream>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> inventory(int defect) {
    MessageBuilder wire(1,7,{11,22,33}); auto& f = wire.builder(); f.ForceDefaults(true);
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons;
    for (int i=0;i<7;++i) reasons.push_back(f.CreateString(i==0?"":"not available"));
    auto owner = CreateInventoryEntryDirect(f,1,0,-1,"backpack_hiking","pack","containers",0,false,true,false,500,3000,600,250,1,&reasons,0,"","","",false);
    auto child = CreateInventoryEntryDirect(f,defect==1?1:2,defect==2?2:1,defect==3?9:0,
        "rock","stone","misc",0,false,false,false,100,100,10,100,defect==4?0:1,&reasons,0,"","","",false);
    auto pocket = CreateInventoryPocketDirect(f,1,0,"main",4000,defect==5?-100:3800,5000,4800,1000,100,false,false,false);
    std::vector<flatbuffers::Offset<InventoryEntry>> entries{owner,child};
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets{pocket};
    if (defect==6) pockets.push_back(pocket);
    auto view = CreateInventoryViewDirect(f,3,defect==7?0:8,&entries,&pockets,false,defect==8?"error":"",600,40000,100,4000);
    return wire.finish_message(Payload::InventoryView,view.Union());
}
int main() {
    // Presentation language cannot alter semantic commands or wire identifiers.
    CHECK(::cwm::set_product_language("en"));
    MessageBuilder english_wire(10,7,{11,22,33});
    auto english = english_wire.build_equipment_request(99,8,2,EquipmentAction::TAKEOFF);
    CHECK(::cwm::set_product_language("it"));
    CHECK(::cwm::wide("Quantity", "Quantità") == L"Quantità");
    const auto supplementary = ::cwm::wide("🌍");
    CHECK(supplementary.size() == (sizeof(wchar_t) == 2 ? 2 : 1));
    if (sizeof(wchar_t) == 2) { CHECK(supplementary[0] == 0xd83c && supplementary[1] == 0xdf0d); }
    else CHECK(supplementary[0] == 0x1f30d);
    const auto bytes = [](std::initializer_list<unsigned> values) {
        std::string out; for (const auto value : values) out += static_cast<char>(value); return out;
    };
    for (const auto &bad : {bytes({0xc0,0x80}), bytes({0xed,0xa0,0x80}), bytes({0xf4,0x90,0x80,0x80}), bytes({0xe2,0x82}), bytes({0x80})}) {
        bool rejected = false;
        try { ::cwm::wide(bad.c_str()); } catch (const std::range_error &) { rejected = true; }
        CHECK(rejected);
    }
    CHECK(::cwm::text("Fallback") == "Fallback");
    CHECK(::cwm::text("Fallback", "") == "Fallback");
    CHECK(!::cwm::set_product_language("fr"));
    CHECK(::cwm::text("Quantity", "Quantità") == "Quantità");
    MessageBuilder italian_wire(10,7,{11,22,33});
    auto italian = italian_wire.build_equipment_request(99,8,2,EquipmentAction::TAKEOFF);
    // Time legitimately advances while Unicode validation runs. Compare the
    // command bytes after normalizing only the envelope's monotonic timestamp.
    CHECK(MessageVerifier::verify(english.data(), english.size()));
    CHECK(MessageVerifier::verify(italian.data(), italian.size()));
    CHECK(GetMutableCwmMessage(english.data())->mutate_timestamp_ms(1));
    CHECK(GetMutableCwmMessage(italian.data())->mutate_timestamp_ms(1));
    CHECK(italian == english);
    CHECK(::cwm::set_product_language("en"));
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
    auto aid = wire.build_cancel_first_aid(101, 51);
    CHECK(GetCwmMessage(aid.data())->payload_as_CancelFirstAidRequest()->activity_token() == 51);
    auto treat = wire.build_equipment_request(102,8,2,EquipmentAction::TREAT);
    CHECK(GetCwmMessage(treat.data())->payload_as_EquipmentRequest()->action()==EquipmentAction::TREAT);
    std::cout << "Inventory bounds, ancestry, pocket links, action masks and request roundtrips PASS\n";
}

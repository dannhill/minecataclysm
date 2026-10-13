#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> catalog(int defect) {
    MessageBuilder wire(1,7,{11,22,33}); auto& f=wire.builder();f.ForceDefaults(true);
    const auto entry=CreateCraftingEntryDirect(f,1,"bandages_makeshift","bandages_makeshift","bandage",
        "cotton sheet","",1600,defect==5,defect==4?-1:defect==5?10000001:0);
    std::vector<flatbuffers::Offset<CraftingEntry>> entries{entry};
    const auto view=CreateCraftingViewDirect(f,defect==1?0:3,defect==2?0:8,defect==3?21:1,&entries,false,defect==6?"error":"");
    return wire.finish_message(Payload::CraftingView,view.Union());
}
int main() {
    for(int defect=0;defect<=6;++defect) {
        const auto bytes=catalog(defect);
        CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
        CHECK(valid_crafting(GetCwmMessage(bytes.data())->payload_as_CraftingView())==(defect==0));
    }
    auto bytes=catalog(0);auto* view=static_cast<CraftingView*>(GetMutableCwmMessage(bytes.data())->mutable_payload());
    CHECK(view->mutable_entries()->GetMutableObject(0)->mutate_id(2)); CHECK(!valid_crafting(view));
    bytes=catalog(0);view=static_cast<CraftingView*>(GetMutableCwmMessage(bytes.data())->mutable_payload());
    view->mutable_entries()->GetMutableObject(0)->mutable_recipe_id()->Mutate(0,'\0');CHECK(!valid_crafting(view));
    MessageBuilder nulls(1,7,{11,22,33}); auto& nf=nulls.builder();
    std::vector<flatbuffers::Offset<CraftingEntry>> empty;
    auto omitted=CreateCraftingView(nf,1,2,1,nf.CreateVector(empty));
    auto omitted_bytes=nulls.finish_message(Payload::CraftingView,omitted.Union());
    CHECK(MessageVerifier::verify(omitted_bytes.data(),omitted_bytes.size()));
    CHECK(!valid_crafting(GetCwmMessage(omitted_bytes.data())->payload_as_CraftingView())); // Required semantic empty strings must be present.
    MessageBuilder wire(10,7,{11,22,33});
    auto query=wire.build_crafting_query(42,"bandage",2);
    const auto* q=GetCwmMessage(query.data())->payload_as_CraftingQueryRequest();CHECK(q->query_id()==42&&q->batch()==2&&q->search()->str()=="bandage");
    auto request=wire.build_crafting_request(99,8,2);const auto* r=GetCwmMessage(request.data())->payload_as_CraftingRequest();CHECK(r->command_id()==99&&r->view_id()==8&&r->entry_id()==2);
    auto cancel=wire.build_cancel_crafting(100,50);CHECK(GetCwmMessage(cancel.data())->payload_as_CancelCraftingRequest()->activity_token()==50);
    MessageBuilder favorite_wire(12,7,{11,22,33});auto star=favorite_wire.build_crafting_favorite(105,8,1,true,false);
    const auto* favorite=GetCwmMessage(star.data())->payload_as_CraftingFavoriteRequest();
    CHECK(favorite->command_id()==105 && favorite->view_id()==8 && favorite->entry_id()==1 && favorite->favorite() && !favorite->expected_favorite());
    for(int defect=0;defect<5;++defect) {
        MessageBuilder wire(1,1);auto& f=wire.builder();
        auto entry=CreateCraftingEntryDirect(f,1,"bandages_makeshift","bandages_makeshift","Bandage","","",1,false,0,defect!=1,defect==2?21:1);
        std::vector<flatbuffers::Offset<CraftingEntry>> list{entry};
        auto view=CreateCraftingViewDirect(f,1,1,1,&list,false,"",defect==3?static_cast<CraftingFilter>(3):defect==4?CraftingFilter::RECENT:CraftingFilter::FAVORITES);
        auto data=wire.finish_message(Payload::CraftingView,view.Union());
        CHECK(valid_crafting(GetCwmMessage(data.data())->payload_as_CraftingView())==(defect==0 || defect==4));
    }
    std::cout<<"Crafting catalog limits, invalid handles/text and request roundtrips PASS\n";
}

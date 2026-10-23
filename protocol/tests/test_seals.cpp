#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
std::vector<uint8_t> inventory(int bad) {
    MessageBuilder wire(1,1);auto& f=wire.builder();
    const std::string reason=bad==3?std::string(2049,'x'):"";
    const auto seal=CreateSealInfoDirect(f,reason.c_str());
    std::vector<flatbuffers::Offset<flatbuffers::String>> reasons;
    for(int n=0;n<8;++n)reasons.push_back(f.CreateString("Unavailable"));
    auto e=CreateInventoryEntryDirect(f,1,0,-1,"bottle_plastic","Bottle","container",0,false,false,false,10,500,180,0,0,&reasons,0,"","","",bad!=2,0,false,0,bad==1,{}, {}, {},seal);
    std::vector<flatbuffers::Offset<InventoryEntry>> entries{e};
    std::vector<flatbuffers::Offset<InventoryPocket>> pockets;
    auto v=CreateInventoryViewDirect(f,1,1,&entries,&pockets,false,"",0,1000,0,1000);
    return wire.finish_message(Payload::InventoryView,v.Union());
}
int main(){
    for(int bad=0;bad<4;++bad){const auto bytes=inventory(bad);CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));CHECK(valid_inventory(GetCwmMessage(bytes.data())->payload_as_InventoryView())==(bad==0));}
    MessageBuilder wire(1,1);auto bytes=wire.build_item_transfer(9,10,11,0,0,ItemTransferAction::OPEN_SEAL);
    CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));
    auto* r=GetCwmMessage(bytes.data())->payload_as_ItemTransferRequest();
    CHECK(r && r->action()==ItemTransferAction::OPEN_SEAL && r->command_id()==9 && r->view_id()==10 && r->item_id()==11 && !r->quantity() && !r->destination_id());
    std::cout<<"Seal request identity and no preselected quantity/destination PASS\n";
}

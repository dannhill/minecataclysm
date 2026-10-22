#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;
using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main() {
    for(int bad=0;bad<17;++bad) {
        MessageBuilder wire(1,1);auto& f=wire.builder();
        auto row=CreateTradeEntry(f,1,true,bad==1?1:0,f.CreateString(bad==2?"":"9mm"),
            f.CreateString(bad==3?std::string("a\0b",3):"Native item"),f.CreateString("ammo"),f.CreateString("backpack"),
            bad==4?0:10,bad==5?11:bad==6?-1:3,bad==7?-1:100,f.CreateString(""));
        std::vector<flatbuffers::Offset<TradeEntry>> rows{row};
        if(bad==8)rows.push_back(row);
        if(bad==9)rows[0]=CreateTradeEntry(f,2,true,0,f.CreateString("9mm"),f.CreateString("ammo"),f.CreateString("ammo"),f.CreateString("bag"),1,0,10,f.CreateString(""));
        if(bad==10 || bad==11) {
            rows[0]=CreateTradeEntry(f,1,true,2,f.CreateString("9mm"),f.CreateString("ammo"),f.CreateString("ammo"),f.CreateString("bag"),1,0,10,f.CreateString(""));
            rows.push_back(CreateTradeEntry(f,2,bad!=10,bad==11?1:0,f.CreateString("backpack"),f.CreateString("bag"),f.CreateString("container"),f.CreateString("worn"),1,0,10,f.CreateString("")));
        }
        auto view=CreateTradeView(f,bad==12?0:1,bad==13?0:2,1,bad==14?1:((uint64_t(1)<<63)|9),
            f.CreateString("NPC"),f.CreateString("Trade"),f.CreateVector(rows),bad==15?int64_t(INT32_MAX)+1:0,300,700,700,bad==16?-1:10000,0,false,true,f.CreateString(""));
        auto bytes=wire.finish_message(Payload::TradeView,view.Union());
        CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));CHECK(valid_trade(GetCwmMessage(bytes.data())->payload_as_TradeView())==(bad==0));
    }
    MessageBuilder wire(1,1);
    auto bytes=wire.build_trade_offer(6,7,8,9,3);auto offer=GetCwmMessage(bytes.data())->payload_as_TradeOfferRequest();
    CHECK(offer && offer->request_id()==6 && offer->trade_id()==7 && offer->quote_id()==8 && offer->entry_id()==9 && offer->quantity()==3);
    bytes=wire.build_trade_commit(10,7,8);auto commit=GetCwmMessage(bytes.data())->payload_as_TradeCommitRequest();CHECK(commit && commit->command_id()==10 && commit->trade_id()==7 && commit->quote_id()==8);
    bytes=wire.build_trade_cancel(7);CHECK(GetCwmMessage(bytes.data())->payload_as_TradeCancelRequest()->trade_id()==7);
    std::cout<<"Native trade bounds, graph identity and separate offer/commit/cancel PASS\n";
}

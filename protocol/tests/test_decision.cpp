#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;
using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
    for(int bad=0;bad<8;++bad){
        MessageBuilder wire(1,1);auto& f=wire.builder();std::vector<std::string> choices{"Yes","No"};
        if(bad==1)choices.clear();if(bad==2)choices.resize(10,"choice");if(bad==3)choices[0]="";if(bad==4)choices[0]=std::string("a\0b",3);
        auto text=f.CreateString(bad==5?std::string(16385,'x'):"<color_c_red>Risk</color>");
        const int cancel=bad==6?2:bad==7?-2:1;
        auto v=CreateDecisionPrompt(f,8,text,f.CreateVectorOfStrings(choices),cancel);
        auto bytes=wire.finish_message(Payload::DecisionPrompt,v.Union());
        CHECK(MessageVerifier::verify(bytes.data(),bytes.size()));CHECK(valid_decision(GetCwmMessage(bytes.data())->payload_as_DecisionPrompt())==(bad==0));
    }
    MessageBuilder wire(1,1);auto& f=wire.builder();std::vector<std::string> labels{"Proceed","Stop"};
    auto v=CreateDecisionPrompt(f,4,f.CreateString("Safe fallback unavailable"),f.CreateVectorOfStrings(labels),-1);auto bytes=wire.finish_message(Payload::DecisionPrompt,v.Union());
    CHECK(valid_decision(GetCwmMessage(bytes.data())->payload_as_DecisionPrompt()));
    std::cout<<"Decision identity, label bounds, cancellation metadata and no inferred cancellation PASS\n";
}

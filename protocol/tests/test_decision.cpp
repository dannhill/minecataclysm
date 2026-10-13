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
    for(int bad=0;bad<10;++bad) {
        MessageBuilder typed(1,1);auto& f=typed.builder();
        const auto part=CreateMedicalOption(f,bad==1?1:bad==2?3:0,f.CreateString(bad==3?"":"arm_l"),f.CreateString("Left arm"),f.CreateString("Native treatment description"),bad==4?21:8,f.CreateString(""),bad==5?5:-1,bad==6?10:-1);
        std::vector<flatbuffers::Offset<MedicalOption>> parts{part};if(bad==7)parts.push_back(part);
        if(bad==8)parts[0]=CreateMedicalOption(f,0,f.CreateString("arm_l"),f.CreateString("Left arm"),f.CreateString(""),-1,f.CreateString(""),5,10);
        if(bad==9)parts[0]=CreateMedicalOption(f,-1,f.CreateString("arm_l"),f.CreateString("Left arm"),f.CreateString("No expected effect"),-1,f.CreateString("Unknown"));
        auto v=CreateDecisionPrompt(f,99,f.CreateString("Choose a part"),f.CreateVectorOfStrings(labels),1,f.CreateVector(parts));
        auto data=typed.finish_message(Payload::DecisionPrompt,v.Union());
        CHECK(valid_decision(GetCwmMessage(data.data())->payload_as_DecisionPrompt())==(bad==0 || bad==9));
    }
    std::cout<<"Decision identity, label bounds, cancellation metadata and no inferred cancellation PASS\n";
}

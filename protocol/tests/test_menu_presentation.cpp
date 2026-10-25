#include "cwm/cwm_protocol.hpp"
#include "../../luanti/src/cdda/decision_text.h"
#include "../../luanti/src/cdda/presentation_theme.h"
#include "../../luanti/src/cdda/decision_model.h"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;using namespace cdda::cwm;using namespace cdda_client;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
 CHECK(decisionChoiceText("Yes.\n")=="Yes");CHECK(decisionChoiceText("Yes.")=="Yes");CHECK(decisionChoiceText("<color_c_red>No.</color>")=="No");
 CHECK(decisionChoiceText("Cancel...")=="Cancel...");CHECK(decisionChoiceText("Really?")=="Really?");
 CHECK(decisionChoiceText("Version 2.0")=="Version 2.0");CHECK(decisionChoiceText("Città.")=="Città");
 CHECK(decisionTrimFullStop("<color_c_red>Stop.</color>")=="<color_c_red>Stop</color>");
 MessageBuilder b(1,1);auto& f=b.builder();std::vector<flatbuffers::Offset<flatbuffers::String>> labels{f.CreateString("Yes."),f.CreateString("No.")};
 auto prompt=CreateDecisionPromptDirect(f,77,"Continue?",&labels,1);
 auto data=b.finish_message(Payload::DecisionPrompt,prompt.Union());auto* wire=GetCwmMessage(data.data())->payload_as_DecisionPrompt();
 DecisionModel model;model.read(*wire,42);CHECK(model.choices[0]=="Yes.");CHECK(model.permits(77,42,0));CHECK(!model.permits(77,43,0));
 model.submitted=true;CHECK(!model.permits(77,42,0));CHECK(wire->choices()->Get(0)->str()=="Yes.");
 CHECK(presentationPanel(16,11).find("size[16,11]")!=std::string::npos);
 std::cout<<"Presentation formatting retains semantic labels, identities, Unicode and explicit input fencing PASS\n";
}

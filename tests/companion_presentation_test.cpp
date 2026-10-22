#include "cdda/decision_dialog.h"
#include <iostream>
#include <stdexcept>
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main() {
    cdda_client::DecisionDialog d;d.id=4;d.connection=5;d.npc=(uint64_t(1)<<63)|6;
    d.companion_controls=true;d.speaker="Known ally";d.body="Base: On\nOverride: Off <action name=evil>";
    d.choices={"Enable base rule","Back","Leave conversation"};d.cancel=2;
    const auto form=d.form();CHECK(form.find("companion_profile;")!=std::string::npos);
    CHECK(form.find("conversation_history;")==std::string::npos);
    CHECK(form.find("choice_0;")!=std::string::npos && form.find("choice_2;")==std::string::npos);
    CHECK(form.find("\\<action")!=std::string::npos);CHECK(d.permits(4,5,0));CHECK(!d.permits(3,5,0));
    d.submitted=true;CHECK(d.form().find("companion_profile;")==std::string::npos);CHECK(!d.permits(4,5,0));
    d.submitted=false;d.companion_controls=false;CHECK(d.form().find("conversation_history;")!=std::string::npos);
    std::cout<<"Native companion panel, safe markup, explicit choices and stale callback fencing PASS\n";
}

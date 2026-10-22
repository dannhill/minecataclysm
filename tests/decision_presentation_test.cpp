#include "cdda/decision_dialog.h"
#include "cdda/decision_input.h"
#include <stdexcept>
#include <iostream>
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
    using namespace cdda_client;
    DecisionInput input;input.observe(49,true);CHECK(input.fresh(49));input.observe(49,true);CHECK(!input.fresh(49));
    input.observe(49,false);CHECK(!input.fresh(49));input.observe(49,true);CHECK(input.fresh(49));
    CHECK(decisionRichText("<color_c_red>Warning</color>")=="<style color=#A53C2C>Warning</style>");
    CHECK(decisionRichText("<action name=unsafe>injection</action>").find("\\<action")!=std::string::npos);
    CHECK(decisionRichText("<color_unknown>x")=="<style>x</style>");
    DecisionDialog view;view.id=18;view.connection=77;view.body="Safe <text>";view.choices={"Accept","Decline"};view.cancel=1;
    CHECK(view.permits(18,77,0));CHECK(!view.permits(17,77,0));CHECK(!view.permits(18,78,0));CHECK(!view.permits(18,77,2));
    CHECK(view.form().find("cancel;Esc: Decline")!=std::string::npos);view.cancel=-1;CHECK(view.form().find("cancel;Esc:")==std::string::npos);
    view.cancel=1;view.medical={{0,8,-1,-1,"arm_l","Left arm","Bandaged: poor -> good",""}, {-1,-1,-1,-1,"leg_l","Left leg","Needs a splint","Broken"}};
    CHECK(view.form().find("medical_scroll")!=std::string::npos);
    CHECK(view.form().find("heart.png")!=std::string::npos);
    CHECK(view.form().find("choice_-1")==std::string::npos);
    CHECK(view.form().find("Broken")!=std::string::npos);
    CHECK(view.form().find("choice_0;1. Left arm")!=std::string::npos);
    view.medical.clear();view.npc=(uint64_t(1)<<63)|12;view.speaker="NPC <unsafe>";
    view.history="The full native conversation history.";view.choices={std::string(300,'x'),"Leave conversation"};
    CHECK(view.form().find("conversation_history")!=std::string::npos);
    CHECK(view.form().find(std::string(300,'x'))!=std::string::npos);
    CHECK(view.form().find("reply_scroll")!=std::string::npos);
    view.submitted=true;CHECK(!view.permits(18,77,0));CHECK(view.form().find("Waiting for the game...")!=std::string::npos);
    std::cout<<"Held-key release, stale prompt/generation, markup safety, explicit cancellation and waiting PASS\n";
}
